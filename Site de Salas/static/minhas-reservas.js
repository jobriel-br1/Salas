// Alterna entre tema escuro (padrão) e claro, e lembra a escolha do usuário.
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

    document.addEventListener('DOMContentLoaded', function () {
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