// static/js/analisis_ia.js

// Función auxiliar para obtener CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


// Manejar botón de análisis IA
document.addEventListener('click', async function(e) {
    if (e.target.classList.contains('btn-analisis-ia')) {
        const btn = e.target;
        const moduleName = btn.getAttribute('data-module-name');

        //debug
        console.log('Iniciando análisis IA para módulo:', moduleName);
        console.log('Datos del módulo:', window.Modulosdata?.[moduleName]);

        // Buscar la card del módulo
        const moduleCard = btn.closest('.bg-light');
        const containerAnalisis = moduleCard.querySelector('.container-analisis-ia');

        //debug
        console.log('Contenedor de análisis IA encontrado:', containerAnalisis);
        console.log('Datos del módulo para análisis:', moduleCard);
        
        // Obtener los datos del módulo
        const moduloData = window.Modulosdata?.[moduleName];
        
        if (!moduloData) {
            alert('No hay datos para analizar');
            return;
        }

        if (!containerAnalisis) {
            alert('No se encontró el contenedor de análisis');
            return;
        }
        
        // Deshabilitar botón y mostrar loading
        btn.disabled = true;
        btn.innerHTML = '⏳ Analizando...';
        
        try {
            const response = await fetch('/analizar-modulo/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    nombre_modulo: moduleName,
                    resultado: moduloData,
                    escaneo_id: window.escaneoId
                })
            });
            
            const data = await response.json();
            console.log('Análisis IA recibido:', data);
            
            // Mostrar resultado
            if (containerAnalisis) {

                // Asegurarse de que el contenedor tenga el HTML correcto
                if (!containerAnalisis.querySelector('.analisis-badge')) {
                    console.warn('⚠️ Recreando estructura del contenedor');
                    containerAnalisis.innerHTML = `
                        <div class="d-flex align-items-start">
                            <span class="badge me-2 mt-1 analisis-badge">Riesgo</span>
                            <p class="mb-0 analisis-texto"></p>
                        </div>
                    `;
                }

                const badge = containerAnalisis.querySelector('.analisis-badge');
                const texto = containerAnalisis.querySelector('.analisis-texto');

                // 👉 AGREGAR DEBUGGING
                console.log('🔍 Elementos encontrados:', {
                    containerAnalisis,
                    badge,
                    texto
                });

                if (!badge || !texto) {
                    console.error('❌ No se encontraron los elementos badge o texto dentro del contenedor');
                    console.log('HTML del contenedor:', containerAnalisis.innerHTML);
                    return;
                }
                
                badge.textContent = `Riesgo ${data.riesgo}`;
                badge.style.backgroundColor = data.color;
                texto.textContent = data.explicacion;
                
                containerAnalisis.classList.remove('d-none');
                containerAnalisis.classList.add('alert-info');
            }
            
            // Restaurar botón
            btn.innerHTML = '✅ Analizado';
            
        } catch (error) {
            console.error('Error al analizar:', error);
            alert('Error al obtener el análisis');
            btn.disabled = false;
            btn.innerHTML = '🤖 Explicación con IA';
        }
    }
});