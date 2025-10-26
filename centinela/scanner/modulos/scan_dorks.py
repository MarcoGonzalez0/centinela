# dorks_runner.py
import os
import logging
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ---------------- ENV ----------------
def _load_env() -> Optional[Dict[str, str]]:
    load_dotenv()
    api_key = os.getenv("API_KEY_SEARCH_GOOGLE")
    cx = os.getenv("SEARCH_ENGINE_ID")
    if not api_key or not cx:
        logging.error("Falta API_KEY_SEARCH_GOOGLE o SEARCH_ENGINE_ID en .env")
        return None
    return {"api_key": api_key, "cx": cx}

# ---------------- Google CSE helper ----------------
def _perform_google_search(api_key: str, cx: str, query: str, start: int = 1, num: int = 10, timeout: int = 10) -> List[Dict]:
    """
    Ejecuta una búsqueda usando Google Custom Search API y devuelve la lista 'items' (puede ser vacía).
    """
    base = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "start": max(1, int(start)),
        "num": max(1, min(10, int(num)))
    }
    try:
        resp = requests.get(base, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        return data.get("items", []) or []
    except requests.HTTPError as e:
        logging.error("HTTP error en Google CSE: %s - %s", e, getattr(e.response, "text", ""))
    except requests.Timeout:
        logging.error("Timeout en Google CSE")
    except requests.RequestException as e:
        logging.error("Error request Google CSE: %s", e)
    except ValueError:
        logging.error("Error parseando JSON de la respuesta")
    return []

# ---------------- Dorks comunes ----------------
COMMON_DORKS = [
    # Archivos de bases de datos / dumps
    ['site:{domain} filetype:sql', "Archivos SQL"],
    # Archivos de configuración / credenciales
    ['site:{domain} (filetype:env OR filetype:cfg OR filetype:conf OR filetype:ini)', "Archivos de configuración"],
    # Backups e índices públicos
    ['site:{domain} intitle:"index of" (backup OR .bak)', "Backups e índices públicos"],
    # Archivos Office / pdf con posible información sensible
    ['site:{domain} (filetype:doc OR filetype:docx OR filetype:pdf)', "Archivos DOC/PDF con posible información sensible"],
    # URLs expuestas, archivos de logs o config
    ['site:{domain} inurl:(admin OR dashboard OR config OR configs OR log OR logs OR "error.log" OR "access.log" OR "wp-config.php") -site:github.com -site:gitlab.com -site:stackoverflow.com', "URLs expuestas, archivos de logs o config"]
]

# ---------------- Runner público ----------------
def run_dorks(domain: str, max_dorks: int = 5, results_per_dork: int = 1, max_total_results: int = 5) -> List[Dict]:
    """
    Ejecuta hasta `max_dorks` dorks sobre `domain` usando Google Custom Search API.
    Devuelve una lista de diccionarios con la forma:
      [{"query": "...", "results": [{"title":..., "snippet":..., "link":...}, ...]}, ...]
    - max_dorks: número de plantillas a ejecutar (máx 5, por defecto 5)
    - results_per_dork: resultados por petición (1..10)
    - max_total_results: opcional, tope global de resultados agregados (None = sin tope)
    """
    env = _load_env()
    if not env:
        raise RuntimeError("Faltan credenciales en .env: API_KEY_SEARCH_GOOGLE y/o SEARCH_ENGINE_ID")

    api_key = env["api_key"]
    cx = env["cx"]

    templates = COMMON_DORKS[: max(1, min(5, int(max_dorks)))] # minimo 1, máximo 5
    aggregated: List[Dict] = []
    total_count = 0

    for tpl in templates:
        q = tpl[0].format(domain=domain)
        logging.info("Ejecutando dork: %s", q)
        items = _perform_google_search(api_key, cx, q, start=1, num=results_per_dork)

        results = []
        for it in items:
            results.append({
                "title": it.get("title"),
                "snippet": it.get("snippet"),
                "link": it.get("link")
            })
            total_count += 1
            if max_total_results is not None and total_count >= max_total_results:
                break

        aggregated.append({"description": tpl[1], "query": q, "results": results})

        if max_total_results is not None and total_count >= max_total_results:
            break

    return aggregated
