# --- EJECUTANDO SCRIPT v19.5: MENÚ LIMPIO Y POLÍTICA DE PRIVACIDAD PROFESIONAL ---
import os
import datetime
import json
from pathlib import Path
import sys
import random
import feedparser
from groq import Groq
from bs4 import BeautifulSoup

print("--- INICIANDO SCRIPT DE GENERACIÓN DE CONTENIDO v19.5 ---")

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

# --- PLANTILLAS HTML (CON MENÚS CORREGIDOS) ---
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

# --- NUEVO: POLÍTICA DE PRIVACIDAD MÁS ROBUSTA ---
PRIVACY_POLICY_CONTENT = """
<main class="article-body" style="margin-top: 2rem;">
    <h1 class="article-title">Política de Privacidad</h1>
    <div class="article-content">
        <p><strong>Fecha de vigencia:</strong> 26 de agosto de 2025</p>
        <p>En sIA ("nosotros", "nuestro"), respetamos su privacidad y nos comprometemos a protegerla. Esta Política de Privacidad explica cómo recopilamos, utilizamos y salvaguardamos su información cuando visita nuestro sitio web sia2news.netlify.app.</p>
        
        <h2>1. Información que Recopilamos</h2>
        <p>Recopilamos información mínima para el funcionamiento del sitio:</p>
        <ul>
            <li><strong>Datos no personales:</strong> Al igual que la mayoría de los sitios web, recopilamos datos que los navegadores ponen a disposición, como el tipo de navegador, la preferencia de idioma y el país de origen. Esto se hace de forma anónima y se utiliza para fines estadísticos a través de herramientas como Netlify Analytics.</li>
            <li><strong>Información de contacto voluntaria:</strong> Si utiliza nuestro formulario de contacto, recopilaremos el nombre y el correo electrónico que nos proporcione para poder responder a su consulta.</li>
        </ul>

        <h2>2. Uso de Cookies y Publicidad de Terceros</h2>
        <p>Este sitio utiliza cookies para mejorar la experiencia del usuario. Además, para mantener el sitio, participamos en programas de publicidad y afiliados.</p>
        <ul>
            <li><strong>Google AdSense:</strong> Google, como proveedor externo, utiliza cookies (como la cookie de DoubleClick) para publicar anuncios basados en las visitas anteriores de un usuario a este u otros sitios web. Los usuarios pueden inhabilitar la publicidad personalizada visitando la <a href="https://adssettings.google.com/authenticated" target="_blank" rel="noopener noreferrer">Configuración de anuncios de Google</a>.</li>
            <li><strong>Marketing de Afiliados:</strong> Algunos de nuestros artículos pueden incluir enlaces de afiliados. Si hace clic en uno de estos enlaces y realiza una compra, podemos recibir una pequeña comisión sin costo adicional para usted.</li>
        </ul>

        <h2>3. Formularios y Comentarios</h2>
        <ul>
            <li><strong>Formulario de Contacto:</strong> La información enviada a través de nuestro formulario de contacto es gestionada por Netlify Forms y se utiliza únicamente para responder a sus consultas.</li>
            <li><strong>Comentarios:</strong> Utilizamos un servicio de terceros (Cusdis) para gestionar los comentarios. Puede comentar de forma anónima. La información que publique en esta sección será pública.</li>
        </ul>

        <h2>4. Derechos del Usuario (GDPR)</h2>
        <p>Si usted es residente del Espacio Económico Europeo (EEE), tiene ciertos derechos de protección de datos. Nos esforzamos por tomar medidas razonables para permitirle corregir, modificar, eliminar o limitar el uso de sus datos personales.</p>

        <h2>5. Seguridad de la Información</h2>
        <p>Tomamos medidas de seguridad razonables para proteger contra el acceso no autorizado o la alteración de la información. Sin embargo, ningún método de transmisión por Internet es 100% seguro.</p>

        <h2>6. Contacto</h2>
        <p>Si tiene alguna pregunta sobre esta Política de Privacidad, puede contactarnos a través de nuestra <a href="/contacto.html">página de contacto</a>.</p>
    </div>
</main>
"""

ACERCA_DE_CONTENT = """<main class="article-body" style="margin-top: 2rem;"><h1 class="article-title">Acerca de sIA</h1><div class="article-content"><h2>Nuestra Misión</h2><p>Nuestra misión es ser la fuente de información de referencia para entusiastas, profesionales y curiosos de la IA en Latinoamérica...</p></div></main>"""
CONTACTO_CONTENT = """<main class="article-body" style="margin-top: 2rem;"><h1 class="article-title">Contacto</h1><div class="article-content"><p>¿Tienes alguna pregunta, sugerencia o quieres colaborar? Utiliza el formulario a continuación.</p><form name="contact" method="POST" data-netlify="true" class="contact-form"><div class="form-group"><label for="name">Nombre:</label><input type="text" id="name" name="name" required></div><div class="form-group"><label for="email">Email:</label><input type="email" id="email" name="email" required></div><div class="form-group"><label for="message">Mensaje:</label><textarea id="message" name="message" rows="6" required></textarea></div><button type="submit" class="subscribe-button">Enviar Mensaje</button></form><h2>Otras formas de contactar</h2><p>También puedes encontrarnos en Twitter: <a href="https://x.com/sIAnoticiastec" target="_blank" rel="noopener noreferrer"><strong>@sIAnoticiastec</strong></a></p></div></main>"""

# --- LÓGICA DE CONTENIDO ---
def obtener_noticia_real_de_rss():
    pass
def generar_contenido_ia(categoria, tema):
    pass
def reescribir_noticia_con_ia(noticia):
    pass
# ... (El resto de las funciones de lógica y creación de páginas no han cambiado)
def get_post_details(file_path):
    pass
def crear_archivo_post(contenido, todos_los_posts):
    pass
def actualizar_paginas(todos_los_posts):
    pass
    
def crear_pagina_privacidad():
    full_html = HTML_HEADER.format(title="Política de Privacidad - sIA", summary="Política de Privacidad de sIA News.") + PRIVACY_POLICY_CONTENT + HTML_FOOTER
    with open(ROOT_DIR / "privacy.html", "w", encoding="utf-8") as f: f.write(full_html)
    print("✅ privacy.html creada/actualizada.")

def crear_pagina_acerca_de():
    full_html = HTML_HEADER.format(title="Acerca de - sIA", summary="Descubre la misión y el funcionamiento de sIA News.") + ACERCA_DE_CONTENT + HTML_FOOTER
    with open(ROOT_DIR / "acerca-de.html", "w", encoding="utf-8") as f: f.write(full_html)
    print("✅ acerca-de.html creada/actualizada.")

def crear_pagina_contacto():
    full_html = HTML_HEADER.format(title="Contacto - sIA", summary="Contacta con el equipo de sIA News.") + CONTACTO_CONTENT + HTML_FOOTER
    with open(ROOT_DIR / "contacto.html", "w", encoding="utf-8") as f: f.write(full_html)
    print("✅ contacto.html creada/actualizada.")

if __name__ == "__main__":
    # --- Flujo de Generación ---
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
    
    # --- Actualización de Páginas ---
    posts_actualizados = sorted(list(POSTS_DIR.glob("*.html")), key=lambda p: p.name, reverse=True)
    actualizar_paginas(posts_actualizados)
    crear_pagina_privacidad()
    crear_pagina_acerca_de()
    crear_pagina_contacto()
    print("\n🎉 ¡Proceso completado exitosamente!")
