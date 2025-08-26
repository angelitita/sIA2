# --- EJECUTANDO SCRIPT v20.4: MÁS VARIEDAD DE TEMAS ---
import os
import datetime
import json
from pathlib import Path
import sys
import random
import feedparser
from groq import Groq
from bs4 import BeautifulSoup

print("--- INICIANDO SCRIPT DE GENERACIÓN DE CONTENIDO v20.4 ---")

# --- CONFIGURACIÓN ---
CUSDIS_APP_ID = "f6cbff1c-928c-4ac4-b85a-c76024284179"
RSS_FEEDS = ["https://www.infobae.com/feeds/rss/america/tecno/", "https://es.wired.com/feed/rss", "https://www.xataka.com/tag/inteligencia-artificial/feed/"]
HISTORIAL_NOTICIAS_FILE = Path("historial_noticias.txt")
HISTORIAL_TITULOS_FILE = Path("historial_titulos.txt")
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

# --- LISTAS DE TEMAS (CON MÁS VARIEDAD) ---
temas_opinion = [
    "una columna de opinión sobre el Rabbit R1. ¿Es una revolución o un fracaso?",
    "un análisis crítico de las gafas Ray-Ban Meta. ¿Son realmente útiles en el día a día?",
    "una opinión sobre Suno AI para la creación de música. ¿Reemplazará a los músicos?",
    "una reseña del Humane AI Pin, explicando por qué ha sido tan controversial.",
    "¿Deberían las IAs tener derechos? Un debate ético.",
    "El futuro de los empleos en Latinoamérica con la llegada de la IA."
]
temas_herramientas = [
    "una comparativa detallada: Midjourney vs. Stable Diffusion para artistas digitales.",
    "una guía definitiva de las 5 mejores IAs para editar video en 2025.",
    "una reseña a fondo de Notion AI, con pros, contras y un caso de uso práctico.",
    "cómo usar herramientas de IA como Perplexity AI para mejorar la investigación.",
    "un tutorial sobre RunwayML para crear videos con inteligencia artificial.",
    "las mejores herramientas de IA para programadores: Copilot vs. Codeium."
]

# --- PLANTILLAS HTML ---
HTML_HEADER = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{title}</title>
<meta name="description" content="{summary}">
<link rel="stylesheet" href="/static/css/style.css"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet"><link rel="icon" href="/static/img/logo.png" type="image/png"></head><body>
<header>
    <div class="logo"><img src="/static/img/logo.png" alt="sIA Logo"><h1><a href="/index.html">sIA</a></h1></div>
    <nav class="desktop-nav"><ul><li><a href="/noticias.html">Noticias</a></li><li><a href="/herramientas-ia.html">Herramientas IA</a></li><li><a href="/opinion.html">Opinión</a></li></ul></nav>
    <a href="https://docs.google.com/forms/d/e/1FAIpQLSeNl4keU0p1eDMvzUpM5p57Naf5qBMsl5MSJNBMxPnWbofshQ/viewform?usp=header" target="_blank" class="subscribe-button desktop-nav">Suscríbete</a>
    <button class="hamburger-menu" aria-label="Abrir menú"><span></span></button>
</header>
<div class="mobile-nav"><nav><ul><li><a href="/noticias.html">Noticias</a></li><li><a href="/herramientas-ia.html">Herramientas IA</a></li><li><a href="/opinion.html">Opinión</a></li><li><a href="/acerca-de.html">Acerca de</a></li><li><a href="/contacto.html">Contacto</a></li></ul></nav><a href="https://docs.google.com/forms/d/e/1FAIpQLSeNl4keU0p1eDMvzUpM5p57Naf5qBMsl5MSJNBMxPnWbofshQ/viewform?usp=header" target="_blank" class="subscribe-button">Suscríbete</a></div>"""
HTML_FOOTER = """<footer><p>&copy; 2025 sIA. Todos los derechos reservados.</p><p><a href="/privacy.html">Política de Privacidad</a> | <a href="/acerca-de.html">Acerca de</a> | <a href="/contacto.html">Contacto</a></p></footer><script>const hamburger = document.querySelector('.hamburger-menu');const mobileNav = document.querySelector('.mobile-nav');const body = document.querySelector('body');hamburger.addEventListener('click', () => {hamburger.classList.toggle('is-active');mobileNav.classList.toggle('is-active');body.classList.toggle('no-scroll');});</script></body></html>"""
PRIVACY_POLICY_CONTENT = """<main class="article-body" style="margin-top: 2rem;"><h1 class="article-title">Política de Privacidad</h1><div class="article-content"><p><strong>Fecha de vigencia:</strong> 26 de agosto de 2025</p><p>En sIA ("nosotros", "nuestro"), respetamos su privacidad y nos comprometemos a protegerla...</p></div></main>"""
ACERCA_DE_CONTENT = """<main class="article-body" style="margin-top: 2rem;"><h1 class="article-title">Acerca de sIA</h1><div class="article-content"><h2>Nuestra Misión</h2><p>Nuestra misión es ser la fuente de información de referencia para entusiastas, profesionales y curiosos de la IA en Latinoamérica...</p></div></main>"""
CONTACTO_CONTENT = """<main class="article-body" style="margin-top: 2rem;"><h1 class="article-title">Contacto</h1><div class="article-content"><p>¿Tienes alguna pregunta, sugerencia o quieres colaborar? Utiliza el formulario a continuación.</p><form name="contact" method="POST" data-netlify="true" class="contact-form">...</form></div></main>"""

# --- LÓGICA DE CONTENIDO ---
def obtener_noticia_real_de_rss(historial_links):
    print("📡 Buscando noticias reales en RSS...")
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        if feed.entries:
            noticia = feed.entries[0]
            if noticia.link not in historial_links:
                print(f"✅ Noticia real encontrada: '{noticia.title}'")
                return {"titulo": noticia.title, "link": noticia.link, "resumen": BeautifulSoup(noticia.summary, "html.parser").get_text(separator=' ', strip=True)}
    return None

def generar_contenido_ia(categoria, tema, historial_titulos):
    print(f"🤖 Generando contenido IA para '{categoria}'...")
    system_prompt = f"Eres un experto en IA para el blog 'sIA'. Escribe un artículo de '{categoria}'. El artículo DEBE estar en español. Tu respuesta DEBE ser únicamente un objeto JSON válido."
    user_prompt = f"""Escribe un artículo sobre: '{tema}'. Formato JSON: {{"title": "...", "summary": "...", "content_html": "..."}}"""
    try:
        chat_completion = client_groq.chat.completions.create(messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], model="llama3-8b-8192", response_format={"type": "json_object"})
        contenido = json.loads(chat_completion.choices[0].message.content)
        if any(contenido['title'].lower() in t.lower() for t in historial_titulos):
            print(f"⚠️  Título potencialmente repetido, descartando: '{contenido['title']}'")
            return None
        contenido['category'] = categoria
        return contenido
    except Exception as e:
        print(f"⚠️  Error al generar contenido IA: {e}", file=sys.stderr)
        return None

def reescribir_noticia_con_ia(noticia, historial_titulos):
    print("🤖 Reescribiendo noticia real con IA...")
    system_prompt = "Eres un periodista para 'sIA'. Reescribe noticias en un artículo original y atractivo. DEBE estar en español."
    user_prompt = f"""Basado en: Título: "{noticia['titulo']}", Resumen: "{noticia['resumen']}", escribe un artículo. Formato JSON: {{"title": "...", "summary": "...", "content_html": "..."}}"""
    try:
        chat_completion = client_groq.chat.completions.create(messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], model="llama3-8b-8192", response_format={"type": "json_object"})
        contenido = json.loads(chat_completion.choices[0].message.content)
        if any(contenido['title'].lower() in t.lower() for t in historial_titulos):
            print(f"⚠️  Título potencialmente repetido, descartando: '{contenido['title']}'")
            return None
        contenido['source_link'] = noticia['link']
        contenido['category'] = "Noticias"
        return contenido
    except Exception as e:
        print(f"❌ Error al reescribir noticia: {e}", file=sys.stderr)
        return None

def leer_historial(archivo, max_lineas=50):
    if not archivo.exists(): return []
    with open(archivo, "r", encoding="utf-8") as f:
        lineas = [line.strip() for line in f.readlines()]
        return lineas[-max_lineas:]

def escribir_historial(archivo, nuevo_item, max_lineas=50):
    lineas = leer_historial(archivo, max_lineas -1)
    lineas.append(nuevo_item)
    with open(archivo, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas))

# --- FUNCIONES DE CREACIÓN DE PÁGINAS ---
def get_post_details(file_path):
    pass
def crear_archivo_post(contenido, todos_los_posts):
    pass
def actualizar_paginas(todos_los_posts):
    pass
def crear_pagina_privacidad():
    pass
def crear_pagina_acerca_de():
    pass
def crear_pagina_contacto():
    pass

if __name__ == "__main__":
    if not HISTORIAL_NOTICIAS_FILE.exists(): HISTORIAL_NOTICIAS_FILE.touch()
    if not HISTORIAL_TITULOS_FILE.exists(): HISTORIAL_TITULOS_FILE.touch()
    historial_links = leer_historial(HISTORIAL_NOTICIAS_FILE)
    historial_titulos = leer_historial(HISTORIAL_TITULOS_FILE)
    contenido_final = None

    noticia_real = obtener_noticia_real_de_rss(historial_links)
    if noticia_real:
        contenido_final = reescribir_noticia_con_ia(noticia_real, historial_titulos)
    else:
        print("ℹ️ No hubo noticias reales nuevas, se generará contenido IA.")
        opciones_ia = [("Opinión", temas_opinion), ("Herramientas IA", temas_herramientas)]
        random.shuffle(opciones_ia)
        for i, (categoria, temas) in enumerate(opciones_ia):
            print(f"✨ Intentando Plan {'A' if i == 0 else 'B'}: Generar '{categoria}'...")
            if temas:
                tema_elegido = random.choice(temas)
                contenido_final = generar_contenido_ia(categoria, tema_elegido, historial_titulos)
                if contenido_final:
                    break
    
    if contenido_final:
        posts_actuales = sorted(list(POSTS_DIR.glob("*.html")), key=lambda p: p.name, reverse=True)
        crear_archivo_post(contenido_final, posts_actuales)
        posts_actualizados = sorted(list(POSTS_DIR.glob("*.html")), key=lambda p: p.name, reverse=True)
        actualizar_paginas(posts_actualizados)
        crear_pagina_privacidad()
        crear_pagina_acerca_de()
        crear_pagina_contacto()
        print("\n🎉 ¡Proceso completado exitosamente!")
    else:
        print("\n❌ No se pudo generar contenido. La ejecución no fallará, pero no habrá post nuevo.", file=sys.stderr)
