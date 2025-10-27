# NMAP
from scan_nmap import run_nmap
import json

if __name__ == "__main__":
    target = "owasp.org"   # cámbialo por la IP/domino que quieras probar
    resultado = run_nmap(target, service_detection=True)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

#DORKS
# from scan_dorks import run_dorks
# import json
# from typing import Optional, List, Dict

# if __name__ == "__main__":
#     target = "madica.it"   # cámbialo por la IP/domino que quieras probar
#     resultado: List[Dict] = run_dorks(target)
#     print(json.dumps(resultado, indent=2, ensure_ascii=False))

#DNS
# from scan_dns import run_dns
# import json

# if __name__ == "__main__":
#     target = "educativaipchile.cl"   # cámbialo por la IP/domino que quieras probar
#     resultado = run_dns(target)
#     print(json.dumps(resultado, indent=2, ensure_ascii=False))

#WHOIS
# import json
# from scan_whois import run_whois

# if __name__ == "__main__":
#     target = "elvillegas.cl"   # cámbialo por la IP/domino que quieras probar
#     resultado = run_whois(target)
#     print(json.dumps(resultado, indent=2, ensure_ascii=False))

#SSL
# from scan_ssl import run_ssl
# import json

# if __name__ == "__main__":
#     target = "educativaipchile.cl"   # cámbialo por la IP/domino que quieras probar
#     resultado = run_ssl(target)
#     print(json.dumps(resultado, indent=2, ensure_ascii=False))

#HTTP HEADERS
# from scan_headerhttp import run_headerhttp
# import json

# if __name__ == "__main__":
#     domain = "hola.cl"   # cámbialo por la IP/domino que quieras probar
#     scan_result = run_headerhttp(domain)
#     print(json.dumps(scan_result, indent=2, ensure_ascii=False))