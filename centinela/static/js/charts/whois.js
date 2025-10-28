/**
 * Función para inicializar los gráficos del módulo WHOIS.
 * @param {Object} datos - JSON de resultados del módulo WHOIS.
 */
(function() {
    function initGraficosWhois(datos) {
        try {
            console.log("(desde whois.js) Datos recibidos para gráficos WHOIS:", datos);

            if (!datos) {
                console.warn("Módulo aún en proceso, datos incompletos.");
                return;
            }

            // === Verificar si hubo un error ===
            if (datos.error) {
                const tbody = document.getElementById('whoisTableBody');
                const chartEl = document.getElementById('whoisChart');
                
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
                        <strong class="fw-bold">⚠️ Error en consulta WHOIS</strong>
                        <p class="mb-0 mt-1">${datos.error}</p>
                        <ul class="mb-0 mt-1" style="font-size: 0.8rem;">
                            <li>El dominio no existe o es inválido</li>
                            <li>Servidor WHOIS no responde</li>
                            <li>Información protegida por privacidad</li>
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
                                <em>No se pudo obtener información WHOIS</em>
                            </td>
                        </tr>
                    `;
                }
                return;
            }

            // === Calcular edad y tiempo hasta expiración ===
            const parseDate = (dateStr) => {
                if (!dateStr) return null;
                // Formato: "2021-06-10 06:45:24 CLST"
                const parts = dateStr.split(' ');
                return new Date(parts[0]);
            };

            const creationDate = parseDate(datos.creation_date);
            const expirationDate = parseDate(datos.expiration_date);
            const now = new Date();

            let daysOld = 0;
            let daysToExpire = 0;
            let totalLifetime = 0;

            if (creationDate && expirationDate) {
                daysOld = Math.floor((now - creationDate) / (1000 * 60 * 60 * 24));
                daysToExpire = Math.floor((expirationDate - now) / (1000 * 60 * 60 * 24));
                totalLifetime = Math.floor((expirationDate - creationDate) / (1000 * 60 * 60 * 24));
            }

            // === 1. Crear gráfico de timeline ===
            const chartEl = document.getElementById('whoisChart');
            if (!chartEl) {
                throw new Error("Elemento canvas no encontrado en el DOM.");
            }

            // Determinar color según tiempo de expiración
            let colorExpiration = daysToExpire <= 30 ? '#dc3545' : daysToExpire <= 90 ? '#ffc107' : '#28a745';

            new Chart(chartEl, {
                type: 'bar',
                data: {
                    labels: ['Antigüedad', 'Hasta expiración'],
                    datasets: [{
                        label: 'Días',
                        data: [daysOld, daysToExpire],
                        backgroundColor: ['#879dacff', colorExpiration],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        title: { 
                            display: true, 
                            text: `Timeline del Dominio`,
                            font: { size: 14, weight: 'bold' }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label;
                                    const value = context.parsed.y;
                                    const years = Math.floor(value / 365);
                                    const days = value % 365;
                                    return `${label}: ${years}a ${days}d (${value} días totales)`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return Math.floor(value / 365) + 'a';
                                }
                            }
                        }
                    }
                }
            });

            // === 2. Extraer información del registrante del campo raw ===
            let registrantName = '—';
            let registrantOrg = '—';
            
            if (datos.raw) {
                const nameMatch = datos.raw.match(/Registrant name:\s*(.+)/i);
                const orgMatch = datos.raw.match(/Registrant organisation:\s*(.+)/i);
                
                if (nameMatch && nameMatch[1].trim()) {
                    registrantName = nameMatch[1].trim();
                }
                if (orgMatch && orgMatch[1].trim()) {
                    registrantOrg = orgMatch[1].trim();
                }
            }

            // === 3. Llenar tabla con información del dominio ===
            const tbody = document.getElementById('whoisTableBody');
            if (!tbody) {
                throw new Error("Elemento tbody no encontrado en el DOM.");
            }

            tbody.innerHTML = '';

            // Determinar estado de expiración
            let estadoExpiracion = '';
            let classExpiracion = '';
            if (daysToExpire <= 0) {
                estadoExpiracion = '<span class="badge bg-danger">Expirado</span>';
                classExpiracion = 'table-danger';
            } else if (daysToExpire <= 30) {
                estadoExpiracion = '<span class="badge bg-danger">Por vencer (crítico)</span>';
                classExpiracion = 'table-danger';
            } else if (daysToExpire <= 90) {
                estadoExpiracion = '<span class="badge bg-warning text-dark">Por renovar pronto</span>';
                classExpiracion = 'table-warning';
            } else {
                estadoExpiracion = '<span class="badge bg-success">Activo</span>';
                classExpiracion = 'table-success';
            }

            // Información principal
            const info = [
                { 
                    campo: 'Registrante', 
                    valor: registrantName !== '—' 
                        ? `${registrantName}${registrantOrg !== '—' ? '<br><small class="text-muted">' + registrantOrg + '</small>' : ''}`
                        : '<em class="text-muted">Información protegida</em>',
                    class: ''
                },
                { 
                    campo: 'Registrar', 
                    valor: datos.registrar || '—',
                    class: ''
                },
                { 
                    campo: 'Estado', 
                    valor: estadoExpiracion,
                    class: classExpiracion
                },
                { 
                    campo: 'Fecha de creación', 
                    valor: creationDate ? creationDate.toLocaleDateString('es-CL') : '—',
                    class: ''
                },
                { 
                    campo: 'Fecha de expiración', 
                    valor: expirationDate ? expirationDate.toLocaleDateString('es-CL') : '—',
                    class: ''
                },
                { 
                    campo: 'Antigüedad', 
                    valor: `${Math.floor(daysOld / 365)} años, ${daysOld % 365} días`,
                    class: ''
                },
                { 
                    campo: 'Días hasta expiración', 
                    valor: daysToExpire,
                    class: ''
                },
                { 
                    campo: 'Servidores DNS', 
                    valor: datos.name_servers && datos.name_servers.length > 0 
                        ? datos.name_servers.join('<br>') 
                        : '—',
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
            console.error("Error al renderizar gráficos WHOIS:", err);
            
            // Buscar contenedor de errores en la card específica
            const tbody = document.getElementById('whoisTableBody');
            const chartEl = document.getElementById('whoisChart');
            
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
    window.Visuals["whois"] = initGraficosWhois;
})();