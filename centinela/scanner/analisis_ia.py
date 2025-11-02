import os
import json
import requests
from dotenv import load_dotenv
from typing import Optional, Dict

# -------------------- Constantes --------------------
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# -------------------- Cargar variables de entorno --------------------
def load_env_variables() -> Optional[Dict[str, str]]:
    """Carga las variables de entorno necesarias"""
    load_dotenv()
    deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')

    if not deepseek_api_key:
        return None

    return {'deepseek_api_key': deepseek_api_key}

# -------------------- Cliente de DeepSeek --------------------
class DeepSeekClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def analyze_content(self, prompt: str, temperature: float = 0.2) -> Optional[str]:
        """Envía una solicitud a la API de DeepSeek para analizar contenido"""
        payload = {
            "model": DEEPSEEK_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": 300  # Reducido para mantener respuestas breves
        }

        try:
            response = requests.post(
                DEEPSEEK_API_URL,
                headers=self.headers,
                json=payload,
                timeout=90
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException:
            return None


# -------------------- Análisis genérico de módulos --------------------
def analizar_modulo_con_ia(nombre_modulo: str, resultados: Dict, client: DeepSeekClient) -> Optional[Dict]:
    """
    Analiza resultados de cualquier módulo y devuelve:
    {
        "explicacion": str (2-3 oraciones para no técnicos),
        "riesgo": "Bajo/Medio/Alto",
        "color": "#28a745/#ffc107/#dc3545"
    }
    """
    
    # Convertir resultados a texto resumido (limitar tamaño)
    resultados_texto = json.dumps(resultados, indent=2, ensure_ascii=False)[:1500]
    
    # Prompts específicos según módulo para mayor precisión
    prompts_modulos = {
        "dns": "DNS (Sistema de Nombres de Dominio)",
        "headers": "Cabeceras HTTP de seguridad",
        "nmap": "Puertos y servicios de red",
        "ssl": "Certificado SSL/TLS",
        "whois": "Registro del dominio",
        "dorks": "Información expuesta en buscadores"
    }
    
    tipo_modulo = prompts_modulos.get(nombre_modulo, nombre_modulo)
    
    prompt = f"""
Eres un experto en ciberseguridad explicando resultados a una persona SIN conocimientos técnicos.

MÓDULO ANALIZADO: {tipo_modulo}

RESULTADOS:
{resultados_texto}

INSTRUCCIONES:
1. Explica en 2-3 oraciones SIMPLES qué se encontró y por qué es importante
2. Usa pocos términos técnicos
3. Usa analogías simples si es necesario
4. Clasifica el riesgo como: Bajo, Medio o Alto

CRITERIOS DE RIESGO:
- Alto: Problemas graves que ponen en peligro la seguridad (certificados vencidos, puertos críticos abiertos, datos sensibles expuestos)
- Medio: Configuraciones que podrían mejorarse (headers faltantes, configuraciones subóptimas)
- Bajo: Todo está bien configurado y seguro

FORMATO DE RESPUESTA (solo JSON, nada más):
{{
    "explicacion": "Explicación simple en 2-3 oraciones",
    "riesgo": "Bajo/Medio/Alto"
}}
"""

    respuesta = client.analyze_content(prompt, temperature=0.2)
    
    if not respuesta:
        return None

    # Limpiar respuesta de markdown
    if "```json" in respuesta:
        respuesta = respuesta.split("```json")[1].split("```")[0].strip()
    elif "```" in respuesta:
        respuesta = respuesta.split("```")[1].split("```")[0].strip()
    
    try:
        datos = json.loads(respuesta)
        
        # Mapear riesgo a color
        color_map = {
            "Bajo": "#28a745",
            "bajo": "#28a745",
            "Medio": "#ffc107",
            "medio": "#ffc107",
            "Alto": "#dc3545",
            "alto": "#dc3545"
        }
        
        riesgo = datos.get("riesgo", "Medio")
        datos["color"] = color_map.get(riesgo, "#6c757d")
        
        # Normalizar riesgo a formato consistente
        datos["riesgo"] = riesgo.capitalize()
        
        return datos
    except json.JSONDecodeError:
        return None


# -------------------- Función principal --------------------
def main_analisis_ia(nombre_modulo: str, resultados: Dict) -> Dict:
    """
    Función principal para análisis de módulos individuales
    Retorna: {"explicacion": str, "riesgo": str, "color": str}
    """
    try:
        env_vars = load_env_variables()
        if not env_vars:
            return {
                "explicacion": "No se pudo conectar al servicio de análisis. Verifica la configuración de la API.",
                "riesgo": "Error",
                "color": "#dc3545"
            }

        client = DeepSeekClient(env_vars['deepseek_api_key'])
        analisis = analizar_modulo_con_ia(nombre_modulo, resultados, client)
        
        if analisis:
            return analisis
        else:
            return {
                "explicacion": "No se pudo procesar el análisis en este momento. Por favor, intenta nuevamente.",
                "riesgo": "Error",
                "color": "#6c757d"
            }

    except Exception as e:
        return {
            "explicacion": f"Ocurrió un error inesperado al procesar el análisis: {str(e)}",
            "riesgo": "Error",
            "color": "#dc3545"
        }