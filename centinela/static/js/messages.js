// Espera 4 segundos y luego oculta todos los mensajes
setTimeout(() => {
    const messages = document.querySelectorAll('.alert');
    messages.forEach(msg => {
        msg.style.transition = 'opacity 0.5s';
        msg.style.opacity = 0;
        setTimeout(() => msg.remove(), 500); // eliminar del DOM
    });
}, 4000); // 4000 ms = 4 segundos