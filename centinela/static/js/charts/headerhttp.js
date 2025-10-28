/**
 * Función para inicializar los gráficos del módulo HTTP Headers.
 * @param {Object} datos - JSON de resultados del módulo headerhttp.
 */
(function() {
    function initGraficosHeaders(datos) {
        try {
            console.log("(desde headerhttp.js) Datos recibidos para gráficos HTTP Headers:", datos);

            if (!datos || !datos.headers) {
                console.warn("Módulo aún en proceso, datos incompletos.");
                return;
            }

            // === Verificar si hubo un error de conexión ===
            if (datos.error || Object.keys(datos.headers).length === 0) {
                const tbody = document.getElementById('headersTableBody');
                const chartEl = document.getElementById('headersChart');
                
                // Buscar contenedor de errores en la card específica
                let container = null;
                if (tbody) {
                    const moduleCard = tbody.closest('.bg-light');
                    container = moduleCard?.querySelector('.container-errores');
                } else if (chartEl) {
                    const moduleCard = chartEl.closest('.bg-light');
                    container = moduleCard?.querySelector('.container-errores');
                }
                
                // Mostrar error en el contenedor de errores
                if (container) {
                    container.innerHTML = `
                        <strong class="fw-bold">⚠️ Error de Conexión</strong>
                        <p class="mb-0 mt-1">No se pudo conectar al servidor objetivo. Esto puede deberse a:</p>
                        <ul class="mb-0 mt-1" style="font-size: 0.8rem;">
                            <li>Timeout de conexión (servidor no responde)</li>
                            <li>Servidor inaccesible o caído</li>
                            <li>Firewall bloqueando la solicitud</li>
                        </ul>
                    `;
                    container.classList.remove('d-none');
                }
                
                // Ocultar canvas vacío
                if (chartEl) {
                    chartEl.parentElement.style.display = 'none';
                }
                
                // Mostrar mensaje en tabla
                if (tbody) {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="2" class="text-center text-muted py-3">
                                <em>No se pudieron obtener los headers HTTP</em>
                            </td>
                        </tr>
                    `;
                }
                return;
            }

            // === Headers de seguridad importantes ===
            const securityHeaders = {
                'Strict-Transport-Security': 'HSTS',
                'Content-Security-Policy': 'CSP',
                'X-Content-Type-Options': 'X-Content-Type',
                'X-Frame-Options': 'X-Frame-Options',
                'Referrer-Policy': 'Referrer-Policy',
                'Permissions-Policy': 'Permissions'
            };

            // Contar presentes y ausentes
            let presentes = 0;
            let ausentes = 0;
            const detalles = [];

            Object.keys(securityHeaders).forEach(header => {
                const presente = datos.headers.hasOwnProperty(header);
                if (presente) {
                    presentes++;
                    detalles.push({ nombre: securityHeaders[header], estado: 'presente' });
                } else {
                    ausentes++;
                    detalles.push({ nombre: securityHeaders[header], estado: 'ausente' });
                }
            });

            // === 1. Crear gráfico de dona (resumen) ===
            const chartEl = document.getElementById('headersChart');
            if (!chartEl) {
                throw new Error("Elemento canvas no encontrado en el DOM.");
            }

            new Chart(chartEl, {
                type: 'doughnut',
                data: {
                    labels: ['✓ Configurados', '⚠ Vulnerables'],
                    datasets: [{
                        data: [presentes, ausentes],
                        backgroundColor: ['#28a745', '#ffc107'],
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
                            text: `Headers de Seguridad: ${presentes}/${presentes + ausentes}`,
                            font: { size: 14, weight: 'bold' }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    const total = presentes + ausentes;
                                    const percentage = ((value / total) * 100).toFixed(0);
                                    return `${label}: ${value} (${percentage}%)`;
                                }
                            }
                        }
                    }
                }
            });

            // === 2. Llenar tabla con detalles de cada header ===
            const tbody = document.getElementById('headersTableBody');
            if (!tbody) {
                throw new Error("Elemento tbody no encontrado en el DOM.");
            }

            tbody.innerHTML = '';
            
            // Ordenar: primero ausentes (más crítico), luego presentes
            detalles.sort((a, b) => {
                if (a.estado === 'ausente' && b.estado === 'presente') return -1;
                if (a.estado === 'presente' && b.estado === 'ausente') return 1;
                return 0;
            });

            detalles.forEach(item => {
                const header = Object.keys(securityHeaders).find(
                    key => securityHeaders[key] === item.nombre
                );
                
                if (item.estado === 'presente') {
                    const valor = datos.headers[header];
                    const valorMostrar = valor.length > 50 
                        ? valor.substring(0, 50) + '...' 
                        : valor;
                    
                    tbody.innerHTML += `
                        <tr class="table-success">
                            <td class="border">
                                <span class="badge bg-success me-1">✓</span>
                                <strong>${item.nombre}</strong>
                            </td>
                            <td class="border" style="font-size: 0.80rem;">${valorMostrar}</td>
                        </tr>
                    `;
                } else {
                    tbody.innerHTML += `
                        <tr class="table-danger">
                            <td class="border">
                                <span class="badge bg-danger me-1">✗</span>
                                <strong>${item.nombre}</strong>
                            </td>
                            <td class="border text-muted" style="font-size: 0.80rem;">
                                <em>No configurado</em>
                            </td>
                        </tr>
                    `;
                }
            });

        } catch (err) {
            console.error("Error al renderizar gráficos HTTP Headers:", err);
            
            const container = document.querySelector('.container-errores');
            if (container) {
                container.innerHTML = `<strong class="font-bold">Error:</strong>
                    <span class="block sm:inline">⚠️ Error al renderizar datos: ${err.message}</span>`;
                container.classList.remove('hidden');
            }
        }
    }

    // Registrar en el namespace global
    window.Visuals = window.Visuals || {};
    window.Visuals["headers"] = initGraficosHeaders;
})();