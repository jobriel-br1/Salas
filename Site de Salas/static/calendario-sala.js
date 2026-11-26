// 1) Alterna entre tema escuro (padrão) e claro, e lembra a escolha do usuário.
// 2) Marca no calendário os dias que já passaram e o dia de hoje.
//
// IMPORTANTE: carregue este arquivo no <head>, SEM "defer".
// Assim o tema salvo é aplicado antes da página aparecer (sem "piscar" de cor).

(function () {
    const CHAVE = 'tema';

    const ICONE_SOL = `
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
     fill="none" stroke="currentColor" stroke-width="2"
     stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <circle cx="12" cy="12" r="4"/>
    <line x1="12" y1="2" x2="12" y2="5"/>
    <line x1="12" y1="19" x2="12" y2="22"/>
    <line x1="2" y1="12" x2="5" y2="12"/>
    <line x1="19" y1="12" x2="22" y2="12"/>
    <line x1="4.9" y1="4.9" x2="7" y2="7"/>
    <line x1="17" y1="17" x2="19.1" y2="19.1"/>
    <line x1="4.9" y1="19.1" x2="7" y2="17"/>
    <line x1="17" y1="7" x2="19.1" y2="4.9"/>
</svg>`;

    const ICONE_LUA = `
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
     fill="none" stroke="currentColor" stroke-width="2"
     stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>
</svg>`;

    function lerTemaSalvo() {
        try {
            return localStorage.getItem(CHAVE);
        } catch (e) {
            return null; // localStorage indisponível (modo privado, etc.)
        }
    }

    function salvarTema(tema) {
        try {
            localStorage.setItem(CHAVE, tema);
        } catch (e) {
            // sem problema: o tema só não será lembrado na próxima visita
        }
    }

    function aplicarTema(tema) {
        document.documentElement.setAttribute('data-theme', tema);
    }

    // Aplica o tema imediatamente (padrão: escuro)
    let temaAtual = lerTemaSalvo() === 'light' ? 'light' : 'dark';
    aplicarTema(temaAtual);

    // Marca as colunas dos dias passados e do dia de hoje.
    // Cada <th> de dia tem o atributo data-data="AAAA-MM-DD".
    function marcarDiasPassados() {
        const tabela = document.querySelector('table');
        if (!tabela) return;

        const hoje = new Date();
        hoje.setHours(0, 0, 0, 0);

        const cabecalhos = tabela.querySelectorAll('thead th');
        const linhas = tabela.querySelectorAll('tbody tr');

        cabecalhos.forEach(function (th, indice) {
            if (!th.dataset.data) return; // pula a coluna "Horário"

            const partes = th.dataset.data.split('-').map(Number);
            const data = new Date(partes[0], partes[1] - 1, partes[2]);

            let classe = '';
            if (data < hoje) {
                classe = 'passado';
            } else if (data.getTime() === hoje.getTime()) {
                classe = 'hoje';
            }
            if (!classe) return;

            th.classList.add(classe);

            linhas.forEach(function (linha) {
                const celula = linha.children[indice];
                if (!celula) return;

                celula.classList.add(classe);

                // Células vagas de dias passados viram "Indisponível"
                if (classe === 'passado' && celula.classList.contains('vago')) {
                    const titulo = celula.querySelector('.estado-titulo');
                    const detalhe = celula.querySelector('.detalhe');
                    if (titulo) titulo.textContent = 'Indisponível';
                    if (detalhe) detalhe.textContent = 'Data passada';
                }
            });
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        marcarDiasPassados();

        const botao = document.getElementById('botao-tema');
        if (!botao) return;

        // No tema escuro mostra o sol (clique para clarear);
        // no tema claro mostra a lua (clique para escurecer).
        function atualizarBotao() {
            const escuro = temaAtual === 'dark';
            botao.innerHTML = escuro ? ICONE_SOL : ICONE_LUA;
            botao.setAttribute(
                'aria-label',
                escuro ? 'Ativar tema claro' : 'Ativar tema escuro'
            );
            botao.setAttribute('title', escuro ? 'Tema claro' : 'Tema escuro');
        }

        atualizarBotao();

        botao.addEventListener('click', function () {
            temaAtual = temaAtual === 'dark' ? 'light' : 'dark';
            aplicarTema(temaAtual);
            salvarTema(temaAtual);
            atualizarBotao();
        });
    });
})();