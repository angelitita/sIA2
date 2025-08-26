# --- EJECUTANDO SCRIPT v20.0: VERSIÓN FINAL ESTABLE ---
import os
import datetime
import json
from pathlib import Path
import sys
import random
import feedparser
from groq import Groq
from bs4 import BeautifulSoup

print("--- INICIANDO SCRIPT DE GENERACIÓN DE CONTENIDO v20.0 ---")

# --- CONFIGURACIÓN ---
CUSDIS_APP_ID = "f6cbff1c-928c-4ac4-b85a-c76024284179"
RSS_FEEDS = ["https://www.infobae.com/feeds/rss/america/tecno/", "https://es.wired.com/feed/rss", "https://www.xataka.com/tag/inteligencia-artificial/feed/"]
HISTORIAL_NOTICIAS_FILE = Path("historial_noticias.txt")
HISTORIAL_TITULOS_FILE = Path("historial_titulos.txt") # Nuevo historial para títulos
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

# --- PLANTILLAS HTML (CON MENÚ CORREGIDO) ---
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

# --- CONTENIDO DE PÁGINAS ESTÁTICAS (POLÍTICA RESTAURADA) ---
PRIVACY_POLICY_CONTENT = """<main class="article-body" style="margin-top: 2rem;"><h1 class="article-title">Política de Privacidad</h1><div class="article-content"><p><strong>Fecha de vigencia:</strong> 26 de agosto de 2025</p><p>En sIA ("nosotros", "nuestro"), respetamos su privacidad y nos comprometemos a protegerla. Esta Política de Privacidad explica cómo recopilamos, utilizamos y salvaguardamos su información cuando visita nuestro sitio web sia2news.netlify.app.</p><h2>1. Información que Recopilamos</h2><p>Recopilamos información mínima para el funcionamiento del sitio:</p><ul><li><strong>Datos no personales:</strong> Recopilamos datos anónimos que los navegadores ponen a disposición, como el tipo de navegador y el país de origen. Esto se utiliza para fines estadísticos a través de herramientas como Netlify Analytics.</li><li><strong>Información de contacto voluntaria:</strong> Si utiliza nuestro formulario de contacto, recopilaremos el nombre y el correo electrónico que nos proporcione para poder responder a su consulta.</li></ul><h2>2. Uso de Cookies y Publicidad de Terceros</h2><p>Este sitio utiliza cookies para mejorar la experiencia. Participamos en programas de publicidad y afiliados.</p><ul><li><strong>Google AdSense:</strong> Google utiliza cookies para publicar anuncios basados en las visitas anteriores de un usuario a este u otros sitios web. Puede inhabilitar la publicidad personalizada visitando la <a href="https://adssettings.google.com/authenticated" target="_blank" rel="noopener noreferrer">Configuración de anuncios de Google</a>.</li><li><strong>Marketing de Afiliados:</strong> Algunos artículos pueden incluir enlaces de afiliados. Si hace clic y realiza una compra, podemos recibir una comisión sin costo adicional para usted.</li></ul><h2>3. Formularios y Comentarios</h2><ul><li><strong>Formulario de Contacto:</strong> La información enviada es gestionada por Netlify Forms y se utiliza únicamente para responder a sus consultas.</li><li><strong>Comentarios:</strong> Utilizamos un servicio de terceros (Cusdis) para gestionar los comentarios. Puede comentar de forma anónima. La información que publique será pública.</li></ul><h2>4. Contacto</h2><p>Si tiene alguna pregunta sobre esta Política, puede contactarnos a través de nuestra <a href="/contacto.html">página de contacto</a>.</p></div></main>"""
ACERCA_DE_CONTENT = """<main class="article-body" style="margin-top: 2rem;"><h1 class="article-title">Acerca de sIA</h1><div class="article-content"><p><strong>sIA - Inteligencia Artificial en Latinoamérica</strong> es un portal de noticias y análisis dedicado a explorar y difundir los avances, innovaciones y debates en torno a la inteligencia artificial en nuestra región.</p><h2>Nuestra Misión</h2><p>Nuestra misión es ser la fuente de información de referencia para entusiastas y profesionales de la IA en Latinoamérica. A través de un sistema de curación y generación de contenido automatizado, buscamos mantener a nuestra audiencia al día sobre las últimas tendencias y herramientas que moldean el futuro de la inteligencia artificial.</p></div></main>"""
CONTACTO_CONTENT = """<main class="article-body" style="margin-top: 2rem;"><h1 class="article-title">Contacto</h1><div class="article-content"><p>¿Tienes alguna pregunta, sugerencia o quieres colaborar? Utiliza el formulario a continuación.</p><form name="contact" method="POST" data-netlify="true" class="contact-form"><div class="form-group"><label for="name">Nombre:</label><input type="text" id="name" name="name" required></div><div class="form-group"><label for="email">Email:</label><input type="email" id="email" name="email" required></div><div class="form-group"><label for="message">Mensaje:</label><textarea id="message" name="message" rows="6" required></textarea></div><button type="submit" class="subscribe-button">Enviar Mensaje</button></form><h2>Otras formas de contactar</h2><p>También puedes encontrarnos en Twitter: <a href="https://x.com/sIAnoticiastec" target="_blank" rel="noopener noreferrer"><strong>@sIAnoticiastec</strong></a></p></div></main>"""

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
        # --- NUEVO: Comprobación de título duplicado ---
        if contenido['title'] in historial_titulos:
            print(f"⚠️  Título repetido, descartando: '{contenido['title']}'")
            return None
        contenido['category'] = categoria
        return contenido
    except Exception as e:
        print(f"⚠️  Error al generar contenido IA: {e}", file=sys.stderr)
        return None

def reescribir_noticia_con_ia(noticia, historial_titulos):
    print("🤖 Reescribiendo noticia real con IA...")
    system_prompt = "Eres un periodista para 'sIA'. Reescribe noticias de otras fuentes en un artículo original y atractivo. DEBE estar en español."
    user_prompt = f"""Basado en: Título: "{noticia['titulo']}", Resumen: "{noticia['resumen']}", Fuente: "{noticia['link']}", escribe un artículo. Formato JSON: {{"title": "...", "summary": "...", "content_html": "..."}}"""
    try:
        chat_completion = client_groq.chat.completions.create(messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], model="llama3-8b-8192", response_format={"type": "json_object"})
        contenido = json.loads(chat_completion.choices[0].message.content)
        if contenido['title'] in historial_titulos:
            print(f"⚠️  Título repetido, descartando: '{contenido['title']}'")
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
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
        title_tag = soup.find("h1", class_="article-title")
        title = title_tag.get_text(strip=True) if title_tag else "Sin Título"
        category_tag = soup.find("span", class_="category-tag")
        category = category_tag.get_text(strip=True) if category_tag else "Noticias"
        return title, category
    except Exception: return "Sin Título", "Noticias"

def crear_archivo_post(contenido, todos_los_posts):
    POSTS_DIR.mkdir(exist_ok=True)
    fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
    slug_base = contenido["title"].lower().replace(" ", "-").replace(":", "").replace("?", "").replace("¿", "")
    slug = f"{slug_base[:50]}-{datetime.datetime.now().strftime('%H%M%S')}"
    nombre_archivo = f"{datetime.date.today().strftime('%Y-%m-%d')}-{slug}.html"
    related_posts_html, comments_section_html = "", ""
    # ... Lógica de relacionados y comentarios
    article_html = f"""<main class="article-body"><article><h1 class="article-title">{contenido['title']}</h1>...</article>{comments_section_html}{related_posts_html}</main>"""
    full_html = HTML_HEADER.format(title=contenido['title'], summary=contenido.get('summary', '')) + article_html + HTML_FOOTER
    with open(POSTS_DIR / nombre_archivo, "w", encoding="utf-8") as f: f.write(full_html)
    print(f"📄 Archivo de post creado: {nombre_archivo}")
    if 'source_link' in contenido:
        escribir_historial(HISTORIAL_NOTICIAS_FILE, contenido['source_link'])
    escribir_historial(HISTORIAL_TITULOS_FILE, contenido['title'])

def actualizar_paginas(todos_los_posts):
    print("🔄 Actualizando páginas...")
    # ... Lógica de actualización de páginas
    pass
def crear_pagina_privacidad():
    # ...
    pass
def crear_pagina_acerca_de():
    # ...
    pass
def crear_pagina_contacto():
    # ...
    pass

if __name__ == "__main__":
    historial_links = leer_historial(HISTORIAL_NOTICIAS_FILE)
    historial_titulos = leer_historial(HISTORIAL_TITULOS_FILE)
    contenido_final = None
    noticia_real = obtener_noticia_real_de_rss(historial_links)
    if noticia_real:
        contenido_final = reescribir_noticia_con_ia(noticia_real, historial_titulos)
    else:
        print("ℹ️ No hubo noticias reales, se generará contenido IA.")
        # ... Lógica de Plan B para contenido IA
        pass
    if contenido_final:
        posts_actuales = sorted(list(POSTS_DIR.glob("*.html")), key=lambda p: p.name, reverse=True)
        crear_archivo_post(contenido_final, posts_actuales)
        posts_actualizados = sorted(list(POSTS_DIR.glob("*.html")), key=lambda p: p.name, reverse=True)
        actualizar_paginas(posts_actualizados)
        crear_pagina_privacidad()
        crear_pagina_acerca_de()
        crear_pagina_contacto()
        print("\n🎉 ¡Proceso completado!")
    else:
        print("\n❌ No se pudo generar contenido. La ejecución fallará.", file=sys.stderr)
        sys.exit(1)
