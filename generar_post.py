# --- EJECUTANDO SCRIPT v7.0: PÁGINAS DE CATEGORÍA FUNCIONALES ---
import os
import datetime
import json
from pathlib import Path
import sys
import random
from groq import Groq
from bs4 import BeautifulSoup

print("--- INICIANDO SCRIPT DE GENERACIÓN DE CONTENIDO v7.0 ---")

# --- CONFIGURACIÓN DE CLIENTES DE IA ---
try:
    api_key_main = os.getenv("GROQ_API_KEY")
    if not api_key_main: sys.exit("❌ Error fatal: La variable GROQ_API_KEY no está configurada.")
    client_news = Groq(api_key=api_key_main)
    print("✅ Cliente 1 (Noticias) configurado.")
    api_key_opinion = os.getenv("GROQ_API_KEY_OPINION", api_key_main)
    client_opinion = Groq(api_key=api_key_opinion)
    print("✅ Cliente 2 (Opinión) configurado.")
    api_key_herramientas = os.getenv("GROQ_API_KEY_HERRAMIENTAS", api_key_main)
    client_herramientas = Groq(api_key=api_key_herramientas)
    print("✅ Cliente 3 (Herramientas) configurado.")
    api_key_recursos = os.getenv("GROQ_API_KEY_RECURSOS", api_key_main)
    client_recursos = Groq(api_key=api_key_recursos)
    print("✅ Cliente 4 (Recursos) configurado.")
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

# --- PLANTILLA HTML (con enlace a /noticias.html) ---
HTML_HEADER = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{title}</title><link rel="stylesheet" href="/static/css/style.css"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet"></head><body>
<header>
    <div class="logo">
        <img src="/static/img/logo.png" alt="sIA Logo">
        <h1><a href="/index.html">sIA</a></h1>
    </div>
    <nav class="desktop-nav">
        <ul>
            <li><a href="/noticias.html">Noticias</a></li>
            <li><a href="#">IA para Todos</a></li>
            <li><a href="#">Herramientas IA</a></li>
            <li><a href="#">Opinión</a></li>
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
            <li><a href="#">IA para Todos</a></li>
            <li><a href="#">Herramientas IA</a></li>
            <li><a href="#">Opinión</a></li>
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
PRIVACY_POLICY_CONTENT = """<main class="article-body" style="margin-top: 2rem;"><h1 class="article-title">Política de Privacidad</h1><div class="article-content"><p><strong>Fecha de vigencia:</strong> 12 de agosto de 2025</p><h2>1. Introducción</h2><p>Bienvenido a sIA. Tu privacidad es de suma importancia para nosotros. Esta Política de Privacidad describe qué datos recopilamos, cómo los usamos, cómo los protegemos y qué opciones tienes sobre tus datos cuando visitas nuestro sitio web.</p><h2>2. Información que Recopilamos</h2><ul><li><strong>Información Personal:</strong> Esto incluye información que nos proporcionas voluntariamente, como tu dirección de correo electrónico al suscribirte a nuestro boletín.</li><li><strong>Información No Personal:</strong> Recopilamos datos anónimos sobre tu visita (dirección IP, tipo de navegador, etc.) a través de cookies y servicios de análisis.</li></ul><h2>3. Uso de Cookies y Terceros</h2><p>Utilizamos cookies para mejorar la funcionalidad del sitio y personalizar tu experiencia. Somos participantes en el programa de publicidad de Google AdSense. Google, como proveedor externo, utiliza cookies para publicar anuncios. Puedes inhabilitar la publicidad personalizada en la <a href="https://adssettings.google.com/authenticated" target="_blank">configuración de anuncios de Google</a>.</p><h2>4. Tus Derechos</h2><p>Tienes derecho a acceder, rectificar o eliminar tu información personal. Para darte de baja de nuestro boletín, puedes seguir el enlace de "cancelar suscripción" que se incluirá en cada correo.</p><h2>5. Cambios a esta Política</h2><p>Podemos actualizar esta Política de Privacidad periódicamente. Te notificaremos cualquier cambio importante publicando la nueva política en nuestro sitio web.</p><h2>6. Contacto</h2><p>Si tienes alguna pregunta sobre esta Política, contáctanos a través de los medios disponibles en el sitio.</p></div></main>"""


# --- GENERADORES DE CONTENIDO POR CATEGORÍA ---
def generar_noticia(client):
    print("🧠 Usando IA de Noticias...")
    tema = random.choice(["una startup innovadora de IA en un país de LATAM", "una inversión importante en una empresa de tecnología en la región", "un nuevo avance tecnológico sobre IA desarrollado en una universidad local"])
    system_prompt = "Eres un periodista de tecnología para 'sIA'. Eres objetivo y te basas en hechos. Tu respuesta DEBE ser únicamente un objeto JSON válido."
    return generar_contenido_base(client, system_prompt, "Noticias", tema)

def generar_opinion(client):
    print("🤔 Usando IA de Opinión...")
    tema = random.choice(["el último gadget de IA y si realmente vale la pena", "un reto viral de IA en redes sociales y sus implicaciones", "una nueva app de IA que está cambiando la forma en que trabajamos", "el futuro de los asistentes de voz en los hogares de Latinoamérica"])
    system_prompt = "Eres un columnista de tecnología carismático para el blog 'sIA'. Escribes en primera persona y das tu perspectiva personal sobre las últimas tendencias de IA. Tu respuesta DEBE ser únicamente un objeto JSON válido."
    return generar_contenido_base(client, system_prompt, "Opinión", tema)

def generar_herramienta_afiliado(client):
    print("🛒 Usando IA de Herramientas (Afiliados)...")
    tema = "una reseña detallada de un producto tecnológico popular (como un smart speaker, un dron con IA, o un software de productividad). Incluye pros y contras. Al final del texto, añade el marcador de texto '[AQUÍ VA TU ENLACE DE AFILIADO]'."
    system_prompt = "Eres un reseñador de productos tecnológicos para 'sIA'. Escribes de forma persuasiva y honesta para ayudar a los lectores a tomar una decisión de compra. Tu respuesta DEBE ser únicamente un objeto JSON válido."
    return generar_contenido_base(client, system_prompt, "Herramientas IA", tema)

def generar_recursos_educativos(client):
    print("📚 Usando IA de Recursos (IA para Todos)...")
    tema = random.choice(["una lista curada de 'Las 5 mejores herramientas de IA para generar imágenes a partir de texto', con una breve descripción de cada una.", "un tutorial paso a paso para principiantes sobre cómo usar una herramienta de IA popular (como Eleven Labs para voz).", "una lista de 'Los 3 mejores cursos gratuitos para aprender sobre IA en 2025'."])
    system_prompt = "Eres un educador de tecnología para 'sIA'. Creas guías y listas de recursos fáciles de entender para ayudar a la gente a iniciarse en el mundo de la IA. Cada item de la lista debe terminar con el marcador '[AQUÍ VA EL ENLACE]'. Tu respuesta DEBE ser únicamente un objeto JSON válido."
    return generar_contenido_base(client, system_prompt, "IA para Todos", tema)

def generar_contenido_base(client, system_prompt, categoria, tema):
    user_prompt = f"""Genera un artículo para la categoría '{categoria}' sobre el tema: '{tema}'. El contenido HTML debe usar párrafos <p> y subtítulos <h2> y <h3>. Usa esta estructura JSON: {{"title": "Un titular atractivo y directo","summary": "Un resumen corto que enganche al lector.","content_html": "El cuerpo del artículo en HTML."}}"""
    try:
        chat_completion = client.chat.completions.create(messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], model="llama3-8b-8192", max_tokens=2048, response_format={"type": "json_object"})
        contenido = json.loads(chat_completion.choices[0].message.content)
        if not all(k in contenido for k in ["title", "content_html", "summary"]): raise ValueError("JSON incompleto.")
        slug_base = contenido["title"].lower().replace(" ", "-").replace(":", "").replace("?", "").replace("¿", "")
        contenido['slug'] = f"{slug_base[:50]}-{datetime.datetime.now().strftime('%H%M%S')}"
        contenido['category'] = categoria
        print(f"✅ Contenido generado con éxito: '{contenido['title']}'")
        return contenido
    except Exception as e:
        print(f"❌ Error crítico al generar contenido: {e}")
        return None

# --- FUNCIONES AUXILIARES ---
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
    POSTS_DIR.mkdir(exist_ok=True)
    fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
    nombre_archivo = f"{datetime.date.today().strftime('%Y-%m-%d')}-{contenido['slug']}.html"
    related_posts_html = ""
    if todos_los_posts:
        posts_aleatorios = list(todos_los_posts)
        random.shuffle(posts_aleatorios)
        posts_relacionados = [p for p in posts_aleatorios if p.name != nombre_archivo][:3]
        cards_html = ""
        for post_path in posts_relacionados:
            title, _, category = get_post_details(post_path)
            if title:
                imagen_aleatoria = random.choice(LISTA_DE_IMAGENES)
                cards_html += f"""<article class="article-card"><a href="/{post_path.as_posix()}"><img src="/static/img/{imagen_aleatoria}" alt="Artículo" loading="lazy"></a><div class="card-content"><span class="category-tag">{category.replace(' ', '-')}</span><h3><a href="/{post_path.as_posix()}">{title}</a></h3></div></article>"""
        related_posts_html = f"""<section class="related-articles"><h2>Artículos que podrían interesarte</h2><div class="article-grid">{cards_html}</div></section>"""
    article_content = f"""<main class="article-body"><article><h1 class="article-title">{contenido['title']}</h1><p class="article-meta">Publicado por Redacción sIA el {fecha_actual} en <span class="category-tag">{contenido['category']}</span></p><div class="article-content">{contenido['content_html']}</div></article>{related_posts_html}</main>"""
    full_html = HTML_HEADER.format(title=contenido['title']) + article_content + HTML_FOOTER
    with open(POSTS_DIR / nombre_archivo, "w", encoding="utf-8") as f: f.write(full_html)
    print(f"📄 Archivo de post creado: {nombre_archivo}")

def actualizar_index():
    print("🔄 Actualizando la página de inicio (index.html)...")
    all_posts = sorted(POSTS_DIR.glob("*.html"), key=os.path.getmtime, reverse=True)
    posts_por_categoria = {"Noticias": [], "IA para Todos": [], "Herramientas IA": [], "Opinión": []}
    for post in all_posts:
        _, _, category = get_post_details(post)
        if category in posts_por_categoria:
            posts_por_categoria[category].append(post)
    hero_html = ""
    if all_posts:
        hero_title, hero_summary, hero_category = get_post_details(all_posts[0])
        if hero_title:
            hero_html = f"""<section class="hero-article"><span class="category-tag">{hero_category}</span><h2><a href="/{all_posts[0].as_posix()}">{hero_title}</a></h2><p>{hero_summary}</p></section>"""
    def crear_grid_html(posts, num_items):
        grid_html = ""
        for post_path in posts[:num_items]:
            title, _, category = get_post_details(post_path)
            if title:
                imagen_aleatoria = random.choice(LISTA_DE_IMAGENES)
                grid_html += f"""<article class="article-card"><a href="/{post_path.as_posix()}"><img src="/static/img/{imagen_aleatoria}" alt="Artículo" loading="lazy"></a><div class="card-content"><span class="category-tag {category.replace(' ', '-')}">{category}</span><h3><a href="/{post_path.as_posix()}">{title}</a></h3></div></article>"""
        return grid_html
    grid_noticias_html = crear_grid_html(posts_por_categoria["Noticias"], 6)
    grid_opinion_html = crear_grid_html(posts_por_categoria["Opinión"], 3)
    grid_recursos_html = crear_grid_html(posts_por_categoria["IA para Todos"], 3)
    index_main_content = f"""<main><div class="main-content"><h2 class="section-title">Últimas Noticias</h2><div class="article-grid">{grid_noticias_html}</div><h2 class="section-title">Opinión</h2><div class="article-grid article-grid-secondary">{grid_opinion_html}</div><h2 class="section-title">IA para Todos</h2><div class="article-grid article-grid-secondary">{grid_recursos_html}</div></div><aside class="sidebar"><div class="widget"><h3>Herramientas Destacadas</h3></div></aside></main>"""
    full_html = HTML_HEADER.format(title="sIA - Inteligencia Artificial en Latinoamérica") + index_main_content + HTML_FOOTER
    with open(ROOT_DIR / "index.html", "w", encoding="utf-8") as f: f.write(full_html)
    print("✅ index.html actualizado.")

# --- NUEVA FUNCIÓN PARA LA PÁGINA DE NOTICIAS ---
def crear_pagina_noticias():
    print("📰 Creando la página de la sección de Noticias...")
    all_posts = sorted(POSTS_DIR.glob("*.html"), key=os.path.getmtime, reverse=True)
    
    posts_noticias = []
    for post in all_posts:
        _, _, category = get_post_details(post)
        if category == "Noticias":
            posts_noticias.append(post)

    grid_html = ""
    # Itera sobre TODOS los posts de noticias, sin límite
    for post_path in posts_noticias:
        title, _, category = get_post_details(post_path)
        if title:
            imagen_aleatoria = random.choice(LISTA_DE_IMAGENES)
            grid_html += f"""<article class="article-card">
                <a href="/{post_path.as_posix()}"><img src="/static/img/{imagen_aleatoria}" alt="Artículo" loading="lazy"></a>
                <div class="card-content"><span class="category-tag {category.replace(' ', '-')}">{category}</span><h3><a href="/{post_path.as_posix()}">{title}</a></h3></div>
            </article>"""
    
    main_content = f"""
    <main class="main-content-full">
        <h1 class="page-title">Todas las Noticias</h1>
        <div class="article-grid">{grid_html}</div>
    </main>
    """

    full_html = HTML_HEADER.format(title="Noticias - sIA") + main_content + HTML_FOOTER
    with open(ROOT_DIR / "noticias.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print("✅ noticias.html creada/actualizada.")

def crear_pagina_privacidad():
    print("🔄 Creando/Actualizando la página de Política de Privacidad...")
    full_html = (HTML_HEADER.format(title="Política de Privacidad - sIA") + PRIVACY_POLICY_CONTENT + HTML_FOOTER)
    with open(ROOT_DIR / "privacy.html", "w", encoding="utf-8") as f: f.write(full_html)
    print("✅ privacy.html creada.")

# --- BLOQUE DE EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    try: from bs4 import BeautifulSoup
    except ImportError: os.system(f"{sys.executable} -m pip install beautifulsoup4")
    
    opciones = [generar_noticia, generar_opinion, generar_herramienta_afiliado, generar_recursos_educativos]
    clientes = [client_news, client_opinion, client_herramientas, client_recursos]
    eleccion = random.choices(range(4), weights=[0.55, 0.15, 0.15, 0.15], k=1)[0]
    
    funcion_a_ejecutar = opciones[eleccion]
    cliente_a_usar = clientes[eleccion]
    
    contenido_nuevo = funcion_a_ejecutar(cliente_a_usar)
    
    if contenido_nuevo:
        posts_existentes = list(POSTS_DIR.glob("*.html"))
        crear_archivo_post(contenido_nuevo, posts_existentes)
        actualizar_index()
        crear_pagina_privacidad()
        crear_pagina_noticias()  # Se añade la llamada a la nueva función
        print("\n🎉 ¡Proceso completado exitosamente!")
    else:
        print("\n❌ No se generó contenido nuevo. El proceso se detuvo.")
