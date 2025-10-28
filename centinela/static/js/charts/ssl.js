/**
 * Función para inicializar los gráficos del módulo SSL/TLS.
 * @param {Object} datos - JSON de resultados del módulo SSL.
 */
(function() {
    function initGraficosSSL(datos) {
        try {
            console.log("(desde ssl.js) Datos recibidos para gráficos SSL:", datos);

            if (!datos) {
                console.warn("Módulo aún en proceso, datos incompletos.");
                return;
            }

            // === Verificar si hubo un error ===
            if (datos.error) {
                const tbody = document.getElementById('sslTableBody');
                const chartEl = document.getElementById('sslChart');
                
                // Buscar contenedor de errores en la card específica
                let container = null;
                if (tbody) {
                    const moduleCard = tbody.closest('.bg-light');
                    container = moduleCard?.querySelector('.container-errores');
                } else if (chartEl) {
                    const moduleCard = chartEl.closest('.bg-light');
                    container = moduleCard?.querySelector('.container-errores');
                }
                
                if (container) {
                    container.innerHTML = `
                        <strong class="fw-bold">⚠️ Error en certificado SSL</strong>
                        <p class="mb-0 mt-1">${datos.error}</p>
                        <ul class="mb-0 mt-1" style="font-size: 0.8rem;">
                            <li>El servidor no tiene SSL/TLS configurado</li>
                            <li>Conexión rechazada o timeout</li>
                            <li>Puerto 443 cerrado o inaccesible</li>
                        </ul>
                    `;
                    container.classList.remove('d-none');
                }
                
                if (chartEl) {
                    chartEl.parentElement.style.display = 'none';
                }
                
                if (tbody) {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="2" class="text-center text-muted py-3">
                                <em>No se pudo obtener información del certificado</em>
                            </td>
                        </tr>
                    `;
                }
                return;
            }

            // === Verificar validez del certificado ===
            const daysToExpire = datos.days_to_expire || 0;
            const isExpired = datos.expired || false;
            
            let estadoCert = '';
            let colorCert = '';
            
            if (isExpired) {
                estadoCert = 'Expirado';
                colorCert = '#dc3545'; // rojo
            } else if (daysToExpire <= 30) {
                estadoCert = 'Por vencer';
                colorCert = '#ffc107'; // amarillo
            } else {
                estadoCert = 'Válido';
                colorCert = '#28a745'; // verde
            }

            // === 1. Crear gráfico de barra horizontal (días restantes) ===
            const chartEl = document.getElementById('sslChart');
            if (!chartEl) {
                throw new Error("Elemento canvas no encontrado en el DOM.");
            }

            // Calcular porcentaje de vida útil (asumiendo 90 días como estándar Let's Encrypt)
            const totalDays = 90;
            const percentRemaining = Math.min((daysToExpire / totalDays) * 100, 100);

            new Chart(chartEl, {
                type: 'bar',
                data: {
                    labels: ['Validez del Certificado'],
                    datasets: [{
                        label: 'Días restantes',
                        data: [daysToExpire],
                        backgroundColor: colorCert,
                        borderWidth: 0
                    }]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        title: { 
                            display: true, 
                            text: `Certificado: ${estadoCert} (${daysToExpire} días)`,
                            font: { size: 14, weight: 'bold' }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `${context.parsed.x} días restantes`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            max: Math.max(daysToExpire + 10, 30),
                            ticks: {
                                callback: function(value) {
                                    return value + 'd';
                                }
                            }
                        }
                    }
                }
            });

            // === 2. Llenar tabla con información del certificado ===
            const tbody = document.getElementById('sslTableBody');
            if (!tbody) {
                throw new Error("Elemento tbody no encontrado en el DOM.");
            }

            tbody.innerHTML = '';

            // Información principal
            const info = [
                { 
                    campo: 'Dominio', 
                    valor: datos.subject?.commonName?.[0] || '—',
                    class: ''
                },
                { 
                    campo: 'Estado', 
                    valor: isExpired 
                        ? '<span class="badge bg-danger">Expirado</span>' 
                        : daysToExpire <= 30
                        ? '<span class="badge bg-warning text-dark">Por vencer</span>'
                        : '<span class="badge bg-success">Válido</span>',
                    class: isExpired ? 'table-danger' : daysToExpire <= 30 ? 'table-warning' : 'table-success'
                },
                { 
                    campo: 'Emisor', 
                    valor: datos.issuer?.organizationName?.[0] || '—',
                    class: ''
                },
                { 
                    campo: 'Válido hasta', 
                    valor: new Date(datos.not_after).toLocaleDateString('es-CL'),
                    class: ''
                },
                { 
                    campo: 'Días restantes', 
                    valor: daysToExpire,
                    class: ''
                },
                { 
                    campo: 'Tipo de clave', 
                    valor: `${datos.public_key?.type} ${datos.public_key?.key_size} bits`,
                    class: ''
                },
                { 
                    campo: 'Algoritmo', 
                    valor: datos.signature_algorithm || '—',
                    class: ''
                }
            ];

            info.forEach(item => {
                tbody.innerHTML += `
                    <tr class="${item.class}">
                        <td class="border"><strong>${item.campo}</strong></td>
                        <td class="border" style="font-size: 0.85rem;">${item.valor}</td>
                    </tr>
                `;
            });

        } catch (err) {
            console.error("Error al renderizar gráficos SSL:", err);
            
            // Buscar contenedor de errores en la card específica
            const tbody = document.getElementById('sslTableBody');
            const chartEl = document.getElementById('sslChart');
            
            let container = null;
            if (tbody) {
                const moduleCard = tbody.closest('.bg-light');
                container = moduleCard?.querySelector('.container-errores');
            } else if (chartEl) {
                const moduleCard = chartEl.closest('.bg-light');
                container = moduleCard?.querySelector('.container-errores');
            }
            
            if (container) {
                container.innerHTML = `<strong class="fw-bold">Error:</strong>
                    <span class="block sm:inline">⚠️ Error al renderizar datos: ${err.message}</span>`;
                container.classList.remove('d-none');
            }
        }
    }

    // Registrar en el namespace global
    window.Visuals = window.Visuals || {};
    window.Visuals["ssl"] = initGraficosSSL;
})();