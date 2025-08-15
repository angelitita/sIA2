# --- EJECUTANDO SCRIPT v8.0: NAVEGACIÓN COMPLETA ---
import os
import datetime
import json
from pathlib import Path
import sys
import random
from groq import Groq
from bs4 import BeautifulSoup

print("--- INICIANDO SCRIPT DE GENERACIÓN DE CONTENIDO v8.0 ---")

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

# --- PLANTILLA HTML (con todos los enlaces del menú funcionales) ---
HTML_HEADER = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{title}</title><link rel="stylesheet" href="/static/css/style.css"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet"></head><body>
<header>
    <div class="logo">
        <img src="/static/img/logo.png" alt="sIA Logo">
        <h1><a href="/index.html">sIA</a></h1>
    </div>
    <nav class="desktop-nav">
        <ul>
            <li><a href="/noticias.html">Noticias</a></li>
            <li><a href="/ia-para-todos.html">IA para Todos</a></li>
            <li><a href="/herramientas.html">Herramientas IA</a></li>
            <li><a href="/opinion.html">Opinión</a></li>
        </ul>
    </nav>
    <a href="https://docs.google.com/forms/d/e/1FAIpQLSeNl4keU0p1eDMvzUpM5p57Naf5qBMsl5MSJNBMxPnWbofshQ/viewform?usp=header" target="_blank" class="subscribe-button desktop-nav">Suscríbete</a>
    <button class="hamburger-menu" aria-label="Abrir menú">
        <span></span>
        <span></span>
        <span></span>
    </button>
</header>
<div class="mobile-nav">
    <nav>
        <ul>
            <li><a href="/noticias.html">Noticias</a></li>
            <li><a href="/ia-para-todos.html">IA para Todos</a></li>
            <li><a href="/herramientas.html">Herramientas IA</a></li>
            <li><a href="/opinion.html">Opinión</a></li>
        </ul>
    </nav>
    <a href="https://docs.google.com/forms/d/e/1FAIpQLSeNl4keU0p1eDMvzUpM5p57Naf5qBMsl5MSJNBMxPnWbofshQ/viewform?usp=header" target="_blank" class="subscribe-button">Suscríbete</a>
</div>
"""
HTML_FOOTER = """<footer><p>&copy; 2025 sIA. Todos los derechos reservados.</p><p><a href="/privacy.html">Política de Privacidad</a></p></footer>
<script>
    const hamburger = document.querySelector('.hamburger-menu');
    const mobileNav = document.querySelector('.mobile-nav');
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('is-active');
        mobileNav.classList.toggle('is-active');
    });
</script>
</body></html>"""
PRIVACY_POLICY_CONTENT = """<main class="article-body" style="margin-top: 2rem;"><h1 class="article-title">Política de Privacidad</h1><div class="article-content"><p>Texto de la política de privacidad...</p></div></main>"""

# --- GENERADORES DE CONTENIDO ---
def generar_noticia(client):
    # ... (código sin cambios)
    return generar_contenido_base(client, "Eres un periodista de tecnología para 'sIA'. Eres objetivo y te basas en hechos...", "Noticias", "una startup innovadora de IA en un país de LATAM")
def generar_opinion(client):
    # ... (código sin cambios)
    return generar_contenido_base(client, "Eres un columnista de tecnología carismático para 'sIA'...", "Opinión", "el último gadget de IA y si realmente vale la pena")
def generar_herramienta_afiliado(client):
    # ... (código sin cambios)
    return generar_contenido_base(client, "Eres un reseñador de productos tecnológicos para 'sIA'...", "Herramientas IA", "una reseña detallada de un producto tecnológico popular...")
def generar_recursos_educativos(client):
    # ... (código sin cambios)
    return generar_contenido_base(client, "Eres un educador de tecnología para 'sIA'...", "IA para Todos", "una lista curada de 'Las 5 mejores herramientas de IA para generar imágenes'...")

def generar_contenido_base(client, system_prompt, categoria, tema):
    user_prompt = f"""Genera un artículo para la categoría '{categoria}' sobre: '{tema}'. Formato JSON: {{"title": "...", "summary": "...", "content_html": "..."}}"""
    try:
        chat_completion = client.chat.completions.create(messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], model="llama3-8b-8192", max_tokens=2048, response_format={"type": "json_object"})
        contenido = json.loads(chat_completion.choices[0].message.content)
        if not all(k in contenido for k in ["title", "content_html", "summary"]): raise ValueError("JSON incompleto.")
        slug_base = contenido["title"].lower().replace(" ", "-").replace(":", "").replace("?", "").replace("¿", "")
        contenido['slug'] = f"{slug_base[:50]}-{datetime.datetime.now().strftime('%H%M%S')}"
        contenido['category'] = categoria
        print(f"✅ Contenido generado: '{contenido['title']}'")
        return contenido
    except Exception as e:
        print(f"❌ Error al generar contenido: {e}")
        return None

# --- FUNCIONES DE CREACIÓN DE PÁGINAS ---
def get_post_details(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            title = soup.find("h1", class_="article-title").string.strip()
            category = soup.find("span", class_="category-tag").string.strip()
            summary_tag = soup.find("div", class_="article-content").find("p")
            summary = summary_tag.string.strip() if summary_tag and summary_tag.string else "Lee más..."
            return title, summary, category
    except Exception:
        return None, None, None

def crear_archivo_post(contenido, todos_los_posts):
    # ... (código sin cambios, esta función sigue igual)
    pass

def actualizar_index():
    print("🔄 Actualizando la página de inicio (index.html)...")
    all_posts = sorted(POSTS_DIR.glob("*.html"), key=os.path.getmtime, reverse=True)
    posts_por_categoria = {"Noticias": [], "IA para Todos": [], "Herramientas IA": [], "Opinión": []}
    for post in all_posts:
        _, _, category = get_post_details(post)
        if category in posts_por_categoria: posts_por_categoria[category].append(post)
    hero_html = ""
    if all_posts:
        hero_title, hero_summary, hero_category = get_post_details(all_posts[0])
        if hero_title:
            hero_html = f"""<section class="hero-article"><span class="category-tag {hero_category.replace(' ', '-')}">{hero_category}</span><h2><a href="/{all_posts[0].as_posix()}">{hero_title}</a></h2><p>{hero_summary}</p></section>"""
    def crear_grid_html(posts, num_items):
        grid_html = ""
        for post_path in posts[:num_items]:
            title, _, category = get_post_details(post_path)
            if title:
                imagen_aleatoria = random.choice(LISTA_DE_IMAGENES)
                grid_html += f"""<article class="article-card"><a href="/{post_path.as_posix()}"><img src="/static/img/{imagen_aleatoria}" alt="Artículo"></a><div class="card-content"><span class="category-tag {category.replace(' ', '-')}">{category}</span><h3><a href="/{post_path.as_posix()}">{title}</a></h3></div></article>"""
        return grid_html
    grid_noticias_html = crear_grid_html(posts_por_categoria["Noticias"], 6)
    grid_opinion_html = crear_grid_html(posts_por_categoria["Opinión"], 3)
    grid_recursos_html = crear_grid_html(posts_por_categoria["IA para Todos"], 3)
    index_main_content = f"""<main><div class="main-content"><h2 class="section-title">Últimas Noticias</h2><div class="article-grid">{grid_noticias_html}</div><h2 class="section-title">Opinión</h2><div class="article-grid article-grid-secondary">{grid_opinion_html}</div><h2 class="section-title">IA para Todos</h2><div class="article-grid article-grid-secondary">{grid_recursos_html}</div></div><aside class="sidebar"><div class="widget"><h3>Herramientas Destacadas</h3></div></aside></main>"""
    full_html = HTML_HEADER.format(title="sIA - Inteligencia Artificial en Latinoamérica") + index_main_content + HTML_FOOTER
    with open(ROOT_DIR / "index.html", "w", encoding="utf-8") as f: f.write(full_html)
    print("✅ index.html actualizado.")

# --- NUEVO: Función genérica para crear páginas de categoría ---
def crear_pagina_de_categoria(nombre_categoria, nombre_archivo):
    print(f"📄 Creando página para la sección '{nombre_categoria}'...")
    all_posts = sorted(POSTS_DIR.glob("*.html"), key=os.path.getmtime, reverse=True)
    posts_de_categoria = []
    for post in all_posts:
        _, _, category = get_post_details(post)
        if category == nombre_categoria:
            posts_de_categoria.append(post)
    grid_html = ""
    for post_path in posts_de_categoria:
        title, _, category = get_post_details(post_path)
        if title:
            imagen_aleatoria = random.choice(LISTA_DE_IMAGENES)
            grid_html += f"""<article class="article-card"><a href="/{post_path.as_posix()}"><img src="/static/img/{imagen_aleatoria}" alt="Artículo"></a><div class="card-content"><span class="category-tag {category.replace(' ', '-')}">{category}</span><h3><a href="/{post_path.as_posix()}">{title}</a></h3></div></article>"""
    main_content = f"""<main class="main-content-full"><h1 class="page-title">Todos los artículos de {nombre_categoria}</h1><div class="article-grid">{grid_html}</div></main>"""
    full_html = HTML_HEADER.format(title=f"{nombre_categoria} - sIA") + main_content + HTML_FOOTER
    with open(ROOT_DIR / nombre_archivo, "w", encoding="utf-8") as f: f.write(full_html)
    print(f"✅ {nombre_archivo} creada/actualizada.")

def crear_pagina_privacidad():
    # ... (código sin cambios)
    pass

# --- BLOQUE DE EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    # ... (lógica de elección sin cambios)
    
    contenido_nuevo = ... # (se genera el contenido)
    
    if contenido_nuevo:
        posts_existentes = list(POSTS_DIR.glob("*.html"))
        crear_archivo_post(contenido_nuevo, posts_existentes)
        actualizar_index()
        crear_pagina_privacidad()
        # --- NUEVO: Genera todas las páginas de categoría en cada ejecución ---
        crear_pagina_de_categoria("Noticias", "noticias.html")
        crear_pagina_de_categoria("Opinión", "opinion.html")
        crear_pagina_de_categoria("Herramientas IA", "herramientas.html")
        crear_pagina_de_categoria("IA para Todos", "ia-para-todos.html")
        print("\n🎉 ¡Proceso completado exitosamente!")
    else:
        print("\n❌ No se generó contenido nuevo.")
