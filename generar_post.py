# --- EJECUTANDO SCRIPT v17.0: VERSIÓN FINAL CON REPARADOR FUNCIONAL ---
import os
import datetime
import json
from pathlib import Path
import sys
import random
import feedparser
from groq import Groq
from bs4 import BeautifulSoup

print("--- INICIANDO SCRIPT DE GENERACIÓN DE CONTENIDO v17.0 ---")

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
PRIVACY_POLICY_CONTENT = """<main class="article-body" style="margin-top: 2rem;"><h1 class="article-title">Política de Privacidad</h1><div class="article-content"><p>Texto de la política de privacidad...</p></div></main>"""

# --- LÓGICA DE CONTENIDO ---
def obtener_noticia_real_de_rss():
    print("📡 Buscando noticias reales en RSS...")
    if not HISTORIAL_FILE.exists(): HISTORIAL_FILE.touch()
    with open(HISTORIAL_FILE, "r") as f:
        historial = [line.strip() for line in f.readlines()]
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        if feed.entries:
            noticia = feed.entries[0]
            if noticia.link not in historial:
                print(f"✅ Noticia real encontrada: '{noticia.title}'")
                return {"titulo": noticia.title, "link": noticia.link, "resumen": BeautifulSoup(noticia.summary, "html.parser").get_text(separator=' ', strip=True)}
    return None

def generar_contenido_ia(categoria, tema):
    print(f"🤖 Generando contenido IA para '{categoria}'...")
    system_prompt = f"Eres un experto en IA para el blog 'sIA'. Escribe un artículo de '{categoria}'. El artículo DEBE estar en español."
    user_prompt = f"""Escribe un artículo sobre: '{tema}'. Formato JSON: {{"title": "...", "summary": "...", "content_html": "..."}}"""
    try:
        chat_completion = client_groq.chat.completions.create(messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], model="llama3-8b-8192", response_format={"type": "json_object"})
        contenido = json.loads(chat_completion.choices[0].message.content)
        contenido['category'] = categoria
        return contenido
    except Exception as e:
        print(f"❌ Error al generar contenido IA: {e}", file=sys.stderr)
        return None

def reescribir_noticia_con_ia(noticia):
    print("🤖 Reescribiendo noticia real con IA...")
    system_prompt = "Eres un periodista para 'sIA'. Reescribe noticias de otras fuentes en un artículo original y atractivo. DEBE estar en español."
    user_prompt = f"""Basado en: Título: "{noticia['titulo']}", Resumen: "{noticia['resumen']}", Fuente: "{noticia['link']}", escribe un artículo. Formato JSON: {{"title": "...", "summary": "...", "content_html": "..."}}"""
    try:
        chat_completion = client_groq.chat.completions.create(messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], model="llama3-8b-8192", response_format={"type": "json_object"})
        contenido = json.loads(chat_completion.choices[0].message.content)
        contenido['source_link'] = noticia['link']
        contenido['category'] = "Noticias"
        return contenido
    except Exception as e:
        print(f"❌ Error al reescribir noticia: {e}", file=sys.stderr)
        return None

# --- FUNCIONES DE CREACIÓN DE PÁGINAS ---
def get_post_details_for_index(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            title_tag = soup.find("h1", class_="article-title")
            title = title_tag.string.strip() if title_tag and title_tag.string else "Sin Título"
            category_tag = soup.find("span", class_="category-tag")
            category = category_tag.string.strip() if category_tag and category_tag.string else "Noticias"
            return title, category
    except Exception: return "Sin Título", "Noticias"

def crear_archivo_post(contenido):
    POSTS_DIR.mkdir(exist_ok=True)
    fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
    slug_base = contenido["title"].lower().replace(" ", "-").replace(":", "").replace("?", "").replace("¿", "")
    slug = f"{slug_base[:50]}-{datetime.datetime.now().strftime('%H%M%S')}"
    nombre_archivo = f"{datetime.date.today().strftime('%Y-%m-%d')}-{slug}.html"
    source_html = f'<p><em>Fuente original: <a href="{contenido.get("source_link", "#")}" target="_blank" rel="noopener noreferrer">Leer más</a></em></p>' if 'source_link' in contenido else ''
    
    article_html = f"""
    <main class="article-body">
        <article>
            <h1 class="article-title">{contenido['title']}</h1>
            <p class="article-meta">Publicado por Redacción sIA el {fecha_actual} en <span class="category-tag {contenido['category'].replace(' ', '-')}">{contenido['category']}</span></p>
            <div class="article-content">{contenido['content_html']}{source_html}</div>
        </article>
    </main>
    """
    full_html = HTML_HEADER.format(title=contenido['title']) + article_html + HTML_FOOTER
    with open(POSTS_DIR / nombre_archivo, "w", encoding="utf-8") as f: f.write(full_html)
    print(f"📄 Archivo de post creado: {nombre_archivo}")
    if 'source_link' in contenido:
        with open(HISTORIAL_FILE, "a") as f: f.write(contenido['source_link'] + "\n")

def actualizar_paginas(todos_los_posts):
    print("🔄 Actualizando páginas (index, categorías, etc.)...")
    posts_por_categoria = {"Noticias": [], "Herramientas IA": [], "Opinión": []}
    for post in todos_los_posts:
        title, category = get_post_details_for_index(post)
        if title != "Sin Título" and category in posts_por_categoria:
            posts_por_categoria[category].append(post)

    def crear_grid_html(posts, num_items):
        grid_html = ""
        for post_path in posts[:num_items]:
            title, category = get_post_details_for_index(post_path)
            if title:
                imagen_aleatoria = random.choice(LISTA_DE_IMAGENES)
                grid_html += f"""<article class="article-card"><a href="/{post_path.as_posix()}"><img src="/static/img/{imagen_aleatoria}" alt="Artículo"></a><div class="card-content"><span class="category-tag {category.replace(' ', '-')}">{category}</span><h3><a href="/{post_path.as_posix()}">{title}</a></h3></div></article>"""
        return grid_html

    index_main_content = """<div class="main-container">"""
    if posts_por_categoria["Noticias"]: index_main_content += f"""<h2 class="section-title"><a href="/noticias.html">Últimas Noticias</a></h2><div class="article-grid">{crear_grid_html(posts_por_categoria["Noticias"], 6)}</div>"""
    if posts_por_categoria["Herramientas IA"]: index_main_content += f"""<h2 class="section-title"><a href="/herramientas.html">Herramientas IA</a></h2><div class="article-grid">{crear_grid_html(posts_por_categoria["Herramientas IA"], 3)}</div>"""
    if posts_por_categoria["Opinión"]: index_main_content += f"""<h2 class="section-title"><a href="/opinion.html">Opinión</a></h2><div class="article-grid">{crear_grid_html(posts_por_categoria["Opinión"], 3)}</div>"""
    index_main_content += "</div>"
    full_html_index = HTML_HEADER.format(title="sIA - Inteligencia Artificial en Latinoamérica") + index_main_content + HTML_FOOTER
    with open(ROOT_DIR / "index.html", "w", encoding="utf-8") as f: f.write(full_html_index)

    for categoria, posts in posts_por_categoria.items():
        if posts:
            nombre_archivo = f"{categoria.lower().replace(' ', '-')}.html"
            grid_categoria = crear_grid_html(posts, len(posts))
            main_categoria = f"""<div class="main-container"><main class="main-content-full"><h1 class="page-title">Artículos de {categoria}</h1><div class="article-grid">{grid_categoria}</div></main></div>"""
            full_html_categoria = HTML_HEADER.format(title=f"{categoria} - sIA") + main_categoria + HTML_FOOTER
            with open(ROOT_DIR / nombre_archivo, "w", encoding="utf-8") as f: f.write(full_html_categoria)

def crear_pagina_privacidad():
    full_html = HTML_HEADER.format(title="Política de Privacidad - sIA") + PRIVACY_POLICY_CONTENT + HTML_FOOTER
    with open(ROOT_DIR / "privacy.html", "w", encoding="utf-8") as f: f.write(full_html)

def reparar_posts_antiguos(todos_los_posts):
    print("🛠️ INICIANDO MODO REPARACIÓN DE POSTS ANTIGUOS...")
    for post_path in todos_los_posts:
        print(f"Intentando reparar: {post_path.name}")
        try:
            with open(post_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
            
            # Extrae el contenido central como texto, pase lo que pase
            content_tag = soup.find("div", class_="article-content") or soup.find("article") or soup.find("main")
            if not content_tag:
                print(f"⚠️  Saltando {post_path.name}, no se pudo encontrar contenido central.")
                continue

            # Genera un título desde el nombre del archivo
            slug_title = post_path.name[11:-12].replace("-", " ").capitalize()
            
            # Asigna una categoría por defecto
            category = "Noticias"
            
            # Extrae la fecha del nombre del archivo
            date_str = post_path.name[:10]
            fecha_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            fecha_reparada = f"{fecha_obj.day} de {meses[fecha_obj.month - 1]} de {fecha_obj.year}"
            
            # Reconstruye el post con la estructura correcta
            repaired_article_html = f"""
            <main class="article-body">
                <article>
                    <h1 class="article-title">{slug_title}</h1>
                    <p class="article-meta">Publicado por Redacción sIA el {fecha_reparada} en <span class="category-tag {category.replace(' ', '-')}">{category}</span></p>
                    <div class="article-content">{str(content_tag)}</div>
                </article>
            </main>
            """
            full_repaired_html = HTML_HEADER.format(title=slug_title) + repaired_article_html + HTML_FOOTER
            with open(post_path, "w", encoding="utf-8") as f:
                f.write(full_repaired_html)
            print(f"✅ Reparado: {post_path.name}")
        except Exception as e:
            print(f"⚠️  Error al reparar {post_path.name}: {e}")
    print("✅ REPARACIÓN COMPLETADA.")

if __name__ == "__main__":
    posts_actuales = sorted(list(POSTS_DIR.glob("*.html")), key=lambda p: p.name, reverse=True)
    
    if RECONSTRUIR_POSTS_ANTIGUOS:
        reparar_posts_antiguos(posts_actuales)
    else:
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
            crear_archivo_post(contenido_final)
        else:
            print("\n❌ No se pudo generar contenido. La ejecución fallará.", file=sys.stderr)
            sys.exit(1)
    
    posts_actualizados = sorted(list(POSTS_DIR.glob("*.html")), key=lambda p: p.name, reverse=True)
    actualizar_paginas(posts_actualizados)
    crear_pagina_privacidad()
    print("\n🎉 ¡Proceso completado exitosamente!")
