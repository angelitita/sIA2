# --- EJECUTANDO SCRIPT v10.0: ORDENAMIENTO Y ERRORES ROBUSTOS ---
import os
import datetime
import json
from pathlib import Path
import sys
import random
from groq import Groq
from bs4 import BeautifulSoup

print("--- INICIANDO SCRIPT DE GENERACIÓN DE CONTENIDO v10.0 ---")

# --- CONFIGURACIÓN DE CLIENTES DE IA ---
try:
    api_key_main = os.getenv("GROQ_API_KEY")
    if not api_key_main: sys.exit("❌ Error fatal: La variable GROQ_API_KEY no está configurada.")
    client_news = Groq(api_key=api_key_main)
    client_opinion = Groq(api_key=os.getenv("GROQ_API_KEY_OPINION", api_key_main))
    client_herramientas = Groq(api_key=os.getenv("GROQ_API_KEY_HERRAMIENTAS", api_key_main))
    client_recursos = Groq(api_key=os.getenv("GROQ_API_KEY_RECURSOS", api_key_main))
    print("✅ Clientes de IA configurados.")
except Exception as e:
    sys.exit(f"❌ Error fatal al configurar los clientes de Groq: {e}")

# --- CONFIGURACIÓN GENERAL ---
IMG_DIR = Path("static/img")
LISTA_DE_IMAGENES = []
try:
    extensions = ['.png', '.jpg', '.jpeg', '.webp']
    LISTA_DE_IMAGENES = [f.name for f in IMG_DIR.glob('*') if f.suffix.lower() in extensions and f.name != 'logo.png']
    if not LISTA_DE_IMAGENES: LISTA_DE_IMAGENES.append("logo.png")
    print(f"✅ {len(LISTA_DE_IMAGENES)} imágenes encontradas.")
except Exception as e:
    print(f"❌ Error al cargar imágenes: {e}")
    LISTA_DE_IMAGENES = ["logo.png"]

POSTS_DIR = Path("posts")
ROOT_DIR = Path(".")

# --- PLANTILLAS HTML ---
HTML_HEADER = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{title}</title><link rel="stylesheet" href="/static/css/style.css"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet"></head><body>
<header>
    <div class="logo"><img src="/static/img/logo.png" alt="sIA Logo"><h1><a href="/index.html">sIA</a></h1></div>
    <nav class="desktop-nav"><ul><li><a href="/noticias.html">Noticias</a></li><li><a href="/ia-para-todos.html">IA para Todos</a></li><li><a href="/herramientas.html">Herramientas IA</a></li><li><a href="/opinion.html">Opinión</a></li></ul></nav>
    <a href="https://docs.google.com/forms/d/e/1FAIpQLSeNl4keU0p1eDMvzUpM5p57Naf5qBMsl5MSJNBMxPnWbofshQ/viewform?usp=header" target="_blank" class="subscribe-button desktop-nav">Suscríbete</a>
    <button class="hamburger-menu" aria-label="Abrir menú"><span></span></button>
</header>
<div class="mobile-nav"><nav><ul><li><a href="/noticias.html">Noticias</a></li><li><a href="/ia-para-todos.html">IA para Todos</a></li><li><a href="/herramientas.html">Herramientas IA</a></li><li><a href="/opinion.html">Opinión</a></li></ul></nav><a href="https://docs.google.com/forms/d/e/1FAIpQLSeNl4keU0p1eDMvzUpM5p57Naf5qBMsl5MSJNBMxPnWbofshQ/viewform?usp=header" target="_blank" class="subscribe-button">Suscríbete</a></div>"""
HTML_FOOTER = """<footer><p>&copy; 2025 sIA. Todos los derechos reservados.</p><p><a href="/privacy.html">Política de Privacidad</a></p></footer>
<script>
    const hamburger = document.querySelector('.hamburger-menu');
    const mobileNav = document.querySelector('.mobile-nav');
    const body = document.querySelector('body');
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('is-active');
        mobileNav.classList.toggle('is-active');
        body.classList.toggle('no-scroll');
    });
</script>
</body></html>"""
PRIVACY_POLICY_CONTENT = """<main class="article-body" style="margin-top: 2rem;"><h1 class="article-title">Política de Privacidad</h1><div class="article-content"><p>Texto de la política de privacidad...</p></div></main>"""

# --- GENERADORES DE CONTENIDO (CON MEJORES ERRORES) ---
def generar_contenido_base(client, system_prompt, categoria, tema):
    user_prompt = f"""Genera un artículo para la categoría '{categoria}' sobre: '{tema}'. El artículo DEBE estar escrito íntegramente en español. Formato JSON: {{"title": "...", "summary": "...", "content_html": "..."}}"""
    try:
        chat_completion = client.chat.completions.create(messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], model="llama3-8b-8192", max_tokens=2048, response_format={"type": "json_object"})
        contenido = json.loads(chat_completion.choices[0].message.content)
        if not all(k in contenido for k in ["title", "content_html", "summary"]): raise ValueError("El JSON recibido de la API no tiene todos los campos requeridos.")
        slug_base = contenido["title"].lower().replace(" ", "-").replace(":", "").replace("?", "").replace("¿", "")
        contenido['slug'] = f"{slug_base[:50]}-{datetime.datetime.now().strftime('%H%M%S')}"
        contenido['category'] = categoria
        print(f"✅ Contenido generado con éxito: '{contenido['title']}'")
        return contenido
    except Exception as e:
        # AHORA VEREMOS EL ERROR EXACTO EN LOS LOGS DE GITHUB
        print(f"❌ Error CRÍTICO al generar contenido con Groq: {e}", file=sys.stderr)
        return None

def generar_noticia(client): return generar_contenido_base(client, "Eres un periodista de tecnología para 'sIA'...", "Noticias", "una startup innovadora de IA en LATAM")
def generar_opinion(client): return generar_contenido_base(client, "Eres un columnista de tecnología para 'sIA'...", "Opinión", "el último gadget de IA y si vale la pena")
def generar_herramienta_afiliado(client): return generar_contenido_base(client, "Eres un reseñador de productos para 'sIA'...", "Herramientas IA", "una reseña de un producto tecnológico popular...")
def generar_recursos_educativos(client): return generar_contenido_base(client, "Eres un educador de tecnología para 'sIA'...", "IA para Todos", "una lista curada de 'Las 5 mejores herramientas de IA'...")

# --- FUNCIONES DE CREACIÓN DE PÁGINAS (CON ORDENAMIENTO CORREGIDO) ---
def get_post_details(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            title = soup.find("h1", class_="article-title").string.strip()
            category = soup.find("span", class_="category-tag").string.strip()
            return title, category
    except Exception: return None, None

def crear_archivo_post(contenido):
    POSTS_DIR.mkdir(exist_ok=True)
    fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
    nombre_archivo = f"{datetime.date.today().strftime('%Y-%m-%d')}-{contenido['slug']}.html"
    article_content = f"""<div class="main-container"><main class="article-body"><article><h1 class="article-title">{contenido['title']}</h1><p class="article-meta">Publicado por Redacción sIA el {fecha_actual} en <span class="category-tag {contenido['category'].replace(' ', '-')}">{contenido['category']}</span></p><div class="article-content">{contenido['content_html']}</div></article></main></div>"""
    full_html = HTML_HEADER.format(title=contenido['title']) + article_content + HTML_FOOTER
    with open(POSTS_DIR / nombre_archivo, "w", encoding="utf-8") as f: f.write(full_html)
    print(f"📄 Archivo de post creado: {nombre_archivo}")

def crear_pagina_de_categoria(nombre_categoria, nombre_archivo, todos_los_posts):
    print(f"📄 Creando página para la sección '{nombre_categoria}'...")
    posts_de_categoria = [post for post in todos_los_posts if get_post_details(post)[1] == nombre_categoria]
    grid_html = ""
    for post_path in posts_de_categoria:
        title, category = get_post_details(post_path)
        if title:
            imagen_aleatoria = random.choice(LISTA_DE_IMAGENES)
            grid_html += f"""<article class="article-card"><a href="/{post_path.as_posix()}"><img src="/static/img/{imagen_aleatoria}" alt="Artículo"></a><div class="card-content"><span class="category-tag {category.replace(' ', '-')}">{category}</span><h3><a href="/{post_path.as_posix()}">{title}</a></h3></div></article>"""
    main_content = f"""<div class="main-container"><main class="main-content-full"><h1 class="page-title">Artículos de {nombre_categoria}</h1><div class="article-grid">{grid_html}</div></main></div>"""
    full_html = HTML_HEADER.format(title=f"{nombre_categoria} - sIA") + main_content + HTML_FOOTER
    with open(ROOT_DIR / nombre_archivo, "w", encoding="utf-8") as f: f.write(full_html)
    print(f"✅ {nombre_archivo} creada/actualizada.")

def actualizar_index(todos_los_posts):
    print("🔄 Actualizando la página de inicio...")
    posts_por_categoria = {"Noticias": [], "IA para Todos": [], "Herramientas IA": [], "Opinión": []}
    for post in todos_los_posts:
        _, category = get_post_details(post)
        if category in posts_por_categoria: posts_por_categoria[category].append(post)
    def crear_grid_html(posts, num_items):
        grid_html = ""
        for post_path in posts[:num_items]:
            title, category = get_post_details(post_path)
            if title:
                imagen_aleatoria = random.choice(LISTA_DE_IMAGENES)
                grid_html += f"""<article class="article-card"><a href="/{post_path.as_posix()}"><img src="/static/img/{imagen_aleatoria}" alt="Artículo"></a><div class="card-content"><span class="category-tag {category.replace(' ', '-')}">{category}</span><h3><a href="/{post_path.as_posix()}">{title}</a></h3></div></article>"""
        return grid_html
    index_main_content = f"""<div class="main-container"><main class="homepage-main"><h2 class="section-title"><a href="/noticias.html">Últimas Noticias</a></h2><div class="article-grid">{crear_grid_html(posts_por_categoria["Noticias"], 6)}</div><h2 class="section-title"><a href="/opinion.html">Opinión</a></h2><div class="article-grid article-grid-secondary">{crear_grid_html(posts_por_categoria["Opinión"], 3)}</div></main></div>"""
    full_html = HTML_HEADER.format(title="sIA - Inteligencia Artificial en Latinoamérica") + index_main_content + HTML_FOOTER
    with open(ROOT_DIR / "index.html", "w", encoding="utf-8") as f: f.write(full_html)
    print("✅ index.html actualizado.")

def crear_pagina_privacidad():
    full_html = HTML_HEADER.format(title="Política de Privacidad - sIA") + PRIVACY_POLICY_CONTENT + HTML_FOOTER
    with open(ROOT_DIR / "privacy.html", "w", encoding="utf-8") as f: f.write(full_html)

# --- BLOQUE DE EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    opciones = [generar_noticia, generar_opinion, generar_herramienta_afiliado, generar_recursos_educativos]
    clientes = [client_news, client_opinion, client_herramientas, client_recursos]
    eleccion = random.choices(range(4), weights=[0.55, 0.15, 0.15, 0.15], k=1)[0]
    
    print(f"--- Decisión: Generar un post de tipo '{opciones[eleccion].__name__}' ---")
    contenido_nuevo = opciones[eleccion](clientes[eleccion])
    
    if contenido_nuevo:
        crear_archivo_post(contenido_nuevo)
        # CORRECCIÓN: Ordenar la lista de posts por nombre de archivo (fecha)
        todos_los_posts = sorted(list(POSTS_DIR.glob("*.html")), key=lambda p: p.name, reverse=True)
        actualizar_index(todos_los_posts)
        crear_pagina_de_categoria("Noticias", "noticias.html", todos_los_posts)
        crear_pagina_de_categoria("Opinión", "opinion.html", todos_los_posts)
        crear_pagina_de_categoria("Herramientas IA", "herramientas.html", todos_los_posts)
        crear_pagina_de_categoria("IA para Todos", "ia-para-todos.html", todos_los_posts)
        crear_pagina_privacidad()
        print("\n🎉 ¡Proceso completado exitosamente!")
    else:
        # AHORA LA ACCIÓN FALLARÁ SI NO HAY CONTENIDO NUEVO
        print("\n❌ No se generó contenido nuevo. La ejecución fallará para alertar del problema.", file=sys.stderr)
        sys.exit(1)
