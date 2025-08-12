print("--- EJECUTANDO SCRIPT v16: LIMPIEZA DE JSON ---")
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
    "imagen-1.jpg",
    "imagen-2.jpg",
    "imagen-3.jpg"
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

# --- FUNCIONES ---

def generar_contenido_ia():
    print("🤖 Actuando como periodista y generando nuevo contenido...")
    system_prompt = "Eres un periodista de tecnología para el portal 'sIA', especializado en IA en Latinoamérica. Tu respuesta DEBE ser únicamente un objeto JSON válido envuelto en un bloque de código markdown ```json ... ```."
    user_prompt = """
    Genera UN artículo de noticias sobre un tema de actualidad en IA relevante para Latinoamérica.
    El artículo debe ser conciso (350-550 palabras) y el HTML debe usar <p>, <h2> y <h3>. NO incluyas imágenes.
    La estructura JSON debe ser:
    {"title": "Un titular de noticia real y atractivo","summary": "Un resumen corto del artículo.","category": "Noticias","content_html": "El cuerpo del artículo en HTML.","slug": "un-slug-para-la-url-basado-en-el-titulo"}
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            model="llama3-8b-8192", max_tokens=2048,
            # Asegurar que la respuesta sea JSON
            response_format={"type": "json_object"},
        )
        response_content = chat_completion.choices[0].message.content
        
        # --- LÓGICA DE LIMPIEZA DE JSON ---
        print("⚙️ Limpiando la respuesta de la IA...")
        # A veces la IA envuelve la respuesta en markdown, lo eliminamos.
        cleaned_json_str = response_content.strip().replace("```json", "").replace("```", "").strip()
        
        contenido = json.loads(cleaned_json_str)
        contenido['slug'] = f"{contenido['slug']}-{datetime.datetime.now().strftime('%H-%M-%S')}"
        print(f"✅ Contenido generado y limpiado con éxito: '{contenido['title']}'")
        return contenido
    except Exception as e:
        # Imprime el contenido problemático si falla el JSON
        print(f"❗️ Contenido recibido de la IA que causó el error: {response_content}")
        sys.exit(f"❌ Error al procesar el JSON de Groq: {e}")

def crear_archivo_post(contenido):
    POSTS_DIR.mkdir(exist_ok=True)
    fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
    
    article_content = f"""<article class="article-body"><h1 class="article-title">{contenido['title']}</h1><p class="article-meta">Publicado por Redacción sIA el {fecha_actual} en <span class="category-tag">{contenido['category']}</span></p><div class="article-content">{contenido['content_html']}</div></article>"""
    
    full_html = (
        HTML_HEADER.format(title=contenido['title'], css_path="../static/css/style.css", logo_path="../static/img/logo.png", index_path="../index.html") +
        article_content +
        HTML_FOOTER
    )
    
    nombre_archivo = f"{datetime.date.today().strftime('%Y-%m-%d')}-{contenido['slug']}.html"
    ruta_archivo = POSTS_DIR / nombre_archivo

    with open(ruta_archivo, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"📄 Archivo de post creado en: {ruta_archivo}")

def get_title_from_html(file_path):
    """Extrae el título H1 de un archivo HTML."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            title_tag = soup.find("h1", class_="article-title")
            return title_tag.string if title_tag else "Título no encontrado"
    except Exception:
        return file_path.stem[11:].replace("-", " ").title()

def actualizar_index():
    print("🔄 Actualizando la página de inicio (index.html)...")
    posts = sorted(POSTS_DIR.glob("*.html"), key=os.path.getmtime, reverse=True)
    
    grid_html = ""
    if not LISTA_DE_IMAGENES:
        LISTA_DE_IMAGENES.append("placeholder.png")

    for post_path in posts[:9]:
        title = get_title_from_html(post_path)
        imagen_aleatoria = random.choice(LISTA_DE_IMAGENES)
        ruta_imagen = f"static/img/{imagen_aleatoria}"
        card_html = f"""<article class="article-card"><a href="{post_path.as_posix()}"><img src="{ruta_imagen}" alt="Imagen del artículo"></a><div class="card-content"><span class="category-tag">Noticias</span><h3><a href="{post_path.as_posix()}">{title}</a></h3></div></article>"""
        grid_html += card_html

    hero_html = ""
    if posts:
        hero_title = get_title_from_html(posts[0])
        hero_html = f"""<section class="hero-article"><h2><a href="{posts[0].as_posix()}">{hero_title}</a></h2><p>Este es el artículo más reciente publicado.</p></section>"""

    index_main_content = f"""<main>{hero_html}<div class="content-area"><div class="article-grid">{grid_html}</div><aside class="sidebar"><div class="widget"><h3>Lo Más Leído</h3></div><div class="widget"><h3>Herramientas IA Destacadas</h3></div></aside></div></main>"""
    
    full_html = (
        HTML_HEADER.format(title="sIA - Inteligencia Artificial en Latinoamérica", css_path="static/css/style.css", logo_path="static/img/logo.png", index_path="index.html") +
        index_main_content +
        HTML_FOOTER
    )

    with open(ROOT_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"✅ index.html actualizado. Tamaño: {os.path.getsize(ROOT_DIR / 'index.html') / 1024:.2f} KB")

# --- Ejecución Principal ---
if __name__ == "__main__":
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("Instalando BeautifulSoup...")
        os.system(f"{sys.executable} -m pip install beautifulsoup4")
        from bs4 import BeautifulSoup

    contenido_nuevo = generar_contenido_ia()
    if contenido_nuevo:
        crear_archivo_post(contenido_nuevo)
        actualizar_index()
        print("\n🎉 ¡Proceso completado!")
