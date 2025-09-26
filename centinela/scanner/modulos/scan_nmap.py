# app/scan_nmap.py
import subprocess
import xml.etree.ElementTree as ET

def run_nmap(ip, service_detection=True):
    """
    Ejecuta Nmap sobre un host con puertos comunes y devuelve JSON.
    
    :param ip: IP o dominio del host
    :param service_detection: si True, hace -sV para detección de servicios
    :return: lista de hosts con info de puertos (JSON serializable)
    """
    result = []

    # Lista de puertos comunes para escaneo intermedio
    puertos = "21,22,23,25,53,80,110,143,443,3306,3389"
    #puertos = "22,80,443,3306"

    try:
        cmd = ["nmap", "-Pn", "-T4", "-p", puertos, "-oX", "-"]  # XML directo a stdout
        if service_detection:
            cmd.insert(1, "-sV")  # añade detección de servicios

        proc = subprocess.run(cmd + [ip], capture_output=True, text=True, check=True)
        result = parse_nmap(proc.stdout)

    except subprocess.CalledProcessError as e:
        result = {"error": str(e)}

    return result


def parse_nmap(xml_string):
    """
    Parsea el XML de Nmap (en string) y devuelve JSON.
    """
    root = ET.fromstring(xml_string)
    hosts_data = []

    for host in root.findall("host"):
        host_info = {"ip": "", "ports": []}

        addr = host.find("address")
        if addr is not None:
            host_info["ip"] = addr.attrib.get("addr", "")

        ports = host.find("ports")
        if ports is not None:
            for port in ports.findall("port"):
                port_info = {
                    "port": port.attrib.get("portid", ""),
                    "protocol": port.attrib.get("protocol", ""),
                    "state": port.find("state").attrib.get("state", ""),
                    "service": {}
                }
                service = port.find("service")
                if service is not None:
                    port_info["service"] = {
                        "name": service.attrib.get("name", ""),
                        "product": service.attrib.get("product", ""),
                        "version": service.attrib.get("version", "")
                    }
                host_info["ports"].append(port_info)

        hosts_data.append(host_info)

    return hosts_data
