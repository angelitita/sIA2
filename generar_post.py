# --- EJECUTANDO SCRIPT v11.0: CORRECCIONES FINALES ---
import os
import datetime
import json
from pathlib import Path
import sys
import random
from groq import Groq
from bs4 import BeautifulSoup

print("--- INICIANDO SCRIPT DE GENERACIÓN DE CONTENIDO v11.0 ---")

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

# --- LISTAS DE TEMAS (para evitar repeticiones) ---
temas_noticias = ["una startup innovadora de IA en un país de LATAM", "una inversión importante en una empresa de tecnología en la región", "un nuevo avance tecnológico sobre IA desarrollado en una universidad local"]
temas_opinion = ["el último gadget de IA y si realmente vale la pena", "un reto viral de IA en redes sociales y sus implicaciones", "una nueva app de IA que está cambiando la forma en que trabajamos", "el futuro de los asistentes de voz en los hogares de Latinoamérica"]
temas_recursos = ["una lista curada de 'Las 5 mejores herramientas de IA para generar imágenes a partir de texto'", "un tutorial paso a paso para principiantes sobre cómo usar una herramienta de IA popular (como Eleven Labs para voz)", "una lista de 'Los 3 mejores cursos gratuitos para aprender sobre IA en 2025'"]
temas_herramientas = ["una reseña detallada de un producto tecnológico popular (como un smart speaker, un dron con IA, o un software de productividad). Incluye pros y contras. Al final del texto, añade el marcador de texto '[AQUÍ VA TU ENLACE DE AFILIADO]'."]

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


def generar_contenido_base(client, system_prompt, categoria, tema):
    user_prompt = f"""Genera un artículo para la categoría '{categoria}' sobre: '{tema}'. Reglas estrictas: 1. El artículo DEBE estar escrito íntegramente en español de Latinoamérica. 2. La respuesta debe ser únicamente un objeto JSON válido, sin texto antes o después. Formato: {{"title": "...", "summary": "...", "content_html": "..."}}"""
    try:
        chat_completion = client.chat.completions.create(messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], model="llama3-8b-8192", max_tokens=2048, response_format={"type": "json_object"})
        contenido = json.loads(chat_completion.choices[0].message.content)
        if not all(k in contenido for k in ["title", "content_html", "summary"]): raise ValueError("El JSON de la API no tiene todos los campos.")
        slug_base = contenido["title"].lower().replace(" ", "-").replace(":", "").replace("?", "").replace("¿", "")
        contenido['slug'] = f"{slug_base[:50]}-{datetime.datetime.now().strftime('%H%M%S')}"
        contenido['category'] = categoria
        print(f"✅ Contenido generado: '{contenido['title']}'")
        return contenido
    except Exception as e:
        print(f"❌ Error CRÍTICO al generar contenido: {e}", file=sys.stderr)
        return None

def get_post_details(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            title = soup.find("h1", class_="article-title").string.strip()
            category = soup.find("span", class_="category-tag").string.strip()
            return title, category
    except Exception: return None, None

def crear_archivo_post(contenido, todos_los_posts):
    POSTS_DIR.mkdir(exist_ok=True)
    fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
    nombre_archivo = f"{datetime.date.today().strftime('%Y-%m-%d')}-{contenido['slug']}.html"
    
    # --- LÓGICA DE RECOMENDACIONES REINCORPORADA ---
    related_posts_html = ""
    if todos_los_posts:
        posts_aleatorios = [p for p in todos_los_posts if p.name != nombre_archivo]
        random.shuffle(posts_aleatorios)
        posts_relacionados = posts_aleatorios[:3]
        cards_html = ""
        for post_path in posts_relacionados:
            title, category = get_post_details(post_path)
            if title:
                imagen_aleatoria = random.choice(LISTA_DE_IMAGENES)
                cards_html += f"""<article class="article-card"><a href="/{post_path.as_posix()}"><img src="/static/img/{imagen_aleatoria}" alt="Artículo"></a><div class="card-content"><span class="category-tag {category.replace(' ', '-')}">{category}</span><h3><a href="/{post_path.as_posix()}">{title}</a></h3></div></article>"""
        if cards_html:
            related_posts_html = f"""<section class="related-articles"><h2>Artículos que podrían interesarte</h2><div class="article-grid">{cards_html}</div></section>"""

    article_content = f"""<div class="main-container"><main class="article-body"><article><h1 class="article-title">{contenido['title']}</h1><p class="article-meta">Publicado por Redacción sIA el {fecha_actual} en <span class="category-tag {contenido['category'].replace(' ', '-')}">{contenido['category']}</span></p><div class="article-content">{contenido['content_html']}</div></article>{related_posts_html}</main></div>"""
    full_html = HTML_HEADER.format(title=contenido['title']) + article_content + HTML_FOOTER
    with open(POSTS_DIR / nombre_archivo, "w", encoding="utf-8") as f: f.write(full_html)
    print(f"📄 Archivo de post creado: {nombre_archivo}")

def actualizar_index(todos_los_posts):
    # ... (código sin cambios)
    pass
def crear_pagina_de_categoria(nombre_categoria, nombre_archivo, todos_los_posts):
    # ... (código sin cambios)
    pass
def crear_pagina_privacidad():
    # ... (código sin cambios)
    pass

# --- BLOQUE DE EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    funciones = {
        "Noticias": (client_news, temas_noticias, "Eres un periodista de tecnología..."),
        "Opinión": (client_opinion, temas_opinion, "Eres un columnista de tecnología..."),
        "Herramientas IA": (client_herramientas, temas_herramientas, "Eres un reseñador de productos..."),
        "IA para Todos": (client_recursos, temas_recursos, "Eres un educador de tecnología...")
    }
    
    # Elige una categoría al azar, con más peso para las noticias
    categoria_elegida = random.choices(list(funciones.keys()), weights=[0.55, 0.15, 0.15, 0.15], k=1)[0]
    
    cliente_a_usar, lista_de_temas, system_prompt = funciones[categoria_elegida]
    
    # Elige un tema de la lista y lo remueve para no repetirlo pronto
    if lista_de_temas:
        tema_elegido = random.choice(lista_de_temas)
        lista_de_temas.remove(tema_elegido)
    else: # Fallback por si la lista se vacía
        tema_elegido = "un tema de actualidad sobre IA en Latinoamérica"

    print(f"--- Decisión: Generar '{categoria_elegida}' sobre '{tema_elegido}' ---")
    contenido_nuevo = generar_contenido_base(cliente_a_usar, system_prompt, categoria_elegida, tema_elegido)
    
    if contenido_nuevo:
        todos_los_posts = sorted(list(POSTS_DIR.glob("*.html")), key=lambda p: p.name, reverse=True)
        crear_archivo_post(contenido_nuevo, todos_los_posts)
        
        # Obtiene la lista actualizada de posts DESPUÉS de crear el nuevo
        posts_actualizados = sorted(list(POSTS_DIR.glob("*.html")), key=lambda p: p.name, reverse=True)
        
        actualizar_index(posts_actualizados)
        crear_pagina_de_categoria("Noticias", "noticias.html", posts_actualizados)
        crear_pagina_de_categoria("Opinión", "opinion.html", posts_actualizados)
        crear_pagina_de_categoria("Herramientas IA", "herramientas.html", posts_actualizados)
        crear_pagina_de_categoria("IA para Todos", "ia-para-todos.html", posts_actualizados)
        crear_pagina_privacidad()
        print("\n🎉 ¡Proceso completado exitosamente!")
    else:
        print("\n❌ No se generó contenido nuevo. La ejecución fallará para alertar del problema.", file=sys.stderr)
        sys.exit(1)
