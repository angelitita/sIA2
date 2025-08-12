print("--- EJECUTANDO SCRIPT v13: VERSIÓN FINAL ---")
import os
import datetime
import json
from pathlib import Path
import sys
from groq import Groq
import random

# --- CONFIGURACIÓN ---
# MODIFICA ESTA LISTA con los nombres de tus imágenes en static/img
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
HTML_FOOTER = """<footer><p>&copy; 2025 sIA. Todos los derechos reservados.</p><p><a href="#">Política de Privacidad</a></p></footer></body></html>"""

# --- FUNCIONES ---

def generar_contenido_ia():
    """Genera el contenido para un artículo usando Groq."""
    print("🤖 Actuando como periodista y generando nuevo contenido...")
    
    system_prompt = "Eres un periodista de tecnología para el portal de noticias 'sIA', especializado en el impacto de la Inteligencia Artificial en Latinoamérica. Tu respuesta debe ser EXCLUSIVAMENTE un objeto JSON válido, sin texto adicional."
    user_prompt = """
    Por favor, genera UN SOLO artículo de noticias sobre un tema de actualidad en IA relevante para Latinoamérica (ej. una nueva startup, una inversión importante, un avance tecnológico local, etc.).
    El artículo debe ser conciso, entre 350 y 550 palabras. El HTML debe ser simple, usando solo <p>, <h2> y <h3>.
    La estructura JSON debe ser:
    {
      "title": "Un titular de noticia real y atractivo",
      "summary": "Un resumen corto de 1-2 frases del artículo.",
      "category": "Noticias",
      "content_html": "El cuerpo completo del artículo en HTML.",
      "slug": "un-slug-para-la-url-basado-en-el-titulo"
    }
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            model="llama3-8b-8192", max_tokens=2048
        )
        response_content = chat_completion.choices[0].message.content
        contenido = json.loads(response_content)
        print(f"✅ Contenido generado con éxito: '{contenido['title']}'")
        return contenido
    except Exception as e:
        sys.exit(f"❌ Error al generar contenido con Groq: {e}")

def crear_archivo_post(contenido):
    POSTS_DIR.mkdir(exist_ok=True)
    fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
    
    article_content = f"""<article class="article-body"><h1 class="article-title">{contenido['title']}</h1><p class="article-meta">Publicado por Redacción sIA el {fecha_actual} en <span class="category-tag">{contenido['category']}</span></p><div class="article-content">{contenido['content_html']}</div></article>"""
    
    full_html = (
        HTML_HEADER.format(title=contenido['title'], css_path="../static/css/style.css", logo_path="../static/img/logo.jpg", index_path="../index.html") +
        article_content +
        HTML_FOOTER
    )
    
    nombre_archivo = f"{datetime.date.today().strftime('%Y-%m-%d')}-{contenido['slug']}.html"
    ruta_archivo = POSTS_DIR / nombre_archivo

    with open(ruta_archivo, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"📄 Archivo de post creado en: {ruta_archivo}")

def actualizar_index():
    print("🔄 Actualizando la página de inicio (index.html)...")
    posts = sorted(POSTS_DIR.glob("*.html"), key=os.path.getmtime, reverse=True)
    
    grid_html = ""
    for post_path in posts[:9]: # Cambiado a 9 para dejar espacio al nuevo
        try:
            with open(post_path, "r", encoding="utf-8") as f:
                # Extraer el título del HTML es complejo, usaremos el slug por ahora
                title_from_slug = post_path.stem[11:].replace("-", " ").title()
                imagen_aleatoria = random.choice(LISTA_DE_IMAGENES)
                ruta_imagen = f"static/img/{imagen_aleatoria}"
                card_html = f"""<article class="article-card"><a href="{post_path.as_posix()}"><img src="{ruta_imagen}" alt="Imagen del artículo"></a><div class="card-content"><span class="category-tag">Noticias</span><h3><a href="{post_path.as_posix()}">{title_from_slug}</a></h3></div></article>"""
                grid_html += card_html
        except Exception as e:
            print(f"No se pudo procesar el post {post_path}: {e}")


    hero_html = ""
    if posts:
        try:
            with open(posts[0], "r", encoding="utf-8") as f:
                hero_title = posts[0].stem[11:].replace("-", " ").title()
                hero_html = f"""<section class="hero-article"><h2><a href="{posts[0].as_posix()}">{hero_title}</a></h2><p>Este es el artículo más reciente generado por nuestra IA.</p></section>"""
        except Exception as e:
            print(f"No se pudo procesar el post héroe {posts[0]}: {e}")

    index_main_content = f"""<main>{hero_html}<div class="content-area"><div class="article-grid">{grid_html}</div><aside class="sidebar"><div class="widget"><h3>Lo Más Leído</h3></div><div class="widget"><h3>Herramientas IA Destacadas</h3></div></aside></div></main>"""
    
    full_html = (
        HTML_HEADER.format(title="sIA - Inteligencia Artificial en Latinoamérica", css_path="static/css/style.css", logo_path="static/img/logo.jpg", index_path="index.html") +
        index_main_content +
        HTML_FOOTER
    )

    with open(ROOT_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"✅ index.html actualizado. Tamaño: {os.path.getsize(ROOT_DIR / 'index.html') / 1024:.2f} KB")

# --- Ejecución Principal ---
if __name__ == "__main__":
    contenido_nuevo = generar_contenido_ia()
    if contenido_nuevo:
        crear_archivo_post(contenido_nuevo)
        actualizar_index()
        print("\n🎉 ¡Proceso completado!")
