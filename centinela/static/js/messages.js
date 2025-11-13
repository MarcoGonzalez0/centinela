// Auto-ocultar solo mensajes de Django (no afecta alertas dinámicas)
setTimeout(() => {
    const messages = document.querySelectorAll('.alert:not(#alertBox)');
    messages.forEach(msg => {
        msg.style.transition = 'opacity 0.5s';
        msg.style.opacity = 0;
        setTimeout(() => msg.remove(), 500);
    });
}, 5000);