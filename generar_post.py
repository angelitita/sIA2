print("--- EJECUTANDO SCRIPT v18: DIAGNÓSTICO FINAL ---")
import os
import datetime
import json
from pathlib import Path
import sys
from groq import Groq
import random
from bs4 import BeautifulSoup

# --- CONFIGURACIÓN ---
LISTA_DE_IMAGENES = ["imagen-1.jpg", "imagen-2.jpg", "imagen-3.jpg", "imagen-4.jpg", "imagen-5.jpg", "imagen-6.jpg", "imagen-8.jpg", "imagen-9.jpg", "imagen-10.jpg", "imagen-11.jpg"]

try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    print("✅ Cliente de Groq configurado.")
except Exception as e:
    sys.exit(f"❌ Error al configurar el cliente de Groq: {e}")

POSTS_DIR = Path("posts")
ROOT_DIR = Path(".")

# --- PLANTILLAS HTML (reducidas para claridad) ---
HTML_HEADER = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{title}</title><link rel="stylesheet" href="{css_path}"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet"></head><body><header><div class="logo"><img src="{logo_path}" alt="sIA Logo"><h1><a href="{index_path}">sIA</a></h1></div><nav><ul><li><a href="#">Noticias</a></li><li><a href="#">Análisis</a></li><li><a href="#">IA para Todos</a></li><li><a href="#">Herramientas IA</a></li><li><a href="#">Opinión</a></li></ul></nav><a href="https://docs.google.com/forms/d/e/1FAIpQLSeNl4keU0p1eDMvzUpM5p57Naf5qBMsl5MSJNBMxPnWbofshQ/viewform?usp=header" target="_blank" class="subscribe-button">Suscríbete</a></header>"""
HTML_FOOTER = """<footer><p>&copy; 2025 sIA. Todos los derechos reservados.</p><p><a href="/privacy.html">Política de Privacidad</a></p></footer></body></html>"""
PRIVACY_POLICY_CONTENT = """<main class="article-body" style="margin-top: 2rem;"><h1 class="article-title">Política de Privacidad</h1><div class="article-content"><p><strong>Fecha de vigencia:</strong> 12 de agosto de 2025</p><p>Bienvenido a sIA. Tu privacidad es de suma importancia para nosotros. Esta Política de Privacidad describe qué datos recopilamos y cómo los usamos.</p></div></main>"""

# --- FUNCIONES ---

def generar_contenido_ia():
    print("🤖 Generando contenido con la API de Groq...")
    system_prompt = "Eres un periodista de tecnología para 'sIA'. Tu respuesta DEBE ser únicamente un objeto JSON válido."
    user_prompt = """Genera UN artículo de noticias sobre un tema de actualidad en IA relevante para Latinoamérica. Usa esta estructura JSON: {"title": "Un titular real","summary": "Un resumen corto.","category": "Noticias","content_html": "El cuerpo del artículo en HTML.","slug": "un-slug-relevante"}"""
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            model="llama3-8b-8192", max_tokens=2048, response_format={"type": "json_object"}
        )
        response_content = chat_completion.choices[0].message.content
        
        # --- Punto de control 1: Ver la respuesta cruda de la IA ---
        print(f"✔️ Respuesta recibida de la API. Verificando contenido...")
        print(f"RAW_RESPONSE: {response_content}")

        if not response_content or not response_content.strip().startswith("{"):
            sys.exit("❌ ERROR: La respuesta de la IA está vacía o no es un JSON.")
        
        contenido = json.loads(response_content)
        
        # --- Punto de control 2: Verificar campos necesarios ---
        required_keys = ["title", "content_html", "slug"]
        if not all(k in contenido for k in required_keys):
             sys.exit(f"❌ ERROR: El JSON de la IA no contiene los campos requeridos. Faltan: {[k for k in required_keys if k not in contenido]}")

        if not contenido["title"] or not contenido["content_html"]:
            sys.exit("❌ ERROR: El título o el contenido del artículo están vacíos en la respuesta de la IA.")

        contenido['slug'] = f"{contenido['slug']}-{datetime.datetime.now().strftime('%H%M%S')}"
        print(f"✅ Contenido generado y validado con éxito: '{contenido['title']}'")
        return contenido
        
    except Exception as e:
        sys.exit(f"❌ Error crítico al generar o validar contenido con Groq: {e}")

def crear_archivo_post(contenido):
    POSTS_DIR.mkdir(exist_ok=True)
    fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
    article_content = f"""<article class="article-body"><h1 class="article-title">{contenido['title']}</h1><p class="article-meta">Publicado por Redacción sIA el {fecha_actual} en <span class="category-tag">{contenido['category']}</span></p><div class="article-content">{contenido['content_html']}</div></article>"""
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
    except Exception: return None

def actualizar_index():
    print("🔄 Actualizando la página de inicio (index.html)...")
    posts = sorted(POSTS_DIR.glob("*.html"), key=os.path.getmtime, reverse=True)
    grid_html = ""
    if not LISTA_DE_IMAGENES: LISTA_DE_IMAGENES.append("placeholder.png")

    for post_path in posts[:9]:
        title = get_title_from_html(post_path)
        if not title: continue
        imagen_aleatoria = random.choice(LISTA_DE_IMAGENES)
        ruta_imagen = f"static/img/{imagen_aleatoria}"
        card_html = f"""<article class="article-card"><a href="{post_path.as_posix()}"><img src="{ruta_imagen}" alt="Imagen del artículo"></a><div class="card-content"><span class="category-tag">Noticias</span><h3><a href="{post_path.as_posix()}">{title}</a></h3></div></article>"""
        grid_html += card_html

    hero_html = ""
    if posts:
        hero_title = get_title_from_html(posts[0])
        if hero_title: hero_html = f"""<section class="hero-article"><h2><a href="{posts[0].as_posix()}">{hero_title}</a></h2><p>Este es el artículo más reciente publicado.</p></section>"""

    index_main_content = f"""<main>{hero_html}<div class="content-area"><div class="article-grid">{grid_html}</div><aside class="sidebar"><div class="widget"><h3>Lo Más Leído</h3></div><div class="widget"><h3>Herramientas IA Destacadas</h3></div></aside></div></main>"""
    full_html = (HTML_HEADER.format(title="sIA - Inteligencia Artificial en Latinoamérica", css_path="static/css/style.css", logo_path="static/img/logo.png", index_path="index.html") + index_main_content + HTML_FOOTER)
    with open(ROOT_DIR / "index.html", "w", encoding="utf-8") as f: f.write(full_html)
    print(f"✅ index.html actualizado.")

def crear_pagina_privacidad():
    print("🔄 Creando/Actualizando la página de Política de Privacidad...")
    full_html = (HTML_HEADER.format(title="Política de Privacidad - sIA", css_path="/static/css/style.css", logo_path="/static/img/logo.png", index_path="/index.html") + PRIVACY_POLICY_CONTENT + HTML_FOOTER)
    with open(ROOT_DIR / "privacy.html", "w", encoding="utf-8") as f: f.write(full_html)
    print("✅ privacy.html creada.")

# --- Ejecución Principal ---
if __name__ == "__main__":
    try: from bs4 import BeautifulSoup
    except ImportError:
        os.system(f"{sys.executable} -m pip install beautifulsoup4")
        from bs4 import BeautifulSoup

    contenido_nuevo = generar_contenido_ia()
    
    # --- Punto de control 3: Asegurarse de que el contenido no sea nulo ---
    if not contenido_nuevo:
        sys.exit("❌ ERROR: La función de generación de contenido devolvió 'None'. El proceso no puede continuar.")
    
    crear_archivo_post(contenido_nuevo)
    actualizar_index()
    crear_pagina_privacidad()
    print("\n🎉 ¡Proceso completado!")
