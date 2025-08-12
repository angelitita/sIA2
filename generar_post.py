print("--- EJECUTANDO SCRIPT v17.3: CORRECCIÓN DE PARÉNTESIS ---")
import os
import datetime
import json
from pathlib import Path
import sys
from groq import Groq
import random
from bs4 import BeautifulSoup

# --- CONFIGURACIÓN ---
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
HTML_FOOTER = """<footer><p>&copy; 2025 sIA. Todos los derechos reservados.</p><p><a href="/privacy.html">Política de Privacidad</a></p></footer></body></html>"""
PRIVACY_POLICY_CONTENT = """<main class="article-body" style="margin-top: 2rem;"><h1 class="article-title">Política de Privacidad</h1><div class="article-content"><p><strong>Fecha de vigencia:</strong> 12 de agosto de 2025</p><h2>Introducción</h2><p>Bienvenido a sIA. Tu privacidad es de suma importancia para nosotros. Esta Política de Privacidad describe qué datos recopilamos, cómo los usamos y qué opciones tienes sobre tus datos cuando visitas nuestro sitio web.</p><h2>Información que Recopilamos</h2><ul><li><strong>Información Personal:</strong> Se refiere a la información que nos proporcionas voluntariamente, como tu dirección de correo electrónico cuando te suscribes a nuestro boletín a través de nuestro formulario de Google.</li><li><strong>Información No Personal:</strong> Recopilamos datos anónimos sobre tu visita, como tu dirección IP, tipo de navegador y páginas visitadas a través de cookies y servicios de análisis.</li></ul><h2>Uso de Cookies y Publicidad</h2><p>Somos participantes en el programa de publicidad de Google AdSense. Google, como proveedor externo, utiliza cookies para publicar anuncios en nuestro sitio. Puedes inhabilitar la publicidad personalizada en la <a href="https://adssettings.google.com/authenticated" target="_blank">configuración de anuncios de Google</a>.</p><h2>Tus Derechos</h2><p>Tienes derecho a acceder, rectificar o eliminar tu información personal. Para darte de baja de nuestro boletín, puedes seguir el enlace de "cancelar suscripción" que se incluirá en cada correo electrónico.</p></div></main>"""

# --- FUNCIONES ---

def generar_contenido_ia():
    print("🤖 Generando contenido con la API de Groq...")
    system_prompt = "Eres un periodista de tecnología para 'sIA', especializado en IA en Latinoamérica. Tu respuesta DEBE ser únicamente un objeto JSON válido."
    user_prompt = """Genera UN artículo de noticias sobre un tema de actualidad en IA relevante para Latinoamérica. El artículo debe ser conciso (350-550 palabras) y el HTML debe usar <p>, <h2> y <h3>. El slug debe ser único y relevante. Usa esta estructura JSON: {"title": "Un titular de noticia real y atractivo","summary": "Un resumen corto del artículo.","category": "Noticias","content_html": "El cuerpo del artículo en HTML.","slug": "un-slug-para-la-url-basado-en-el-titulo"}"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            model="llama3-8b-8192", max_tokens=2048, response_format={"type": "json_object"}
        )
        response_content = chat_completion.choices[0].message.content
        contenido = json.loads(response_content)
        if not all(k in contenido for k in ["title", "content_html", "slug"]):
             raise ValueError("El JSON recibido de la IA no tiene los campos requeridos.")
        contenido['slug'] = f"{contenido['slug']}-{datetime.datetime.now().strftime('%H%M%S')}"
        print(f"✅ Contenido generado con éxito: '{contenido['title']}'")
        return contenido
    except Exception as e:
        sys.exit(f"❌ Error crítico al generar o validar contenido con Groq: {e}")

def crear_archivo_post(contenido):
    POSTS_DIR.mkdir(exist_ok=True)
    fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
    article_content = f"""<article class="article-body"><h1 class="article-title">{contenido['title']}</h1><p class="article-meta">Publicado por Redacción sIA el {fecha_actual} en <span class="category-tag">{contenido['category']}</span></p><div class="article-content">{contenido['content_html']}</div></article>"""
    # CORRECCIÓN: Faltaba un paréntesis de cierre en la siguiente línea
    full_html = (HTML_HEADER.format(title=contenido['title'], css_path="../static/css/style.css", logo_path="../static/img/logo.png", index_path="../index.html") + article_content + HTML_FOOTER)
    nombre_archivo = f"{datetime.date.today().strftime('%Y-%m-%d')}-{contenido['slug']}.html"
    ruta_archivo = POSTS_DIR / nombre_archivo
    with open(ruta_archivo, "w", encoding="utf-8") as f: f.write(full_html)
    print(f"📄 Archivo de post creado en: {ruta_archivo}")

def get_title_from_html(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            title_tag = soup.find("h1", class_="article-title")
            return title_tag.string.strip() if title_tag and title_tag.string else None
    except Exception:
        return None

def actualizar_index():
    print("🔄 Actualizando la página de inicio (index.html)...")
    posts = sorted
