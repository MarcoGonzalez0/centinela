# whois_utils.py
import whois
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

def _to_iso(val: Any) -> Optional[Union[str, List[str]]]:
    """
    Convierte datetime o lista de datetimes/strings a ISO strings.
    Devuelve None si val es None o vacío.
    """
    if val is None:
        return None
    # Si es lista, mapear recursivamente
    if isinstance(val, (list, tuple, set)):
        out = []
        for x in val:
            if isinstance(x, datetime):
                out.append(x.isoformat())
            elif isinstance(x, str):
                out.append(x)
            else:
                out.append(str(x))
        return out if out else None
    # Si es datetime
    if isinstance(val, datetime):
        return val.isoformat()
    # Si es string u otro tipo, devolver str
    return str(val)

def _ensure_list(val: Any) -> List[str]:
    """Devuelve una lista de strings, incluso si val es str o None."""
    if val is None:
        return []
    if isinstance(val, (list, tuple, set)):
        return [str(x) for x in val]
    return [str(val)]

def run_whois(domain: str) -> Dict[str, Any]:
    """
    Ejecuta whois para el dominio y devuelve un dict JSON-serializable.
    """
    try:
        w = whois.whois(domain)
    except Exception as e:
        # Devuelve un dict con error para que el caller lo maneje (no lanzar excepción)
        return {"error": f"whois lookup failed: {str(e)}"}

    # Extraer y normalizar campos
    result: Dict[str, Any] = {
        "domain_name": w.domain_name if hasattr(w, "domain_name") else None,
        "registrar": w.registrar if hasattr(w, "registrar") else None,
        "creation_date": _to_iso(getattr(w, "creation_date", None)),
        "expiration_date": _to_iso(getattr(w, "expiration_date", None)),
        "updated_date": _to_iso(getattr(w, "updated_date", None)),
        "name_servers": _ensure_list(getattr(w, "name_servers", None)),
        "status": _ensure_list(getattr(w, "status", None)),
        "emails": _ensure_list(getattr(w, "emails", None)),
        "country": getattr(w, "country", None),
        "whois_server": getattr(w, "whois_server", None),
        # opcional: raw text (útil para debugging). Ten cuidado con datos sensibles.
        "raw": getattr(w, "text", None)
    }

    return result
