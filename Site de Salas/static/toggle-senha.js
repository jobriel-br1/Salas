// Adiciona um botão "olho" em todos os campos de senha da página,
// permitindo mostrar/ocultar a senha enquanto o usuário digita.
//   - Senha oculta  -> olho aberto (clique para mostrar)
//   - Senha visível -> olho fechado/riscado (clique para ocultar)

const ICONE_OLHO_ABERTO = `
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
     fill="none" stroke="currentColor" stroke-width="2"
     stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
    <circle cx="12" cy="12" r="3"/>
</svg>`;

const ICONE_OLHO_FECHADO = `
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
     fill="none" stroke="currentColor" stroke-width="2"
     stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
    <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
    <path d="M14.12 14.12a3 3 0 1 1-4.24-4.24"/>
    <line x1="1" y1="1" x2="23" y2="23"/>
</svg>`;

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('input[type="password"]').forEach(function (input) {
        // Cria um wrapper em volta do input para posicionar o botão
        const wrapper = document.createElement('div');
        wrapper.className = 'campo-senha';
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);

        // Cria o botão do olho
        const botao = document.createElement('button');
        botao.type = 'button'; // evita enviar o formulário ao clicar
        botao.className = 'botao-olho';
        botao.setAttribute('aria-label', 'Mostrar senha');
        botao.innerHTML = ICONE_OLHO_ABERTO;
        wrapper.appendChild(botao);

        // Alterna entre mostrar e ocultar a senha
        botao.addEventListener('click', function () {
            const visivel = input.type === 'text';
            input.type = visivel ? 'password' : 'text';
            botao.innerHTML = visivel ? ICONE_OLHO_ABERTO : ICONE_OLHO_FECHADO;
            botao.setAttribute('aria-label', visivel ? 'Mostrar senha' : 'Ocultar senha');
        });
    });
});