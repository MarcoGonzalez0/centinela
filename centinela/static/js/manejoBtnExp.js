// Diccionario de explicaciones
const explicaciones = {
    "dns": "DNS es como la guía telefónica de Internet: traduce el nombre de un sitio (por ejemplo, madica.it) a una dirección que entienden las computadoras. Este módulo revisa si esa 'guía' responde correctamente y si hay registros importantes faltantes o con errores.",
    "dorks": "Este módulo busca información que podría estar expuesta públicamente en la web usando búsquedas avanzadas. Piensa en ello como revisar si alguien dejó documentos importantes en una carpeta pública por accidente.",
    "headers": "Los encabezados HTTP son pequeñas notas que envía el servidor al navegador. El módulo revisa si esas notas revelan información sensible o si falta alguna configuración de seguridad.",
    "nmap": "Nmap revisa qué 'puertas' (puertos) tiene abiertas un servidor. Es como comprobar qué entradas están abiertas en una casa para saber si alguien podría entrar por allí.",
    "ssl": "SSL/TLS es la capa que cifra la conexión (el candado en tu navegador). Este módulo revisa si el candado está bien configurado y si el certificado es válido y seguro.",
    "whois": "Whois consulta la información pública del dominio (quién lo registró y cuándo). Sirve para ver si la información de contacto es correcta o si hay señales sospechosas."
};

// Función para inicializar tooltips de un módulo específico
// LoadHTML se ejecuta N veces, es decir, por cada modulo
// Esa misma cantidad de veces se ejecuta esta función
// Crea un tooltip por cada módulo
function initializeTooltipsForModule(moduleWrapper, moduleName) {
    const tooltipElement = moduleWrapper.querySelector('[data-bs-toggle="tooltip"]');
    
    if (!tooltipElement) {
        console.warn(`No se encontró tooltip en módulo ${moduleName}`);
        return;
    }

    // Evitar inicializar dos veces
    if (bootstrap.Tooltip.getInstance(tooltipElement)) {
        console.log(`Tooltip ya inicializado para ${moduleName}`);
        return;
    }

    const explicacion = explicaciones[moduleName.toLowerCase()] || "No hay explicación disponible para este módulo.";

    // Inicializar tooltip con el contenido correcto
    new bootstrap.Tooltip(tooltipElement, {
        title: explicacion,
        html: false,
        trigger: 'hover focus',
        placement: 'top'
    });

    console.log(`✅ Tooltip inicializado para módulo ${moduleName}`);
}

// Por si acaso hay tooltips estáticos al cargar la página
document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM listo, buscando tooltips estáticos...');
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    console.log(`Encontrados ${tooltips.length} tooltips estáticos`);
});