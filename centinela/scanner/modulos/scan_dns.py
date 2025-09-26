# dns_resolver_json.py
import dns.resolver
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

class DNSResolver:
    def __init__(self, domain: str, record_types: Optional[List[str]] = None, timeout: float = 5.0):
        self.domain = domain
        self.record_types = record_types or ["A", "AAAA", "CNAME", "MX", "NS", "SOA", "TXT"]
        self.resolver = dns.resolver.Resolver()
        self.resolver.lifetime = timeout
        self.resolver.timeout = timeout
        self.records: Dict[str, List[str]] = {}
        self.meta: Dict[str, Any] = {}

    def resolve_all(self) -> Dict[str, List[str]]:
        """
        Realiza resoluciones DNS por cada tipo en self.record_types.
        Guarda resultados en self.records y retorna el dict.
        """
        self.records = {}
        for record_type in self.record_types:
            try:
                answers = self.resolver.resolve(self.domain, record_type)
                # para registros MX/SOA puede convenir formatear, aquí convertimos a string simple
                self.records[record_type] = [r.to_text() for r in answers]
            except Exception as e:
                # en caso de error devolvemos lista vacía pero almacenamos el error en meta si es útil
                self.records[record_type] = []
                # opcional: almacenar error corto (no sensible) por tipo
                self.meta.setdefault("errors", {})[record_type] = str(e)
        # guardar timestamp de la resolución
        self.meta["resolved_at"] = datetime.utcnow().isoformat() + "Z"
        return self.records

    def resolve_ns_ips(self) -> List[str]:
        """
        Devuelve lista única de IPs A (IPv4) encontradas en registros A + IPs resueltas desde NS.
        """
        ips = []
        # asegurarnos de tener resultados (si no, ejecutar resolve_all primero)
        if not self.records:
            self.resolve_all()

        # IPs A del dominio
        ips.extend(self.records.get("A", []))

        # Resolver NS -> A
        ns_records = self.records.get("NS", [])
        for ns in ns_records:
            # ns puede venir con un punto final; dns.resolver acepta ambos, pero lo normalizamos
            ns_hostname = ns.rstrip(".")
            try:
                ns_answers = self.resolver.resolve(ns_hostname, "A")
                ips.extend([a.to_text() for a in ns_answers])
            except Exception as e:
                # seguir si falla resolver un NS concreto
                self.meta.setdefault("ns_resolution_errors", {})[ns_hostname] = str(e)
                continue

        # quitar duplicados y retornar
        unique_ips = list(dict.fromkeys(ips))
        return unique_ips

    def to_dict(self) -> Dict[str, Any]:
        """
        Devuelve un dict serializable con registros, IPs de NS y metadatos.
        """
        # asegurarnos que records estén poblados
        if not self.records:
            self.resolve_all()

        ns_ips = self.resolve_ns_ips()
        return {
            "domain": self.domain,
            "records": self.records,
            "ns_ips": ns_ips,
            "meta": self.meta
        }

    def to_json(self, indent: Optional[int] = 2) -> str:
        """
        Devuelve el JSON (string) del resultado.
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
    
def run_dns(domain: str, record_types: Optional[List[str]] = None, timeout: float = 5.0) -> Dict[str, Any]:
    """
    Función helper para uso rápido sin instanciar la clase.
    Realiza la resolución y devuelve el dict resultado.
    """
    resolver = DNSResolver(domain=domain, record_types=record_types, timeout=timeout)
    resolver.resolve_all()
    return resolver.to_dict()

