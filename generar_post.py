# --- EJECUTANDO SCRIPT v3.0: VERSIÓN FINAL CON ARTÍCULOS RELACIONADOS ---
import os
import datetime
import json
from pathlib import Path
import sys
import random
from groq import Groq
from bs4 import BeautifulSoup

print("--- INICIANDO SCRIPT DE GENERACIÓN DE CONTENIDO v3.0 ---")

# \--- CONFIGURACIÓN AUTOMÁTICA DE IMÁGENES ---

IMG\_DIR = Path("static/img")
LISTA\_DE\_IMAGENES = []
try:
extensions = ['.png', '.jpg', '.jpeg', '.webp']
LISTA\_DE\_IMAGENES = [f.name for f in IMG\_DIR.glob('\*') if f.suffix.lower() in extensions and f.name \!= 'logo.png']
if not LISTA\_DE\_IMAGENES:
LISTA\_DE\_IMAGENES.append("logo.png")
print(f"⚠️  Advertencia: No se encontraron imágenes. Se usará 'logo.png'.")
else:
print(f"✅ {len(LISTA\_DE\_IMAGENES)} imágenes encontradas en {IMG\_DIR}.")
except Exception as e:
print(f"❌ Error al cargar imágenes: {e}")
LISTA\_DE\_IMAGENES = ["logo.png"]

# \--- CONFIGURACIÓN DEL CLIENTE DE IA ---

try:
client = Groq(api\_key=os.getenv("GROQ\_API\_KEY"))
print("✅ Cliente de Groq configurado.")
except Exception as e:
sys.exit(f"❌ Error fatal al configurar el cliente de Groq: {e}")

POSTS\_DIR = Path("posts")
ROOT\_DIR = Path(".")

# \--- PLANTILLAS HTML ---

HTML\_HEADER = """&lt;!DOCTYPE html&gt;&lt;html lang=&quot;es&quot;&gt;&lt;head&gt;&lt;meta charset=&quot;UTF-8&quot;&gt;&lt;meta name=&quot;viewport&quot; content=&quot;width=device-width, initial-scale=1.0&quot;&gt;&lt;title&gt;{title}&lt;/title&gt;&lt;link rel=&quot;stylesheet&quot; href=&quot;/static/css/style.css&quot;&gt;&lt;link rel=&quot;preconnect&quot; href=&quot;https://fonts.googleapis.com&quot;&gt;&lt;link rel=&quot;preconnect&quot; href=&quot;https://fonts.gstatic.com&quot; crossorigin&gt;&lt;link href=&quot;https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&amp;display=swap&quot; rel=&quot;stylesheet&quot;&gt;&lt;/head&gt;&lt;body&gt;&lt;header&gt;&lt;div class=&quot;logo&quot;&gt;&lt;img src=&quot;/static/img/logo.png&quot; alt=&quot;sIA Logo&quot;&gt;&lt;h1&gt;&lt;a href=&quot;/index.html&quot;&gt;sIA&lt;/a&gt;&lt;/h1&gt;&lt;/div&gt;&lt;nav&gt;&lt;ul&gt;&lt;li&gt;&lt;a href=&quot;#&quot;&gt;Noticias&lt;/a&gt;&lt;/li&gt;&lt;li&gt;&lt;a href=&quot;#&quot;&gt;Análisis&lt;/a&gt;&lt;/li&gt;&lt;li&gt;&lt;a href=&quot;#&quot;&gt;IA para Todos&lt;/a&gt;&lt;/li&gt;&lt;li&gt;&lt;a href=&quot;#&quot;&gt;Herramientas IA&lt;/a&gt;&lt;/li&gt;&lt;li&gt;&lt;a href=&quot;#&quot;&gt;Opinión&lt;/a&gt;&lt;/li&gt;&lt;/ul&gt;&lt;/nav&gt;&lt;a href=&quot;https://docs.google.com/forms/d/e/1FAIpQLSeNl4keU0p1eDMvzUpM5p57Naf5qBMsl5MSJNBMxPnWbofshQ/viewform?usp=header&quot; target=&quot;_blank&quot; class=&quot;subscribe-button&quot;&gt;Suscríbete&lt;/a&gt;&lt;/header&gt;"""
HTML\_FOOTER = """&lt;footer&gt;&lt;p&gt;© 2025 sIA. Todos los derechos reservados.&lt;/p&gt;&lt;p&gt;&lt;a href=&quot;/privacy.html&quot;&gt;Política de Privacidad&lt;/a&gt;&lt;/p&gt;&lt;/footer&gt;&lt;/body&gt;&lt;/html&gt;"""
PRIVACY\_POLICY\_CONTENT = """&lt;main class=&quot;article-body&quot; style=&quot;margin-top: 2rem;&quot;&gt;&lt;h1 class=&quot;article-title&quot;&gt;Política de Privacidad&lt;/h1&gt;&lt;div class=&quot;article-content&quot;&gt;&lt;p&gt;&lt;strong&gt;Fecha de vigencia:&lt;/strong&gt; 12 de agosto de 2025&lt;/p&gt;&lt;h2&gt;1. Introducción&lt;/h2&gt;&lt;p&gt;Bienvenido a sIA. Tu privacidad es de suma importancia para nosotros. Esta Política de Privacidad describe qué datos recopilamos, cómo los usamos, cómo los protegemos y qué opciones tienes sobre tus datos cuando visitas nuestro sitio web.&lt;/p&gt;&lt;h2&gt;2. Información que Recopilamos&lt;/h2&gt;&lt;ul&gt;&lt;li&gt;&lt;strong&gt;Información Personal:&lt;/strong&gt; Esto incluye información que nos proporcionas voluntariamente, como tu dirección de correo electrónico al suscribirte a nuestro boletín.&lt;/li&gt;&lt;li&gt;&lt;strong&gt;Información No Personal:&lt;/strong&gt; Recopilamos datos anónimos sobre tu visita (dirección IP, tipo de navegador, etc.) a través de cookies y servicios de análisis.&lt;/li&gt;&lt;/ul&gt;&lt;h2&gt;3. Uso de Cookies y Terceros&lt;/h2&gt;&lt;p&gt;Utilizamos cookies para mejorar la funcionalidad del sitio y personalizar tu experiencia. Somos participantes en el programa de publicidad de Google AdSense. Google, como proveedor externo, utiliza cookies para publicar anuncios. Puedes inhabilitar la publicidad personalizada en la &lt;a href=&quot;https://adssettings.google.com/authenticated&quot; target=&quot;_blank&quot;&gt;configuración de anuncios de Google&lt;/a&gt;.&lt;/p&gt;&lt;h2&gt;4. Tus Derechos&lt;/h2&gt;&lt;p&gt;Tienes derecho a acceder, rectificar o eliminar tu información personal. Para darte de baja de nuestro boletín, puedes seguir el enlace de "cancelar suscripción" que se incluirá en cada correo.&lt;/p&gt;&lt;h2&gt;5. Cambios a esta Política&lt;/h2&gt;&lt;p&gt;Podemos actualizar esta Política de Privacidad periódicamente. Te notificaremos cualquier cambio importante publicando la nueva política en nuestro sitio web.&lt;/p&gt;&lt;h2&gt;6. Contacto&lt;/h2&gt;&lt;p&gt;Si tienes alguna pregunta sobre esta Política, contáctanos a través de los medios disponibles en el sitio.&lt;/p&gt;&lt;/div&gt;&lt;/main&gt;"""

def generar\_contenido\_ia():
print("🤖 Generando contenido con la API de Groq...")
temas\_posibles = [
"el uso de IA para optimizar la red eléctrica en un país de LATAM",
"una nueva ley o regulación sobre ética y uso de IA en Chile o Colombia",
"cómo las startups de Agrotech en Argentina están usando IA para mejorar cosechas",
"el impacto de la IA en el sector bancario y fintech de Brasil",
"un proyecto ecológico en Perú que use IA para monitorear la deforestación del Amazonas",
"el rol de la IA en las campañas políticas o la administración pública en México",
"una colaboración entre una universidad de LATAM y una empresa internacional para investigar nuevos modelos de lenguaje",
"el avance de la IA en el sector de la salud y telemedicina en un país centroamericano",
"cómo la IA está ayudando a preservar lenguas indígenas o patrimonio cultural en la región"
]
tema\_elegido = random.choice(temas\_posibles)
print(f"✔️ Tema elegido para este post: '{tema\_elegido}'")
