/**
 * Función para inicializar los gráficos del módulo Nmap.
 * @param {Array} datos - JSON de resultados del módulo Nmap.
 */
(function() {
    function initGraficosNmap(datos) {
        try {
            console.log("(desde nmap.js) Datos recibidos para gráficos Nmap:", datos);

            if (!datos || !Array.isArray(datos)) {
                console.warn("Módulo aún en proceso, datos incompletos.");
                return;
            }

            // === Verificar si hubo un error ===
            if (datos.length === 0 || (datos[0] && datos[0].error)) {
                const container = document.querySelector('.container-errores');
                const tbody = document.getElementById('nmapTableBody');
                
                if (container) {
                    container.innerHTML = `
                        <strong class="fw-bold">⚠️ Error en escaneo Nmap</strong>
                        <p class="mb-0 mt-1">No se pudo realizar el escaneo de puertos. Posibles causas:</p>
                        <ul class="mb-0 mt-1" style="font-size: 0.8rem;">
                            <li>Host no responde o está caído</li>
                            <li>Firewall bloqueando el escaneo</li>
                            <li>Timeout de conexión</li>
                        </ul>
                    `;
                    container.classList.remove('d-none');
                }
                
                const chartEl = document.getElementById('nmapChart');
                if (chartEl) {
                    chartEl.parentElement.style.display = 'none';
                }
                
                if (tbody) {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="4" class="text-center text-muted py-3">
                                <em>No se pudieron escanear puertos</em>
                            </td>
                        </tr>
                    `;
                }
                return;
            }

            // Extraer todos los puertos del primer host
            const host = datos[0];
            const ports = host.ports || [];

            if (ports.length === 0) {
                console.warn("No se encontraron puertos escaneados");
                return;
            }

            // === Contar estados de puertos ===
            const estados = {
                'open': 0,
                'closed': 0,
                'filtered': 0
            };

            ports.forEach(port => {
                const estado = port.state.toLowerCase();
                if (estados.hasOwnProperty(estado)) {
                    estados[estado]++;
                }
            });

            // === 1. Crear gráfico de dona ===
            const chartEl = document.getElementById('nmapChart');
            if (!chartEl) {
                throw new Error("Elemento canvas no encontrado en el DOM.");
            }

            new Chart(chartEl, {
                type: 'doughnut',
                data: {
                    labels: ['🟢 Abiertos', '🔴 Cerrados', '🟡 Filtrados'],
                    datasets: [{
                        data: [estados.open, estados.closed, estados.filtered],
                        backgroundColor: ['#28a745', '#dc3545', '#ffc107'],
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom',
                            labels: {
                                font: { size: 11 },
                                padding: 10
                            }
                        },
                        title: { 
                            display: true, 
                            text: `Puertos Escaneados: ${ports.length} total`,
                            font: { size: 14, weight: 'bold' }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = ports.length;
                                    const percentage = ((value / total) * 100).toFixed(0);
                                    return `${label}: ${value} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });

            // === 2. Llenar tabla con información de puertos ===
            const tbody = document.getElementById('nmapTableBody');
            if (!tbody) {
                throw new Error("Elemento tbody no encontrado en el DOM.");
            }

            tbody.innerHTML = '';

            // Ordenar: primero abiertos, luego filtrados, luego cerrados
            const ordenEstado = { 'open': 1, 'filtered': 2, 'closed': 3 };
            ports.sort((a, b) => ordenEstado[a.state] - ordenEstado[b.state]);

            ports.forEach(port => {
                let estadoClass = '';
                let estadoBadge = '';
                
                switch(port.state.toLowerCase()) {
                    case 'open':
                        estadoClass = 'table-success';
                        estadoBadge = '<span class="badge bg-success">🟢 Abierto</span>';
                        break;
                    case 'closed':
                        estadoClass = 'table-danger';
                        estadoBadge = '<span class="badge bg-danger">🔴 Cerrado</span>';
                        break;
                    case 'filtered':
                        estadoClass = 'table-warning';
                        estadoBadge = '<span class="badge bg-warning text-dark">🟡 Filtrado</span>';
                        break;
                    default:
                        estadoBadge = `<span class="badge bg-secondary">${port.state}</span>`;
                }

                const servicio = port.service.name || '—';
                const producto = port.service.product || '—';

                tbody.innerHTML += `
                    <tr class="${estadoClass}">
                        <td class="border"><strong>${port.port}/${port.protocol}</strong></td>
                        <td class="border">${estadoBadge}</td>
                        <td class="border">${servicio}</td>
                        <td class="border" style="font-size: 0.80rem;">${producto}</td>
                    </tr>
                `;
            });

        } catch (err) {
            console.error("Error al renderizar gráficos Nmap:", err);
            
            const container = document.querySelector('.container-errores');
            if (container) {
                container.innerHTML = `<strong class="fw-bold">Error:</strong>
                    <span class="block sm:inline">⚠️ Error al renderizar datos: ${err.message}</span>`;
                container.classList.remove('d-none');
            }
        }
    }

    // Registrar en el namespace global
    window.Visuals = window.Visuals || {};
    window.Visuals["nmap"] = initGraficosNmap;
})();