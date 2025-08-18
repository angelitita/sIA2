# --- EJECUTANDO SCRIPT v14.0: LECTOR DE NOTICIAS REALES AUTOMÁTICO ---
import os
import datetime
import json
from pathlib import Path
import sys
import random
import feedparser
from groq import Groq
from bs4 import BeautifulSoup

print("--- INICIANDO SCRIPT DE GENERACIÓN DE CONTENIDO v14.0 ---")

# --- CONFIGURACIÓN DE RSS FEEDS ---
# Lista de canales de noticias que el script revisará.
RSS_FEEDS = [
    "https://www.infobae.com/feeds/rss/america/tecno/",
    "https://es.wired.com/feed/rss",
    "https://www.xataka.com/tag/inteligencia-artificial/feed/",
    # Puedes añadir más feeds de noticias de tecnología en español aquí
]
HISTORIAL_FILE = Path("historial_noticias.txt")

# --- CONFIGURACIÓN DE CLIENTES DE IA ---
try:
    api_key_main = os.getenv("GROQ_API_KEY")
    if not api_key_main: sys.exit("❌ Error: La variable GROQ_API_KEY no está configurada.")
    client_groq = Groq(api_key=api_key_main)
    print("✅ Cliente de Groq configurado.")
except Exception as e:
    sys.exit(f"❌ Error al configurar el cliente de Groq: {e}")

# --- CONFIGURACIÓN GENERAL ---
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

# --- PLANTILLAS HTML ---
HTML_HEADER = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{title}</title><link rel="stylesheet" href="/static/css/style.css"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet"><link rel="icon" href="/static/img/logo.png" type="image/png"></head><body><header><div class="logo"><img src="/static/img/logo.png" alt="sIA Logo"><h1><a href="/index.html">sIA</a></h1></div><nav class="desktop-nav"><ul><li><a href="/noticias.html">Noticias</a></li></ul></nav><a href="https://docs.google.com/forms/d/e/1FAIpQLSeNl4keU0p1eDMvzUpM5p57Naf5qBMsl5MSJNBMxPnWbofshQ/viewform?usp=header" target="_blank" class="subscribe-button desktop-nav">Suscríbete</a><button class="hamburger-menu" aria-label="Abrir menú"><span></span></button></header><div class="mobile-nav"><nav><ul><li><a href="/noticias.html">Noticias</a></li></ul></nav><a href="https://docs.google.com/forms/d/e/1FAIpQLSeNl4keU0p1eDMvzUpM5p57Naf5qBMsl5MSJNBMxPnWbofshQ/viewform?usp=header" target="_blank" class="subscribe-button">Suscríbete</a></div>"""
HTML_FOOTER = """<footer><p>&copy; 2025 sIA. Todos los derechos reservados.</p><p><a href="/privacy.html">Política de Privacidad</a></p></footer><script>const hamburger = document.querySelector('.hamburger-menu');const mobileNav = document.querySelector('.mobile-nav');const body = document.querySelector('body');hamburger.addEventListener('click', () => {hamburger.classList.toggle('is-active');mobileNav.classList.toggle('is-active');body.classList.toggle('no-scroll');});</script></body></html>"""

# --- LÓGICA PRINCIPAL ---
def obtener_noticia_real_de_rss():
    print("📡 Buscando noticias reales en los RSS Feeds...")
    if not HISTORIAL_FILE.exists():
        HISTORIAL_FILE.touch()
    
    with open(HISTORIAL_FILE, "r") as f:
        historial = [line.strip() for line in f.readlines()]

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            if feed.entries:
                ultima_noticia = feed.entries[0]
                titulo = ultima_noticia.title
                link = ultima_noticia.link
                resumen = BeautifulSoup(ultima_noticia.summary, "html.parser").get_text(separator=' ', strip=True)

                if link not in historial:
                    print(f"✅ Noticia nueva encontrada: '{titulo}'")
                    return {"titulo": titulo, "link": link, "resumen": resumen}
        except Exception as e:
            print(f"⚠️  Advertencia: No se pudo leer el feed {feed_url}. Error: {e}")

    print("ℹ️ No se encontraron noticias nuevas en esta ejecución.")
    return None

def reescribir_noticia_con_ia(noticia):
    print("🤖 Pasando noticia real a la IA para reescribir...")
    system_prompt = "Eres un periodista para el blog 'sIA', especializado en IA en Latinoamérica. Tu tarea es reescribir noticias de otras fuentes en un artículo original, conciso y atractivo. Tu respuesta DEBE ser únicamente un objeto JSON válido. El artículo DEBE estar escrito íntegramente en español."
    user_prompt = f"""
    Basándote ESTRICTAMENTE en la siguiente información de una noticia real, escribe un artículo para nuestro blog. No inventes hechos que no estén aquí.
    - Título Original: "{noticia['titulo']}"
    - Resumen Original: "{noticia['resumen']}"
    - Fuente Original: "{noticia['link']}"

    Crea un nuevo título atractivo y un cuerpo de artículo que expanda el resumen de forma original.
    Formato JSON: {{"title": "Un nuevo titular atractivo para el artículo", "summary": "Un resumen corto (2-3 frases) del nuevo artículo.", "content_html": "El cuerpo del artículo en formato HTML, usando <p>, <h2> y <h3>."}}
    """
    try:
        chat_completion = client_groq.chat.completions.create(messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], model="llama3-8b-8192", max_tokens=2048, response_format={"type": "json_object"})
        contenido = json.loads(chat_completion.choices[0].message.content)
        if not all(k in contenido for k in ["title", "content_html", "summary"]):
            raise ValueError("El JSON de la API no tiene todos los campos.")
        contenido['source_link'] = noticia['link']
        return contenido
    except Exception as e:
        print(f"❌ Error CRÍTICO al generar contenido con Groq: {e}", file=sys.stderr)
        return None

def get_post_details(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            title = soup.find("h1", class_="article-title").string.strip()
            return title
    except Exception:
        return None

def crear_archivo_post(contenido):
    POSTS_DIR.mkdir(exist_ok=True)
    fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
    slug_base = contenido["title"].lower().replace(" ", "-").replace(":", "").replace("?", "").replace("¿", "")
    slug = f"{slug_base[:50]}-{datetime.datetime.now().strftime('%H%M%S')}"
    nombre_archivo = f"{datetime.date.today().strftime('%Y-%m-%d')}-{slug}.html"
    
    contenido['content_html'] += f'<p><em>Fuente original de la noticia: <a href="{contenido["source_link"]}" target="_blank" rel="noopener noreferrer">Leer más</a></em></p>'
    
    article_content = f"""<div class="main-container"><main class="article-body"><article><h1 class="article-title">{contenido['title']}</h1><p class="article-meta">Publicado por Redacción sIA el {fecha_actual}</p><div class="article-content">{contenido['content_html']}</div></article></main></div>"""
    full_html = HTML_HEADER.format(title=contenido['title']) + article_content + HTML_FOOTER
    with open(POSTS_DIR / nombre_archivo, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"📄 Archivo de post creado: {nombre_archivo}")
    with open(HISTORIAL_FILE, "a") as f:
        f.write(contenido['source_link'] + "\n")

def actualizar_paginas(todos_los_posts):
    print("🔄 Actualizando páginas (index, noticias, etc.)...")
    
    # Actualizar index.html (muestra los 9 más recientes)
    grid_index = ""
    for post_path in todos_los_posts[:9]:
        title = get_post_details(post_path)
        if title:
            imagen_aleatoria = random.choice(LISTA_DE_IMAGENES)
            grid_index += f"""<article class="article-card"><a href="/{post_path.as_posix()}"><img src="/static/img/{imagen_aleatoria}" alt="Artículo"></a><div class="card-content"><h3><a href="/{post_path.as_posix()}">{title}</a></h3></div></article>"""
    main_index = f"""<div class="main-container"><main class="homepage-main"><h2 class="section-title"><a href="/noticias.html">Últimas Noticias</a></h2><div class="article-grid">{grid_index}</div></main></div>"""
    full_html_index = HTML_HEADER.format(title="sIA - Inteligencia Artificial en Latinoamérica") + main_index + HTML_FOOTER
    with open(ROOT_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(full_html_index)

    # Actualizar noticias.html (muestra todos)
    grid_noticias = ""
    for post_path in todos_los_posts:
        title = get_post_details(post_path)
        if title:
            imagen_aleatoria = random.choice(LISTA_DE_IMAGENES)
            grid_noticias += f"""<article class="article-card"><a href="/{post_path.as_posix()}"><img src="/static/img/{imagen_aleatoria}" alt="Artículo"></a><div class="card-content"><h3><a href="/{post_path.as_posix()}">{title}</a></h3></div></article>"""
    main_noticias = f"""<div class="main-container"><main class="main-content-full"><h1 class="page-title">Archivo de Noticias</h1><div class="article-grid">{grid_noticias}</div></main></div>"""
    full_html_noticias = HTML_HEADER.format(title="Noticias - sIA") + main_noticias + HTML_FOOTER
    with open(ROOT_DIR / "noticias.html", "w", encoding="utf-8") as f:
        f.write(full_html_noticias)

if __name__ == "__main__":
    noticia_real = obtener_noticia_real_de_rss()
    
    if noticia_real:
        contenido_reescrito = reescribir_noticia_con_ia(noticia_real)
        
        if contenido_reescrito:
            crear_archivo_post(contenido_reescrito)
            posts_actualizados = sorted(list(POSTS_DIR.glob("*.html")), key=lambda p: p.name, reverse=True)
            actualizar_paginas(posts_actualizados)
            print("\n🎉 ¡Proceso completado exitosamente con una noticia real!")
        else:
            print("\n❌ La IA no pudo reescribir la noticia. La ejecución fallará.", file=sys.stderr)
            sys.exit(1)
    else:
        print("\n✅ Proceso completado. No había noticias nuevas para publicar.")
