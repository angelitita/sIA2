# --- EJECUTANDO SCRIPT v19.2: PÁGINAS DE ACERCA DE Y CONTACTO ---
import os
import datetime
import json
from pathlib import Path
import sys
import random
import feedparser
from groq import Groq
from bs4 import BeautifulSoup

print("--- INICIANDO SCRIPT DE GENERACIÓN DE CONTENIDO v19.2 ---")

# --- CONFIGURACIÓN ---
CUSDIS_APP_ID = "f6cbff1c-928c-4ac4-b85a-c76024284179"
RSS_FEEDS = ["https://www.infobae.com/feeds/rss/america/tecno/", "https://es.wired.com/feed/rss", "https://www.xataka.com/tag/inteligencia-artificial/feed/"]
HISTORIAL_FILE = Path("historial_noticias.txt")
try:
    api_key_main = os.getenv("GROQ_API_KEY")
    if not api_key_main: sys.exit("❌ Error: GROQ_API_KEY no configurada.")
    client_groq = Groq(api_key=api_key_main)
    print("✅ Cliente de Groq configurado.")
except Exception as e:
    sys.exit(f"❌ Error al configurar cliente de Groq: {e}")

IMG_DIR = Path("static/img")
LISTA_DE_IMAGENES = []
try:
    extensions = ['.png', '.jpg', '.jpeg', '.webp']
    LISTA_DE_IMAGENES = [f.name for f in IMG_DIR.glob('*') if f.suffix.lower() in extensions and f.name != 'logo.png']
    if not LISTA_DE_IMAGENES: LISTA_DE_IMAGENES.append("logo.png")
except Exception:
    LISTA_DE_IMAGENES = ["logo.png"]
POSTS_DIR = Path("posts")
ROOT_DIR = Path(".")

temas_opinion = ["una columna de opinión sobre el Rabbit R1.", "un análisis crítico de las gafas Ray-Ban Meta.", "una opinión sobre Suno AI."]
temas_herramientas = ["una comparativa detallada: Midjourney vs. Stable Diffusion.", "una guía de las 5 mejores IAs para editar video.", "una reseña a fondo de Notion AI."]

# --- PLANTILLAS HTML (CON NUEVOS ENLACES) ---
HTML_HEADER = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{title}</title>
<meta name="description" content="{summary}">
<link rel="stylesheet" href="/static/css/style.css"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet"><link rel="icon" href="/static/img/logo.png" type="image/png"></head><body>
<header>
    <div class="logo"><img src="/static/img/logo.png" alt="sIA Logo"><h1><a href="/index.html">sIA</a></h1></div>
    <nav class="desktop-nav"><ul><li><a href="/noticias.html">Noticias</a></li><li><a href="/herramientas-ia.html">Herramientas IA</a></li><li><a href="/opinion.html">Opinión</a></li><li><a href="/acerca-de.html">Acerca de</a></li><li><a href="/contacto.html">Contacto</a></li></ul></nav>
    <a href="https://docs.google.com/forms/d/e/1FAIpQLSeNl4keU0p1eDMvzUpM5p57Naf5qBMsl5MSJNBMxPnWbofshQ/viewform?usp=header" target="_blank" class="subscribe-button desktop-nav">Suscríbete</a>
    <button class="hamburger-menu" aria-label="Abrir menú"><span></span></button>
</header>
<div class="mobile-nav"><nav><ul><li><a href="/noticias.html">Noticias</a></li><li><a href="/herramientas-ia.html">Herramientas IA</a></li><li><a href="/opinion.html">Opinión</a></li><li><a href="/acerca-de.html">Acerca de</a></li><li><a href="/contacto.html">Contacto</a></li></ul></nav><a href="https://docs.google.com/forms/d/e/1FAIpQLSeNl4keU0p1eDMvzUpM5p57Naf5qBMsl5MSJNBMxPnWbofshQ/viewform?usp=header" target="_blank" class="subscribe-button">Suscríbete</a></div>"""
HTML_FOOTER = """<footer><p>&copy; 2025 sIA. Todos los derechos reservados.</p><p><a href="/privacy.html">Política de Privacidad</a> | <a href="/acerca-de.html">Acerca de</a> | <a href="/contacto.html">Contacto</a></p></footer><script>const hamburger = document.querySelector('.hamburger-menu');const mobileNav = document.querySelector('.mobile-nav');const body = document.querySelector('body');hamburger.addEventListener('click', () => {hamburger.classList.toggle('is-active');mobileNav.classList.toggle('is-active');body.classList.toggle('no-scroll');});</script></body></html>"""
PRIVACY_POLICY_CONTENT = """<main class="article-body" style="margin-top: 2rem;"><h1 class="article-title">Política de Privacidad</h1><div class="article-content"><p><strong>Fecha de vigencia:</strong> 22 de agosto de 2025</p><h2>1. Introducción</h2><p>Bienvenido a sIA. Tu privacidad es de suma importancia para nosotros...</p></div></main>"""

# --- NUEVO: CONTENIDO PÁGINA ACERCA DE ---
ACERCA_DE_CONTENT = """
<main class="article-body" style="margin-top: 2rem;">
    <h1 class="article-title">Acerca de sIA</h1>
    <div class="article-content">
        <p><strong>sIA - Inteligencia Artificial en Latinoamérica</strong> es un portal de noticias y análisis dedicado a explorar y difundir los avances, innovaciones y debates en torno a la inteligencia artificial en nuestra región.</p>
        <h2>Nuestra Misión</h2>
        <p>Nuestra misión es ser la fuente de información de referencia para entusiastas, profesionales y curiosos de la IA en Latinoamérica. Creemos en el poder de la información para educar, inspirar y fomentar el desarrollo tecnológico responsable. A través de un sistema de curación y generación de contenido automatizado, buscamos mantener a nuestra audiencia al día sobre las últimas tendencias, herramientas y debates éticos que moldean el futuro de la inteligencia artificial.</p>
        <h2>¿Cómo funciona este sitio?</h2>
        <p>Este sitio utiliza un sistema automatizado que combina la lectura de fuentes de noticias de alta calidad (vía RSS) con modelos de lenguaje avanzados (LLMs) para reescribir y generar contenido relevante. Esto nos permite mantener un flujo constante de información, cubriendo desde las últimas noticias hasta artículos de opinión y reseñas de herramientas, asegurando que nuestra comunidad siempre tenga algo nuevo que leer y aprender.</p>
    </div>
</main>
"""

# --- NUEVO: CONTENIDO PÁGINA CONTACTO ---
CONTACTO_CONTENT = """
<main class="article-body" style="margin-top: 2rem;">
    <h1 class="article-title">Contacto</h1>
    <div class="article-content">
        <p>¿Tienes alguna pregunta, sugerencia o quieres colaborar? Nos encantaría saber de ti. Puedes usar el formulario a continuación para enviarnos un mensaje directamente a nuestro correo.</p>
        
        <form name="contact" method="POST" data-netlify="true" class="contact-form">
            <div class="form-group">
                <label for="name">Nombre:</label>
                <input type="text" id="name" name="name" required>
            </div>
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="message">Mensaje:</label>
                <textarea id="message" name="message" rows="6" required></textarea>
            </div>
            <button type="submit" class="subscribe-button">Enviar Mensaje</button>
        </form>

        <h2>Otras formas de contactar</h2>
        <p>También puedes encontrarnos y seguir nuestras actualizaciones en Twitter:</p>
        <p><a href="https://x.com/sIAnoticiastec" target="_blank" rel="noopener noreferrer"><strong>@sIAnoticiastec</strong></a></p>
    </div>
</main>
"""

# ... (El resto de las funciones de lógica y creación de páginas no han cambiado)
def obtener_noticia_real_de_rss():
    # ...
    pass
def generar_contenido_ia(categoria, tema):
    # ...
    pass
def reescribir_noticia_con_ia(noticia):
    # ...
    pass
def get_post_details(file_path):
    # ...
    pass
def crear_archivo_post(contenido, todos_los_posts):
    # ...
    pass
def actualizar_paginas(todos_los_posts):
    # ...
    pass
def crear_pagina_privacidad():
    full_html = HTML_HEADER.format(title="Política de Privacidad - sIA", summary="Política de Privacidad de sIA News.") + PRIVACY_POLICY_CONTENT + HTML_FOOTER
    with open(ROOT_DIR / "privacy.html", "w", encoding="utf-8") as f: f.write(full_html)
    print("✅ privacy.html creada/actualizada.")

# --- NUEVO: FUNCIONES PARA CREAR LAS NUEVAS PÁGINAS ---
def crear_pagina_acerca_de():
    full_html = HTML_HEADER.format(title="Acerca de - sIA", summary="Descubre la misión y el funcionamiento de sIA News.") + ACERCA_DE_CONTENT + HTML_FOOTER
    with open(ROOT_DIR / "acerca-de.html", "w", encoding="utf-8") as f: f.write(full_html)
    print("✅ acerca-de.html creada/actualizada.")

def crear_pagina_contacto():
    full_html = HTML_HEADER.format(title="Contacto - sIA", summary="Contacta con el equipo de sIA News.") + CONTACTO_CONTENT + HTML_FOOTER
    with open(ROOT_DIR / "contacto.html", "w", encoding="utf-8") as f: f.write(full_html)
    print("✅ contacto.html creada/actualizada.")

if __name__ == "__main__":
    # ... (Flujo normal de generación)
    contenido_final = None
    noticia_real = obtener_noticia_real_de_rss()
    if noticia_real:
        contenido_final = reescribir_noticia_con_ia(noticia_real)
    else:
        print("ℹ️ No hubo noticias reales nuevas, se generará contenido IA original.")
        categoria_ia, temas_ia = random.choice([("Opinión", temas_opinion), ("Herramientas IA", temas_herramientas)])
        tema_elegido = random.choice(temas_ia)
        if temas_ia: temas_ia.remove(tema_elegido)
        contenido_final = generar_contenido_ia(categoria_ia, tema_elegido)
    
    if contenido_final:
        posts_actuales = sorted(list(POSTS_DIR.glob("*.html")), key=lambda p: p.name, reverse=True)
        crear_archivo_post(contenido_final, posts_actuales)
    else:
        print("\n❌ No se pudo generar contenido. La ejecución fallará.", file=sys.stderr)
        sys.exit(1)
    
    posts_actualizados = sorted(list(POSTS_DIR.glob("*.html")), key=lambda p: p.name, reverse=True)
    actualizar_paginas(posts_actualizados)
    crear_pagina_privacidad()
    # --- NUEVO: Se añaden las llamadas para crear las nuevas páginas ---
    crear_pagina_acerca_de()
    crear_pagina_contacto()
    print("\n🎉 ¡Proceso completado exitosamente!")
