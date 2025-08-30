// authForms.js - Módulo para manejar formularios de autenticación

// Clase principal para gestionar los formularios
class AuthForms {
    constructor() {
        this.loginTab = document.getElementById('login-tab');
        this.registerTab = document.getElementById('register-tab');
        this.loginForm = document.getElementById('login-form');
        this.registerForm = document.getElementById('register-form');
        
        this.init();
    }
    
    init() {
        // Event listeners para los botones
        this.loginTab.addEventListener('click', () => this.showLogin());
        this.registerTab.addEventListener('click', () => this.showRegister());
        
        // Mostrar el formulario correcto según la URL o parámetros
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('form') === 'register') {
            this.showRegister();
        } else {
            this.showLogin();
        }
    }
    
    // Función para cambiar al formulario de login
    showLogin() {
        this.loginForm.classList.remove('hidden');
        this.registerForm.classList.add('hidden');
        this.loginTab.classList.add('text-blue-600', 'border-blue-600');
        this.loginTab.classList.remove('text-gray-500');
        this.registerTab.classList.add('text-gray-500');
        this.registerTab.classList.remove('text-blue-600', 'border-blue-600');
        
        // Actualizar URL sin recargar
        this.updateUrl('login');
    }
    
    // Función para cambiar al formulario de registro
    showRegister() {
        this.loginForm.classList.add('hidden');
        this.registerForm.classList.remove('hidden');
        this.registerTab.classList.add('text-blue-600', 'border-blue-600');
        this.registerTab.classList.remove('text-gray-500');
        this.loginTab.classList.add('text-gray-500');
        this.loginTab.classList.remove('text-blue-600', 'border-blue-600');
        
        // Actualizar URL sin recargar
        this.updateUrl('register');
    }
    
    // Actualizar la URL con el parámetro del formulario activo
    updateUrl(formType) {
        const url = new URL(window.location);
        url.searchParams.set('form', formType);
        window.history.replaceState({}, '', url);
    }
}

// Inicializar cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', function() {
    new AuthForms();
});

// Exportar la clase para poder usarla en otros módulos si es necesario
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthForms;
}