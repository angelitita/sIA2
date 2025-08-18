# --- EJECUTANDO SCRIPT v17.2: VERSIÓN FINAL CON POLÍTICA DE PRIVACIDAD COMPLETA ---
import os
import datetime
import json
from pathlib import Path
import sys
import random
import feedparser
from groq import Groq
from bs4 import BeautifulSoup

print("--- INICIANDO SCRIPT DE GENERACIÓN DE CONTENIDO v17.2 ---")

# --- INTERRUPTOR DE REPARACIÓN ---
RECONSTRUIR_POSTS_ANTIGUOS = True

# --- CONFIGURACIÓN ---
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

# --- PLANTILLAS HTML ---
HTML_HEADER = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{title}</title><link rel="stylesheet" href="/static/css/style.css"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet"><link rel="icon" href="/static/img/logo.png" type="image/png"></head><body>
<header>
    <div class="logo"><img src="/static/img/logo.png" alt="sIA Logo"><h1><a href="/index.html">sIA</a></h1></div>
    <nav class="desktop-nav"><ul><li><a href="/noticias.html">Noticias</a></li><li><a href="/herramientas.html">Herramientas IA</a></li><li><a href="/opinion.html">Opinión</a></li></ul></nav>
    <a href="https://docs.google.com/forms/d/e/1FAIpQLSeNl4keU0p1eDMvzUpM5p57Naf5qBMsl5MSJNBMxPnWbofshQ/viewform?usp=header" target="_blank" class="subscribe-button desktop-nav">Suscríbete</a>
    <button class="hamburger-menu" aria-label="Abrir menú"><span></span></button>
</header>
<div class="mobile-nav"><nav><ul><li><a href="/noticias.html">Noticias</a></li><li><a href="/herramientas.html">Herramientas IA</a></li><li><a href="/opinion.html">Opinión</a></li></ul></nav><a href="https://docs.google.com/forms/d/e/1FAIpQLSeNl4keU0p1eDMvzUpM5p57Naf5qBMsl5MSJNBMxPnWbofshQ/viewform?usp=header" target="_blank" class="subscribe-button">Suscríbete</a></div>"""
HTML_FOOTER = """<footer><p>&copy; 2025 sIA. Todos los derechos reservados.</p><p><a href="/privacy.html">Política de Privacidad</a></p></footer><script>const hamburger = document.querySelector('.hamburger-menu');const mobileNav = document.querySelector('.mobile-nav');const body = document.querySelector('body');hamburger.addEventListener('click', () => {hamburger.classList.toggle('is-active');mobileNav.classList.toggle('is-active');body.classList.toggle('no-scroll');});</script></body></html>"""
# --- TEXTO DE POLÍTICA DE PRIVACIDAD RESTAURADO ---
PRIVACY_POLICY_CONTENT = """
<main class="article-body" style="margin-top: 2rem;">
    <h1 class="article-title">Política de Privacidad</h1>
    <div class="article-content">
        <p><strong>Fecha de vigencia:</strong> 18 de agosto de 2025</p>
        <h2>1. Introducción</h2>
        <p>Bienvenido a sIA. Tu privacidad es de suma importancia para nosotros. Esta Política de Privacidad describe qué datos recopilamos, cómo los usamos, cómo los protegemos y qué opciones tienes sobre tus datos cuando visitas nuestro sitio web.</p>
        <h2>2. Información que Recopilamos</h2>
        <ul>
            <li><strong>Información No Personal:</strong> Recopilamos datos anónimos sobre tu visita (como tipo de navegador, país de origen, etc.) a través de servicios de análisis web para entender mejor a nuestra audiencia. No recopilamos información personal identificable como nombres o correos electrónicos, a menos que te suscribas voluntariamente a nuestro boletín.</li>
        </ul>
        <h2>3. Uso de la Información</h2>
        <p>La información anónima recopilada se utiliza exclusivamente para mejorar el contenido y la experiencia de usuario en nuestro sitio web. Si te suscribes a nuestro boletín, tu correo electrónico se usará únicamente para enviarte nuevas publicaciones.</p>
        <h2>4. Cookies y Terceros</h2>
        <p>Utilizamos cookies para el funcionamiento básico del sitio. Podemos participar en programas de afiliados (como Amazon Afiliados) y redes publicitarias (como Google AdSense). Estos servicios de terceros pueden usar cookies para mostrar anuncios relevantes. Puedes gestionar tus preferencias de anuncios en la configuración de cada plataforma respectiva.</p>
        <h2>5. Comentarios</h2>
        <p>Nuestro sistema de comentarios es gestionado por un proveedor externo. Al comentar, puedes hacerlo de forma anónima o con un apodo. La información que proporciones en los comentarios es pública.</p>
        <h2>6. Tus Derechos</h2>
        <p>Tienes derecho a solicitar la eliminación de cualquier comentario que hayas publicado. Si estás suscrito a nuestro boletín, puedes cancelar tu suscripción en cualquier momento a través del enlace proporcionado en cada correo.</p>
        <h2>7. Cambios a esta Política</h2>
        <p>Podemos actualizar esta Política de Privacidad periódicamente. Te notificaremos cualquier cambio importante publicando la nueva política en nuestro sitio web.</p>
    </div>
</main>
"""

# --- LÓGICA DE CONTENIDO (sin cambios) ---
def obtener_noticia_real_de_rss():
    pass
def generar_contenido_ia(categoria, tema):
    pass
def reescribir_noticia_con_ia(noticia):
    pass
# ... (El resto de las funciones de lógica y creación de páginas no han cambiado)
def get_post_details(file_path):
    pass
def crear_archivo_post(contenido):
    pass
def actualizar_paginas(todos_los_posts):
    pass

def crear_pagina_privacidad():
    print("🔄 Creando página de Política de Privacidad...")
    full_html = HTML_HEADER.format(title="Política de Privacidad - sIA") + PRIVACY_POLICY_CONTENT + HTML_FOOTER
    with open(ROOT_DIR / "privacy.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print("✅ privacy.html creada/actualizada.")

def reparar_posts_antiguos(todos_los_posts):
    # ... (código de reparación sin cambios)
    pass

# --- BLOQUE DE EJECUCIÓN PRINCIPAL (sin cambios) ---
if __name__ == "__main__":
    if RECONSTRUIR_POSTS_ANTIGUOS:
        reparar_posts_antiguos(sorted(list(POSTS_DIR.glob("*.html")), key=lambda p: p.name, reverse=True))
    else:
        # Flujo normal de generación
        contenido_final = None
        noticia_real = obtener_noticia_real_de_rss()
        if noticia_real:
            contenido_final = reescribir_noticia_con_ia(noticia_real)
        else:
            print("ℹ️ No hubo noticias reales nuevas, se generará contenido IA.")
            categoria_ia, temas_ia = random.choice([("Opinión", temas_opinion), ("Herramientas IA", temas_herramientas)])
            tema_elegido = random.choice(temas_ia)
            if temas_ia: temas_ia.remove(tema_elegido)
            contenido_final = generar_contenido_ia(categoria_ia, tema_elegido)
        
        if contenido_final:
            crear_archivo_post(contenido_final)
        else:
            print("\n❌ No se pudo generar contenido. La ejecución fallará.", file=sys.stderr)
            sys.exit(1)
    
    posts_actualizados = sorted(list(POSTS_DIR.glob("*.html")), key=lambda p: p.name, reverse=True)
    actualizar_paginas(posts_actualizados)
    crear_pagina_privacidad() # Se asegura de que la página de privacidad siempre se actualice
    print("\n🎉 ¡Proceso completado exitosamente!")
