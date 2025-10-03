/**
   * Función genérica para inicializar los gráficos del módulo.
   * @param {Object} datos - JSON de resultados del módulo DNS.
   */
(function() {
    function initGraficosDNS(datos) {
    try {
        // Validar que datos tenga la estructura esperada
        if (!datos || !datos.resultados || !datos.meta) {
        throw new Error("Formato inválido en los datos recibidos.");
        }
        // === 1. Preparar datos para gráfico ===
        const counts = Object.keys(datos.resultados).map(tipo => ({
        tipo,
        cantidad: Array.isArray(datos.resultados[tipo]) ? datos.resultados[tipo].length : 0
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
            backgroundColor: '#3498db'
            }]
        },
        options: {
            responsive: true,
            plugins: {
            legend: { display: false }
            }
        }
        });

        // === 2. Llenar tabla ===
        const tbody = document.getElementById('dnsTableBody');
        if (!tbody) {
        throw new Error("Elemento tbody no encontrado en el DOM.");
        }

        tbody.innerHTML = ''; // limpiar contenido previo
        Object.keys(datos.resultados).forEach(tipo => {
        const valores = datos.resultados[tipo]?.join('<br>') || '—';
        const error = datos.meta.errors?.[tipo] || '—';
        tbody.innerHTML += `
            <tr>
            <td class="border">${tipo}</td>
            <td class="border">${valores}</td>
            <td class="border text-red-600">${error}</td>
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