/**
   * Función genérica para inicializar los gráficos del módulo.
   * @param {Object} datos - JSON de resultados del módulo DNS.
   */
(function() {
    function initGraficosDNS(datos) {
        try {
            // Validar que datos tenga la estructura esperada
            console.log("(desde dns.js) Datos recibidos para gráficos DNS:", datos);

            if (!datos || !datos.records || !datos.meta) {
                console.warn("Módulo aún en proceso, datos incompletos.");
                return; // Evita intentar graficar
            }
            // === 1. Preparar datos para gráfico ===
            const counts = Object.keys(datos.records).map(tipo => ({
            tipo,
            cantidad: Array.isArray(datos.records[tipo]) ? datos.records[tipo].length : 0
            }));

            // Verificar que exista el canvas antes de usar Chart.js
            const chartEl = document.getElementById('dnsChart');
            if (!chartEl) {
            throw new Error("Elemento canvas no encontrado en el DOM.");
            }

            // Crear gráfico de barras
            new Chart(chartEl, {
            type: 'bar',
            data: {
                labels: counts.map(c => c.tipo),
                datasets: [{
                label: 'Cantidad de registros',
                data: counts.map(c => c.cantidad),
                backgroundColor: '#879dacff'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                legend: { display: false },
                title:{display:true, text:'Cantidad de registros DNS por tipo'}
                }
            }
            });

            // === 2. Llenar tabla ===
            const tbody = document.getElementById('dnsTableBody');
            if (!tbody) {
            throw new Error("Elemento tbody no encontrado en el DOM.");
            }

            tbody.innerHTML = ''; // limpiar contenido previo
            Object.keys(datos.records).forEach(tipo => {
            const valores = datos.records[tipo]?.join('<br>') || '—';
            const error = datos.meta.errors?.[tipo] || '—';
            tbody.innerHTML += `
                <tr>
                <td class="border">${tipo}</td>
                <td class="border">${valores}</td>
                <td class="border">${error}</td>
                </tr>
            `;
            });

        } catch (err) {
            // Mostrar error en consola (para debugging)
            console.error("Error al renderizar gráficos DNS:", err);

            // Mostrarlo en la UI
            const container = document.querySelector('.container-errores');
            if (container) {
                container.innerHTML = `<strong class="font-bold">Error:</strong>
            <span class="block sm:inline">⚠️ Error al renderizar datos: ${err.message}</span>`;
                container.classList.remove('hidden');
            }
        }
}
// Registrar en el namespace global
// Hacer esto al final de cada archivo de gráficos
window.Visuals = window.Visuals || {};
window.Visuals["dns"] = initGraficosDNS;
})();