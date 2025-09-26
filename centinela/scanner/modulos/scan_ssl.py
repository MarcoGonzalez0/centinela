# ssl_scanner.py
import socket
import ssl
import json
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

# Intentamos usar cryptography para parseo completo (recomendado).
try:
    from cryptography import x509
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, ec
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except Exception:
    CRYPTO_AVAILABLE = False


class SSLCertScanner:
    def __init__(self, host: str, port: int = 443, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.raw_pem: Optional[str] = None
        self.cert_dict: Dict[str, Any] = {}
        self.meta: Dict[str, Any] = {}

    def _get_peer_cert_der(self) -> Optional[bytes]:
        """
        Conecta al host:port y devuelve el certificado en formato DER (bytes).
        """
        context = ssl.create_default_context()
        # No verificamos hostname ni chain para el escaneo; solo obtener cert
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
            with context.wrap_socket(sock, server_hostname=self.host) as ssock:
                der = ssock.getpeercert(binary_form=True)
                return der

    def scan(self) -> Dict[str, Any]:
        """
        Ejecuta el escaneo y devuelve el dict con la info del certificado.
        """
        try:
            der = self._get_peer_cert_der()
            if not der:
                return {"error": "No se obtuvo certificado (respuesta vacía)"}

            # Convertir a PEM para guardarlo/mostrarlo
            pem = ssl.DER_cert_to_PEM_cert(der)
            self.raw_pem = pem

            if CRYPTO_AVAILABLE:
                cert = x509.load_der_x509_certificate(der, backend=default_backend())
                self.cert_dict = self._parse_with_cryptography(cert)
            else:
                # Fallback: usar ssl.getpeercert (no da DER aquí), pero podemos parsear mínimo
                self.cert_dict = self._parse_with_ssl_fallback(der)

            # metadata
            self.meta["scanned_at"] = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
            self.cert_dict["raw_pem"] = self.raw_pem
            self.cert_dict["meta"] = self.meta
            return self.cert_dict

        except (socket.timeout, ConnectionRefusedError) as e:
            return {"error": f"Conexión fallida: {str(e)}"}
        except ssl.SSLError as e:
            return {"error": f"Error TLS/SSL: {str(e)}"}
        except Exception as e:
            return {"error": f"Error inesperado: {str(e)}"}

    def _parse_with_cryptography(self, cert: "x509.Certificate") -> Dict[str, Any]:
        """
        Extrae datos relevantes usando cryptography.x509
        """
        def _name_to_dict(name):
            return [{attr.oid._name or attr.oid.dotted_string: attr.value} for attr in name]

        # Subject
        subject = {}
        for rdn in cert.subject.rdns:
            for attr in rdn:
                key = attr.oid._name if getattr(attr.oid, "_name", None) else attr.oid.dotted_string
                subject.setdefault(key, []).append(str(attr.value))

        # Issuer
        issuer = {}
        for rdn in cert.issuer.rdns:
            for attr in rdn:
                key = attr.oid._name if getattr(attr.oid, "_name", None) else attr.oid.dotted_string
                issuer.setdefault(key, []).append(str(attr.value))

        # Validity
        not_before = cert.not_valid_before.replace(tzinfo=timezone.utc).isoformat()
        not_after = cert.not_valid_after_utc.replace(tzinfo=timezone.utc).isoformat()
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        days_to_expire = (cert.not_valid_after_utc - now).days if cert.not_valid_after_utc > now else 0
        expired = now > cert.not_valid_after_utc

        # SANs
        san_list: List[str] = []
        try:
            ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
            san_list = ext.value.get_values_for_type(x509.DNSName)
        except Exception:
            san_list = []

        # Public key info
        pubkey = cert.public_key()
        pubkey_info = {}
        try:
            if isinstance(pubkey, rsa.RSAPublicKey):
                pubkey_info = {"type": "RSA", "key_size": pubkey.key_size}
            elif isinstance(pubkey, ec.EllipticCurvePublicKey):
                pubkey_info = {"type": "EC", "curve": pubkey.curve.name}
            else:
                pubkey_info = {"type": type(pubkey).__name__}
        except Exception:
            pubkey_info = {"type": str(type(pubkey))}

        # Signature algorithm
        sig_alg = cert.signature_hash_algorithm.name if cert.signature_hash_algorithm else None

        parsed = {
            "subject": subject,
            "issuer": issuer,
            "not_before": not_before,
            "not_after": not_after,
            "expired": expired,
            "days_to_expire": days_to_expire,
            "serial_number": str(cert.serial_number),
            "signature_algorithm": sig_alg,
            "san": san_list,
            "public_key": pubkey_info,
        }
        return parsed

    def _parse_with_ssl_fallback(self, der_bytes: bytes) -> Dict[str, Any]:
        """
        Fallback simple si cryptography no está disponible.
        Usamos ssl module para obtener info mínima usando getpeercert() by re-opening socket.
        """
        # abrimos socket otra vez para usar getpeercert() en formato dict
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
            with context.wrap_socket(sock, server_hostname=self.host) as ssock:
                cert_dict = ssock.getpeercert()

        # cert_dict puede incluir 'subject', 'issuer', 'notAfter', 'notBefore', 'subjectAltName'...
        subject = {}
        for part in cert_dict.get("subject", ()):
            for k, v in part:
                subject.setdefault(k, []).append(v)

        issuer = {}
        for part in cert_dict.get("issuer", ()):
            for k, v in part:
                issuer.setdefault(k, []).append(v)

        san = []
        for typ, val in cert_dict.get("subjectAltName", ()):
            if typ.lower() == "dns":
                san.append(val)

        not_before = cert_dict.get("notBefore")
        not_after = cert_dict.get("notAfter")
        # transformar fechas si vienen en string -- ssl devuelve formato como 'Jun  1 12:00:00 2025 GMT'
        def _parse_ssl_date(dt_str):
            try:
                return datetime.strptime(dt_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc).isoformat()
            except Exception:
                return dt_str

        parsed = {
            "subject": subject,
            "issuer": issuer,
            "not_before": _parse_ssl_date(not_before) if not_before else None,
            "not_after": _parse_ssl_date(not_after) if not_after else None,
            "expired": None,
            "days_to_expire": None,
            "serial_number": cert_dict.get("serialNumber"),
            "signature_algorithm": None,
            "san": san
        }
        # calcular expired/days cuando sea posible
        try:
            if parsed["not_after"]:
                na = datetime.fromisoformat(parsed["not_after"])
                now = datetime.utcnow().replace(tzinfo=timezone.utc)
                parsed["expired"] = now > na
                parsed["days_to_expire"] = (na - now).days
        except Exception:
            pass

        return parsed

    def to_dict(self) -> Dict[str, Any]:
        """
        Devuelve dict listo para serializar (con raw_pem en cert_dict).
        """
        if not self.cert_dict:
            return self.scan()
        return self.cert_dict

    def to_json(self, indent: Optional[int] = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


# Helper público (función rápida)
def run_ssl(host: str, port: int = 443, timeout: float = 5.0) -> Dict[str, Any]:
    """
    Helper para uso rápido: escanea el certificado TLS/SSL del host y devuelve un dict.
    """
    scanner = SSLCertScanner(host, port=port, timeout=timeout)
    return scanner.scan()
