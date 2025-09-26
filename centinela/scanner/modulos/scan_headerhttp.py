import requests
from typing import Dict, Any
import json

def run_headerhttp(domain: str, timeout: float = 5.0) -> Dict[str, Any]:
    """
    Escanea los headers HTTP(S) de un dominio y detecta configuraciones básicas de seguridad.
    
    :param domain: dominio o URL (ej: 'example.com' o 'https://example.com')
    :param timeout: tiempo máximo de espera para la conexión
    :return: diccionario con headers y posibles alertas de seguridad
    """
    # Normalizar la URL agregando esquema si falta
    if not domain.startswith(("http://", "https://")):
        url = "https://" + domain  # por defecto HTTPS
    else:
        url = domain

    result: Dict[str, Any] = {"url": url, "headers": {}, "security_issues": []}

    try:
        # Enviar petición HTTP GET
        resp = requests.get(url, timeout=timeout, verify=False)
        headers = dict(resp.headers)
        result["headers"] = headers

        # ---------------- Revisiones básicas de seguridad ----------------
        if "Strict-Transport-Security" not in headers:
            result["security_issues"].append("HSTS no configurado (Strict-Transport-Security)")

        if "X-Frame-Options" not in headers:
            result["security_issues"].append("Protección clickjacking ausente (X-Frame-Options)")

        if "X-Content-Type-Options" not in headers:
            result["security_issues"].append("Protección MIME sniffing ausente (X-Content-Type-Options)")

        if "Content-Security-Policy" not in headers:
            result["security_issues"].append("Política de seguridad de contenido ausente (Content-Security-Policy)")

        if "Referrer-Policy" not in headers:
            result["security_issues"].append("Política de referrer no definida (Referrer-Policy)")

    except requests.exceptions.RequestException as e:
        result["error"] = str(e)

    return result

