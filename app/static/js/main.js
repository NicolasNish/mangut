document.addEventListener('DOMContentLoaded', () => {
    const themeBtn = document.getElementById('theme-toggle');
    const currentTheme = localStorage.getItem('theme');

    // Aplica o tema salvo no localStorage, se existir
    if (currentTheme) {
        document.documentElement.setAttribute('data-theme', currentTheme);
        if (currentTheme === 'dark') {
            themeBtn.textContent = '☀️';
        }
    }

    // Ação ao clicar no botão de alterar tema
    themeBtn.addEventListener('click', () => {
        let theme = document.documentElement.getAttribute('data-theme');

        if (theme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
            themeBtn.textContent = '🌙';
        } else {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
            themeBtn.textContent = '☀️';
        }
    });
});