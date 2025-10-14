// authForms.js - versión Bootstrap 5

document.addEventListener('DOMContentLoaded', function () {
    // Buscar elementos
    const loginTab = document.getElementById('login-tab');
    const registerTab = document.getElementById('register-tab');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    if (!loginTab || !registerTab) return;

    // Inicializar Bootstrap Tabs
    const triggerTab = (tabEl) => {
        const tab = new bootstrap.Tab(tabEl);
        tab.show();
    };

    // Verificar parámetro de URL
    const urlParams = new URLSearchParams(window.location.search);
    const formType = urlParams.get('form');

    if (formType === 'register') {
        triggerTab(registerTab);
    } else {
        triggerTab(loginTab);
    }

    // Actualizar URL al cambiar de pestaña (sin recargar)
    [loginTab, registerTab].forEach(tabEl => {
        tabEl.addEventListener('shown.bs.tab', (event) => {
            const newForm = event.target.id === 'register-tab' ? 'register' : 'login';
            const url = new URL(window.location);
            url.searchParams.set('form', newForm);
            window.history.replaceState({}, '', url);
        });
    });
});
