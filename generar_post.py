print("--- EJECUTANDO SCRIPT v18: VERSIÓN FINAL ESTABLE ---")
import os
import datetime
import json
from pathlib import Path
import sys
from groq import Groq
import random
from bs4 import BeautifulSoup

# --- CONFIGURACIÓN ---
# ¡IMPORTANTE! MODIFICA ESTA LISTA con los nombres exactos de tus imágenes.
LISTA_DE_IMAGENES = [
    "imagen-1.jpg", "imagen-2.jpg", "imagen-3.jpg", "imagen-4.jpg",
    "imagen-5.jpg", "imagen-6.jpg", "imagen-8.jpg", "imagen-9.jpg",
    "imagen-10.jpg", "imagen-11.jpg"
]

try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    print("✅ Cliente de Groq configurado.")
except Exception as e:
    sys.exit(f"❌ Error al configurar el cliente de Groq: {e}")

POSTS_DIR = Path("posts")
ROOT_DIR = Path(".")

# --- PLANTILLAS HTML ---
HTML_HEADER = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{title}</title><link rel="stylesheet" href="{css_path}"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet"></head><body><header><div class="logo"><img src="{logo_path}" alt="sIA Logo"><h1><a href="{index_path}">sIA</a></h1></div><nav><ul><li><a href="#">Noticias</a></li><li><a href="#">Análisis</a></li><li><a href="#">IA para Todos</a></li><li><a href="#">Herramientas IA</a></li><li><a href="#">Opinión</a></li></ul></nav><a href="https://docs.google.com/forms/d/e/1FAIpQLSeNl4keU0p1eDMvzUpM5p57Naf5qBMsl5MSJNBMxPnWbofshQ/viewform?usp=header" target="_blank" class="subscribe-button">Suscríbete</a></header>"""
HTML_FOOTER = """<footer><p>&copy; 2025 sIA. Todos los derechos reservados.</p><p><a href="{privacy_path}">Política de Privacidad</a></p></footer></body></html>"""
PRIVACY_POLICY_CONTENT = """<main class="article-body" style="margin-top: 2rem;"><h1 class="article-title">Política de Privacidad</h1><div class="article-content"><p><strong>Fecha de vigencia:</strong> 12 de agosto de 2025</p><h2>1. Introducción</h2><p>Bienvenido a sIA. Tu privacidad es de suma importancia para nosotros. Esta Política de Privacidad describe qué datos recopilamos, cómo los usamos, cómo los protegemos y qué opciones tienes sobre tus datos cuando visitas nuestro sitio web.</p><h2>2. Información que Recopilamos</h2><ul><li><strong>Información Personal:</strong> Esto incluye información que nos proporcionas voluntariamente, como tu dirección de correo electrónico al suscribirte a nuestro boletín.</li><li><strong>Información No Personal:</strong> Recopilamos datos anónimos sobre tu visita (dirección IP, tipo de navegador, etc.) a través de cookies y servicios de análisis.</li></ul><h2>3. Uso de Cookies y Terceros</h2><p>Utilizamos cookies para mejorar la funcionalidad del sitio y personalizar tu experiencia. Somos participantes en el programa de publicidad de Google AdSense. Google, como proveedor externo, utiliza cookies para publicar anuncios. Puedes inhabilitar la publicidad personalizada en la <a href="https://adssettings.google.com/authenticated" target="_blank">configuración de anuncios de Google</a>.</p><h2>4. Tus Derechos</h2><p>Tienes derecho a acceder, rectificar o eliminar tu información personal. Para darte de baja de nuestro boletín, puedes seguir el enlace de "cancelar suscripción" que se incluirá en cada correo.</p><h2>5. Cambios a esta Política</h2><p>Podemos actualizar esta Política de Privacidad periódicamente. Te notificaremos cualquier cambio importante publicando la nueva política en nuestro sitio web.</p><h2>6. Contacto</h2><p>Si tienes alguna pregunta sobre esta Política, contáctanos a través de los medios disponibles en el sitio.</p></div></main>"""

# --- FUNCIONES ---

def generar_contenido_ia():
    print("🤖 Generando contenido con la API de Groq...")
    system_prompt = "Eres un periodista de tecnología para 'sIA', especializado en IA en Latinoamérica. Tu respuesta DEBE ser únicamente un objeto JSON válido."
    user_prompt = """Genera UN artículo de noticias sobre un tema de actualidad en IA relevante para Latinoamérica (una nueva startup, una inversión, un avance tecnológico, etc.). El artículo debe ser conciso (35
