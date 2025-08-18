# --- EJECUTANDO SCRIPT v15.2: REPARADOR DE POSTS ANTIGUOS ---
import os
import datetime
import json
from pathlib import Path
import sys
import random
import feedparser
from groq import Groq
from bs4 import BeautifulSoup

print("--- INICIANDO SCRIPT DE GENERACIÓN DE CONTENIDO v15.2 ---")

# --- INTERRUPTOR DE REPARACIÓN ---
# PONER EN `True` UNA SOLA VEZ para reparar todos los posts antiguos.
# Después de una ejecución exitosa, VOLVER A PONER EN `False`.
RECONSTRUIR_POSTS_ANTIGUOS = True

# --- CONFIGURACIÓN (sin cambios) ---
RSS_FEEDS = ["https://www.infobae.com/feeds/rss/america/tecno/", "https://es.wired.com/feed/rss", "https://www.xataka.com/tag/inteligencia-artificial/feed/"]
HISTORIAL_FILE = Path("historial_noticias.txt")
try:
    api_key_main = os.getenv("GROQ_API_KEY")
    if not api_key_main: sys.exit("❌ Error: La variable GROQ_API_KEY no está configurada.")
    client_groq = Groq(api_key=api_key_main)
    print("✅ Cliente de Groq configurado.")
except Exception as e:
    sys.exit(f"❌ Error al configurar el cliente de Groq: {e}")
IMG_DIR = Path("static/img")
LISTA_DE_IMAGENES = []
try:
    extensions = ['.png', '.jpg', '.jpeg', '.webp']
    LISTA_DE_IMAGENES = [f.name for f in IMG_DIR.glob('*') if f.suffix.lower() in extensions and f.name != 'logo.png']
    if not LISTA_DE_IMAGENES: LISTA_DE_IMAGENES.append("logo.png")
except Exception as e:
    LISTA_DE_IMAGENES = ["logo.png"]
POSTS_DIR = Path("posts")
ROOT_DIR = Path(".")
temas_opinion = ["una columna de opinión sobre el Rabbit R1.", "un análisis crítico de las gafas Ray-Ban Meta.", "una opinión sobre Suno AI para la creación de música."]
temas_herramientas = ["una comparativa detallada: Midjourney vs. Stable Diffusion.", "una guía de las 5 mejores IAs para editar video.", "una reseña a fondo de Notion AI."]

# --- PLANTILLAS HTML (Menú final) ---
HTML_HEADER = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{title}</title><link rel="stylesheet" href="/static/css/style.css"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet"><link rel="icon" href="/static/img/logo.png" type="image/png"></head><body>
<header>
    <div class="logo"><img src="/static/img/logo.png" alt="sIA Logo"><h1><a href="/index.html">sIA</a></h1></div>
    <nav class="desktop-nav"><ul><li><a href="/noticias.html">Noticias</a></li><li><a href="/herramientas.html">Herramientas IA</a></li><li><a href="/opinion.html">Opinión</a></li></ul></nav>
    <a href="https://docs.google.com/forms/d/e/1FAIpQLSeNl4keU0p1eDMvzUpM5p57Naf5qBMsl5MSJNBMxPnWbofshQ/viewform?usp=header" target="_blank" class="subscribe-button desktop-nav">Suscríbete</a>
    <button class="hamburger-menu" aria-label="Abrir menú"><span></span></button>
</header>
<div class="mobile-nav"><nav><ul><li><a href="/noticias.html">Noticias</a></li><li><a href="/herramientas.html">Herramientas IA</a></li><li><a href="/opinion.html">Opinión</a></li></ul></nav><a href="https://docs.google.com/forms/d/e/1FAIpQLSeNl4keU0p1eDMvzUpM5p57Naf5qBMsl5MSJNBMxPnWbofshQ/viewform?usp=header" target="_blank" class="subscribe-button">Suscríbete</a></div>"""
HTML_FOOTER = """<footer><p>&copy; 2025 sIA. Todos los derechos reservados.</p><p><a href="/privacy.html">Política de Privacidad</a></p></footer><script>const hamburger = document.querySelector('.hamburger-menu');const mobileNav = document.querySelector('.mobile-nav');const body = document.querySelector('body');hamburger.addEventListener('click', () => {hamburger.classList.toggle('is-active');mobileNav.classList.toggle('is-active');body.classList.toggle('no-scroll');});</script></body></html>"""
PRIVACY_POLICY_CONTENT = """<main class="article-body" style="margin-top: 2rem;"><h1 class="article-title">Política de Privacidad</h1><div class="article-content"><p>Texto de la política de privacidad...</p></div></main>"""

# --- LÓGICA DE CONTENIDO Y CREACIÓN DE PÁGINAS (sin cambios) ---
def obtener_noticia_real_de_rss():
    # ... (código sin cambios)
    pass
def generar_contenido_ia(categoria, tema):
    # ... (código sin cambios)
    pass
def reescribir_noticia_con_ia(noticia):
    # ... (código sin cambios)
    pass
def get_post_details(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            title_tag = soup.find("h1", class_="article-title")
            title = title_tag.string.strip() if title_tag else "Sin Título"
            category_tag = soup.find("span", class_="category-tag")
            category = category_tag.string.strip() if category_tag else "Noticias"
            article_content_tag = soup.find("div", class_="article-content")
            article_content = str(article_content_tag) if article_content_tag else ""
            return title, category, article_content
    except Exception: return None, None, None
def crear_archivo_post(contenido):
    # ... (código sin cambios)
    pass
def actualizar_paginas(todos_los_posts):
    # ... (código sin cambios)
    pass
def crear_pagina_privacidad():
    # ... (código sin cambios)
    pass

# --- NUEVA FUNCIÓN DE REPARACIÓN ---
def reparar_posts_antiguos():
    print("🛠️ INICIANDO MODO REPARACIÓN DE POSTS ANTIGUOS...")
    posts_a_reparar = list(POSTS_DIR.glob("*.html"))
    if not posts_a_reparar:
        print("No se encontraron posts para reparar.")
        return

    for post_path in posts_a_reparar:
        print(f"Reparando: {post_path.name}")
        title, _, article_content_html = get_post_details(post_path)
        if title and article_content_html:
            # Reconstruye el post con el header y footer correctos
            repaired_content = f"""<div class="main-container"><main class="article-body">{article_content_html}</main></div>"""
            full_repaired_html = HTML_HEADER.format(title=title) + repaired_content + HTML_FOOTER
            with open(post_path, "w", encoding="utf-8") as f:
                f.write(full_repaired_html)
        else:
            print(f"⚠️  No se pudo reparar {post_path.name} (contenido no encontrado).")
    print("✅ REPARACIÓN COMPLETADA.")

# --- BLOQUE DE EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    if RECONSTRUIR_POSTS_ANTIGUOS:
        reparar_posts_antiguos()
        # Después de reparar, también actualizamos las páginas de categorías
        posts_actualizados = sorted(list(POSTS_DIR.glob("*.html")), key=lambda p: p.name, reverse=True)
        actualizar_paginas(posts_actualizados)
    else:
        # Flujo normal de generación de contenido
        contenido_final = None
        noticia_real = obtener_noticia_real_de_rss()
        if noticia_real:
            contenido_final = reescribir_noticia_con_ia(noticia_real)
        else:
            print("ℹ️ No hubo noticias reales nuevas, se generará contenido IA original.")
            categoria_ia, temas_ia = random.choice([("Opinión", temas_opinion), ("Herramientas IA", temas_herramientas)])
            tema_elegido = random.choice(temas_ia)
            contenido_final = generar_contenido_ia(categoria_ia, tema_elegido)
        
        if contenido_final:
            crear_archivo_post(contenido_final)
            posts_actualizados = sorted(list(POSTS_DIR.glob("*.html")), key=lambda p: p.name, reverse=True)
            actualizar_paginas(posts_actualizados)
            crear_pagina_privacidad()
            print("\n🎉 ¡Proceso completado exitosamente!")
        else:
            print("\n❌ No se pudo generar ni encontrar contenido. La ejecución fallará.", file=sys.stderr)
            sys.exit(1)
