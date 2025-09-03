# --- EJECUTANDO SCRIPT v20.0 (Optimizado con validaciones, SEO, caching, concurrencia) ---
import os
import datetime
import json
from pathlib import Path
import sys
import random
import feedparser
import concurrent.futures
from groq import Groq
from bs4 import BeautifulSoup
import re
from html import escape

print("--- INICIANDO SCRIPT DE GENERACIÓN DE CONTENIDO v20.0 ---")

# --- CONFIGURACIÓN ---
CUSDIS_APP_ID = "f6cbff1c-928c-4ac4-b85a-c76024284179"
RSS_FEEDS = [
    "https://www.infobae.com/feeds/rss/america/tecno/",
    "https://es.wired.com/feed/rss",
    "https://www.xataka.com/tag/inteligencia-artificial/feed/",
]
HISTORIAL_FILE = Path("historial_noticias.txt")
IMG_CACHE_FILE = Path("img_cache.json")
IMG_DIR = Path("static/img")
POSTS_DIR = Path("posts")
ROOT_DIR = Path(".")
SITE_TITLE = "sIA"
SITE_DESC = "Noticias y análisis sobre IA en Latinoamérica."
SITE_URL = "https://sia2news.netlify.app"  # ajusta si cambia

# --- CLIENTE GROQ ---
try:
    api_key_main = os.getenv("GROQ_API_KEY")
    if not api_key_main:
        sys.exit("❌ Error: GROQ_API_KEY no configurada.")
    client_groq = Groq(api_key=api_key_main)
    print("✅ Cliente de Groq configurado.")
except Exception as e:
    sys.exit(f"❌ Error al configurar cliente de Groq: {e}")

# --- IMÁGENES DISPONIBLES ---
extensions = [".png", ".jpg", ".jpeg", ".webp"]
LISTA_DE_IMAGENES = [
    f.name for f in IMG_DIR.glob("*") if f.suffix.lower() in extensions and f.name != "logo.png"
]
if not LISTA_DE_IMAGENES:
    LISTA_DE_IMAGENES = ["logo.png"]

# cache de imágenes por slug
def _load_img_cache():
    if IMG_CACHE_FILE.exists():
        try:
            with open(IMG_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

IMG_CACHE = _load_img_cache()

# --- HELPERS ---
def slugify(text: str) -> str:
    """Convierte un título en un slug seguro para URLs."""
    text = text.lower()
    text = re.sub(r"[áàä]", "a", text)
    text = re.sub(r"[éèë]", "e", text)
    text = re.sub(r"[íìï]", "i", text)
    text = re.sub(r"[óòö]", "o", text)
    text = re.sub(r"[úùü]", "u", text)
    text = re.sub(r"ñ", "n", text)
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")[:80]


def load_json_safe(content: str):
    """Valida y carga JSON de forma robusta: intenta extraer el primer objeto JSON válido."""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.S)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                return None
        return None


def sanitize_html(html: str) -> str:
    """Filtra etiquetas potencialmente peligrosas; mantiene estructura básica."""
    try:
        soup = BeautifulSoup(html or "", "html.parser")
        # Elimina scripts/iframes/style
        for tag in soup(["script", "iframe", "style", "object", "embed"]):
            tag.decompose()
        return str(soup)
    except Exception:
        return escape(html or "")


# --- PLANTILLAS HTML SEO/Accesibilidad ---
HTML_HEADER = """<!DOCTYPE html><html lang=\"es\"><head><meta charset=\"UTF-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
<title>{title}</title><meta name=\"description\" content=\"{summary}\">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6306514511826618" crossorigin="anonymous"></script>
<!-- SEO OpenGraph -->
<meta property=\"og:title\" content=\"{title}\">
<meta property=\"og:description\" content=\"{summary}\">
<meta property=\"og:image\" content=\"/static/img/logo.png\">
<meta property=\"og:type\" content=\"article\">
<meta property=\"og:site_name\" content=\"{site}\">
<meta name=\"twitter:card\" content=\"summary_large_image\">
<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
<link rel=\"stylesheet\" href=\"/static/css/style.css\">
<link rel=\"icon\" href=\"/static/img/logo.png\" type=\"image/png\"></head>
<body>
<header role=\"banner\">
    <div class=\"logo\"><img src=\"/static/img/logo.png\" alt=\"Logo de sIA\"><h1><a href=\"/index.html\">sIA</a></h1></div>
    <nav class=\"desktop-nav\" role=\"navigation\" aria-label=\"Menú principal\">
        <ul>
            <li><a href=\"/noticias.html\">Noticias</a></li>
            <li><a href=\"/herramientas-ia.html\">Herramientas IA</a></li>
            <li><a href=\"/opinion.html\">Opinión</a></li>
        </ul>
    </nav>
    <a href=\"https://docs.google.com/forms/d/e/1FAIpQLSeNl4keU0p1eDMvzUpM5p57Naf5qBMsl5MSJNBMxPnWbofshQ/viewform?usp=header\" 
       target=\"_blank\" class=\"subscribe-button desktop-nav\">Suscríbete</a>
    <button class=\"hamburger-menu\" aria-label=\"Abrir menú\"><span></span></button>
</header>
<div class=\"mobile-nav\" role=\"navigation\" aria-label=\"Menú móvil\">
    <nav><ul>
        <li><a href=\"/noticias.html\">Noticias</a></li>
        <li><a href=\"/herramientas-ia.html\">Herramientas IA</a></li>
        <li><a href=\"/opinion.html\">Opinión</a></li>
        <li><a href=\"/acerca-de.html\">Acerca de</a></li>
        <li><a href=\"/contacto.html\">Contacto</a></li>
    </ul></nav>
    <a href=\"https://docs.google.com/forms/d/e/1FAIpQLSeNl4keU0p1eDMvzUpM5p57Naf5qBMsl5MSJNBMxPnWbofshQ/viewform?usp=header\" target=\"_blank\" class=\"subscribe-button\">Suscríbete</a>
</div>"""

HTML_FOOTER = """<footer><p>&copy; 2025 sIA. Todos los derechos reservados.</p>
<p><a href=\"/privacy.html\">Política de Privacidad</a> | <a href=\"/acerca-de.html\">Acerca de</a> | <a href=\"/contacto.html\">Contacto</a></p></footer>
<script>
const hamburger = document.querySelector('.hamburger-menu');
const mobileNav = document.querySelector('.mobile-nav');
const body = document.querySelector('body');
hamburger.addEventListener('click', () => {{
    hamburger.classList.toggle('is-active');
    mobileNav.classList.toggle('is-active');
    body.classList.toggle('no-scroll');
}});
</script></body></html>"""

PRIVACY_POLICY_CONTENT = """<main class=\"article-body\" style=\"margin-top: 2rem;\"><h1 class=\"article-title\">Política de Privacidad</h1><div class=\"article-content\"><p><strong>Fecha de vigencia:</strong> 26 de agosto de 2025</p><p>En sIA (\"nosotros\", \"nuestro\"), respetamos su privacidad y nos comprometemos a protegerla. Esta Política de Privacidad explica cómo recopilamos, utilizamos y salvaguardamos su información cuando visita nuestro sitio web sia2news.netlify.app.</p><h2>1. Información que Recopilamos</h2><ul><li><strong>Datos no personales:</strong> Recopilamos datos anónimos que los navegadores ponen a disposición, como el tipo de navegador y el país de origen. Esto se utiliza para fines estadísticos a través de herramientas como Netlify Analytics.</li><li><strong>Información de contacto voluntaria:</strong> Si utiliza nuestro formulario de contacto, recopilaremos el nombre y el correo electrónico que nos proporcione para poder responder a su consulta.</li></ul><h2>2. Uso de Cookies y Publicidad de Terceros</h2><p>Este sitio utiliza cookies para mejorar la experiencia. Participamos en programas de publicidad y afiliados.</p><ul><li><strong>Google AdSense:</strong> Google utiliza cookies para publicar anuncios basados en las visitas anteriores de un usuario a este u otros sitios web. Puede inhabilitar la publicidad personalizada visitando la <a href=\"https://adssettings.google.com/authenticated\" target=\"_blank\" rel=\"noopener noreferrer\">Configuración de anuncios de Google</a>.</li></ul><h2>3. Formularios y Comentarios</h2><ul><li><strong>Formulario de Contacto:</strong> La información enviada es gestionada por Netlify Forms y se utiliza únicamente para responder a sus consultas.</li><li><strong>Comentarios:</strong> Utilizamos un servicio de terceros (Cusdis) para gestionar los comentarios. Puede comentar de forma anónima. La información que publique será pública.</li></ul><h2>4. Contacto</h2><p>Si tiene alguna pregunta sobre esta Política, puede contactarnos a través de nuestra <a href=\"/contacto.html\">página de contacto</a>.</p></div></main>"""

ACERCA_DE_CONTENT = """<main class=\"article-body\" style=\"margin-top: 2rem;\"><h1 class=\"article-title\">Acerca de sIA</h1><div class=\"article-content\"><h2>Nuestra Misión</h2><p>Nuestra misión es ser la fuente de información de referencia para entusiastas y profesionales de la IA en Latinoamérica. A través de un sistema de curación y generación de contenido automatizado, buscamos mantener a nuestra audiencia al día sobre las últimas tendencias y herramientas que moldean el futuro de la inteligencia artificial.</p></div></main>"""

CONTACTO_CONTENT = """<main class=\"article-body\" style=\"margin-top: 2rem;\"><h1 class=\"article-title\">Contacto</h1><div class=\"article-content\"><p>¿Tienes alguna pregunta, sugerencia o quieres colaborar? Utiliza el formulario a continuación.</p><form name=\"contact\" method=\"POST\" data-netlify=\"true\" class=\"contact-form\"><div class=\"form-group\"><label for=\"name\">Nombre:</label><input type=\"text\" id=\"name\" name=\"name\" required></div><div class=\"form-group\"><label for=\"email\">Email:</label><input type=\"email\" id=\"email\" name=\"email\" required></div><div class=\"form-group\"><label for=\"message\">Mensaje:</label><textarea id=\"message\" name=\"message\" rows=\"6\" required></textarea></div><button type=\"submit\" class=\"subscribe-button\">Enviar Mensaje</button></form><h2>Otras formas de contactar</h2><p>También puedes encontrarnos en Twitter: <a href=\"https://x.com/sIAnoticiastec\" target=\"_blank\" rel=\"noopener noreferrer\"><strong>@sIAnoticiastec</strong></a></p></div></main>"""

# --- RSS con concurrencia ---
def fetch_feed(url):
    try:
        return feedparser.parse(url)
    except Exception:
        return None


def obtener_noticia_real_de_rss():
    print("📡 Buscando noticias reales en RSS...")
    if not HISTORIAL_FILE.exists():
        HISTORIAL_FILE.touch()
    with open(HISTORIAL_FILE, "r", encoding="utf-8") as f:
        historial = [line.strip() for line in f.readlines()]
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(8, len(RSS_FEEDS) or 1)) as executor:
        feeds = list(executor.map(fetch_feed, RSS_FEEDS))
    for feed in feeds:
        if feed and getattr(feed, "entries", None):
            for noticia in feed.entries[:5]:
                link = getattr(noticia, "link", None)
                title = getattr(noticia, "title", None)
                if not link or not title:
                    continue
                if link in historial:
                    continue
                resumen_raw = getattr(noticia, "summary", "")
                resumen = BeautifulSoup(resumen_raw, "html.parser").get_text(" ", strip=True)
                print(f"✅ Noticia real encontrada: '{title}'")
                return {"titulo": title, "link": link, "resumen": resumen}
    return None


# --- IA con validación JSON ---
def generar_contenido_ia(categoria, tema):
    print(f"🤖 Generando contenido IA para '{categoria}'...")
    system_prompt = (
        f"Eres un experto en IA para el blog '{SITE_TITLE}'. Escribe un artículo de '{categoria}'. "
        f"El artículo DEBE estar en español. Devuelve JSON con keys: title, summary, content_html."
    )
    user_prompt = f"""Escribe un artículo sobre: '{tema}'. Formato JSON: {{"title": "...", "summary": "...", "content_html": "..."}}"""
    try:
        chat_completion = client_groq.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            model="llama3-8b-8192",
            response_format={"type": "json_object"},
        )
        contenido = load_json_safe(chat_completion.choices[0].message.content)
        if contenido:
            contenido["category"] = categoria
            contenido["content_html"] = sanitize_html(contenido.get("content_html", ""))
        return contenido
    except Exception as e:
        print(f"❌ Error al generar contenido IA: {e}", file=sys.stderr)
        return None


def reescribir_noticia_con_ia(noticia):
    print("🤖 Reescribiendo noticia real con IA...")
    system_prompt = (
        f"Eres un periodista para '{SITE_TITLE}'. Reescribe noticias en un artículo original y atractivo. "
        f"DEBE estar en español. Devuelve JSON con keys: title, summary, content_html."
    )
    user_prompt = (
        f"Basado en: Título: \"{noticia['titulo']}\", Resumen: \"{noticia['resumen']}\", "
        f"Fuente: \"{noticia['link']}\". Escribe un artículo. Formato JSON: "
        f"{{\"title\": \"...\", \"summary\": \"...\", \"content_html\": \"...\"}}"
    )
    try:
        chat_completion = client_groq.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            model="llama3-8b-8192",
            response_format={"type": "json_object"},
        )
        contenido = load_json_safe(chat_completion.choices[0].message.content)
        if contenido:
            contenido["source_link"] = noticia["link"]
            contenido["category"] = "Noticias"
            contenido["content_html"] = sanitize_html(contenido.get("content_html", ""))
        return contenido
    except Exception as e:
        print(f"❌ Error al reescribir noticia: {e}", file=sys.stderr)
        return None


# --- Caching de imagen por slug ---
def save_img_cache():
    try:
        with open(IMG_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(IMG_CACHE, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ No se pudo guardar img_cache: {e}")


def asignar_imagen(slug: str):
    if slug in IMG_CACHE:
        return IMG_CACHE[slug]
    imagen = random.choice(LISTA_DE_IMAGENES)
    IMG_CACHE[slug] = imagen
    save_img_cache()
    return imagen


# --- Utilidades de posts ---
def get_post_details(file_path: Path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
        title_tag = soup.find("h1", class_="article-title")
        title = title_tag.get_text(strip=True) if title_tag else "Sin Título"
        category_tag = soup.find("span", class_="category-tag")
        category = category_tag.get_text(strip=True) if category_tag else "Noticias"
        return title, category
    except Exception:
        return "Sin Título", "Noticias"


def crear_archivo_post(contenido: dict, todos_los_posts):
    POSTS_DIR.mkdir(exist_ok=True)
    fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
    title = contenido.get("title", "Sin título").strip() or "Sin título"
    summary = contenido.get("summary", "")
    category = contenido.get("category", "Noticias")

    slug_base = slugify(title)
    timestamp = datetime.datetime.now().strftime("%H%M%S")
    slug = f"{slug_base}-{timestamp}"
    nombre_archivo = f"{datetime.date.today().strftime('%Y-%m-%d')}-{slug}.html"

    # imagen consistente por slug
    imagen_aleatoria = asignar_imagen(slug_base)

    # posts relacionados
    posts_relacionados = [p for p in todos_los_posts if p.name != nombre_archivo]
    random.shuffle(posts_relacionados)
    posts_relacionados = posts_relacionados[:3]

    def card_html(post_path: Path):
        t, c = get_post_details(post_path)
        if t == "Sin Título":
            return ""
        related_slug = slugify(t)
        img_rel = asignar_imagen(related_slug)
        return (
            f"<article class=\"article-card\">"
            f"<a href=\"/{post_path.as_posix()}\">"
            f"<img src=\"/static/img/{img_rel}\" alt=\"{escape(t)}\"></a>"
            f"<div class=\"card-content\"><span class=\"category-tag {c.replace(' ', '-')}\">{c}</span>"
            f"<h3><a href=\"/{post_path.as_posix()}\">{escape(t)}</a></h3></div></article>"
        )

    cards_html = "".join(card_html(p) for p in posts_relacionados if p)
    related_posts_html = (
        f"<section class=\"related-articles\"><h2>Artículos que podrían interesarte</h2>"
        f"<div class=\"article-grid\">{cards_html}</div></section>" if cards_html else ""
    )

    comments_section_html = (
        f"<section class=\"comments-section\"><h2>Comentarios</h2>"
        f"<div id=\"cusdis_thread\" data-host=\"https://cusdis.com\" data-app-id=\"{CUSDIS_APP_ID}\" "
        f"data-page-id=\"{nombre_archivo}\" data-page-url=\"/posts/{nombre_archivo}\" data-page-title=\"{escape(title)}\"></div>"
        f"<script async defer src=\"https://cusdis.com/js/cusdis.es.js\"></script></section>"
    )

    source_html = (
        f"<p><em>Fuente original: <a href=\"{contenido.get('source_link', '#')}\" target=\"_blank\" rel=\"noopener noreferrer\">Leer más</a></em></p>"
        if "source_link" in contenido
        else ""
    )

    content_html = sanitize_html(contenido.get("content_html", ""))
    article_html = (
        f"<main class=\"article-body\"><article>"
        f"<h1 class=\"article-title\">{escape(title)}</h1>"
        f"<p class=\"article-meta\">Publicado por Redacción sIA el {fecha_actual} en "
        f"<span class=\"category-tag {category.replace(' ', '-')}\">{category}</span></p>"
        f"<figure class=\"cover-image\"><img src=\"/static/img/{imagen_aleatoria}\" alt=\"{escape(title)}\"></figure>"
        f"<div class=\"article-content\">{content_html}{source_html}</div>"
        f"</article>{comments_section_html}{related_posts_html}</main>"
    )

    full_html = HTML_HEADER.format(title=escape(title), summary=escape(summary), site=SITE_TITLE) + article_html + HTML_FOOTER

    with open(POSTS_DIR / nombre_archivo, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"📄 Archivo de post creado: {nombre_archivo}")

    if "source_link" in contenido:
        with open(HISTORIAL_FILE, "a", encoding="utf-8") as f:
            f.write(contenido["source_link"] + "\n")


def _crear_grid_html(posts, num_items):
    grid_html = ""
    for post_path in posts[:num_items]:
        title, category = get_post_details(post_path)
        if title:
            img = asignar_imagen(slugify(title))
            grid_html += (
                f"<article class=\"article-card\">"
                f"<a href=\"/{post_path.as_posix()}\">"
                f"<img src=\"/static/img/{img}\" alt=\"{escape(title)}\"></a>"
                f"<div class=\"card-content\"><span class=\"category-tag {category.replace(' ', '-')}\">{category}</span>"
                f"<h3><a href=\"/{post_path.as_posix()}\">{escape(title)}</a></h3></div></article>"
            )
    return grid_html


def actualizar_paginas(todos_los_posts):
    print("🔄 Actualizando páginas (index, categorías, etc.)...")
    posts_por_categoria = {"Noticias": [], "Herramientas IA": [], "Opinión": []}
    for post in todos_los_posts:
        title, category = get_post_details(post)
        if title != "Sin Título" and category in posts_por_categoria:
            posts_por_categoria[category].append(post)

    index_main_content = """<div class=\"main-container\">"""
    if posts_por_categoria["Noticias"]:
        index_main_content += (
            f"<h2 class=\"section-title\"><a href=\"/noticias.html\">Últimas Noticias</a></h2>"
            f"<div class=\"article-grid\">{_crear_grid_html(posts_por_categoria['Noticias'], 6)}</div>"
        )
    if posts_por_categoria["Herramientas IA"]:
        index_main_content += (
            f"<h2 class=\"section-title\"><a href=\"/herramientas-ia.html\">Herramientas IA</a></h2>"
            f"<div class=\"article-grid\">{_crear_grid_html(posts_por_categoria['Herramientas IA'], 3)}</div>"
        )
    if posts_por_categoria["Opinión"]:
        index_main_content += (
            f"<h2 class=\"section-title\"><a href=\"/opinion.html\">Opinión</a></h2>"
            f"<div class=\"article-grid\">{_crear_grid_html(posts_por_categoria['Opinión'], 3)}</div>"
        )
    index_main_content += "</div>"

    full_html_index = (
        HTML_HEADER.format(title=f"{SITE_TITLE} - Inteligencia Artificial en Latinoamérica", summary=SITE_DESC, site=SITE_TITLE)
        + index_main_content
        + HTML_FOOTER
    )
    with open(ROOT_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(full_html_index)

    for categoria, posts in posts_por_categoria.items():
        if posts:
            nombre_archivo = f"{categoria.lower().replace(' ', '-')}.html"
            grid_categoria = _crear_grid_html(posts, len(posts))
            main_categoria = (
                f"<div class=\"main-container\"><main class=\"main-content-full\">"
                f"<h1 class=\"page-title\">Artículos de {categoria}</h1>"
                f"<div class=\"article-grid\">{grid_categoria}</div>"
                f"</main></div>"
            )
            full_html_categoria = (
                HTML_HEADER.format(title=f"{categoria} - {SITE_TITLE}", summary=f"Artículos de {categoria}", site=SITE_TITLE)
                + main_categoria
                + HTML_FOOTER
            )
            with open(ROOT_DIR / nombre_archivo, "w", encoding="utf-8") as f:
                f.write(full_html_categoria)


# --- Páginas estáticas ---
def crear_pagina_privacidad():
    full_html = HTML_HEADER.format(title="Política de Privacidad - sIA", summary="Política de Privacidad de sIA News.", site=SITE_TITLE) + PRIVACY_POLICY_CONTENT + HTML_FOOTER
    with open(ROOT_DIR / "privacy.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print("✅ privacy.html creada/actualizada.")


def crear_pagina_acerca_de():
    full_html = HTML_HEADER.format(title="Acerca de - sIA", summary="Descubre la misión y el funcionamiento de sIA News.", site=SITE_TITLE) + ACERCA_DE_CONTENT + HTML_FOOTER
    with open(ROOT_DIR / "acerca-de.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print("✅ acerca-de.html creada/actualizada.")


def crear_pagina_contacto():
    full_html = HTML_HEADER.format(title="Contacto - sIA", summary="Contacta con el equipo de sIA News.", site=SITE_TITLE) + CONTACTO_CONTENT + HTML_FOOTER
    with open(ROOT_DIR / "contacto.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print("✅ contacto.html creada/actualizada.")


# --- Sitemap y RSS propio ---
def generar_sitemap(posts_files):
    print("🗺️ Generando sitemap.xml...")
    urls = [f"{SITE_URL}/index.html"]
    for p in posts_files:
        urls.append(f"{SITE_URL}/{p.as_posix()}")
    xml = [
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
        "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">",
    ]
    today = datetime.date.today().isoformat()
    for u in urls:
        xml.append("<url>")
        xml.append(f"<loc>{u}</loc>")
        xml.append(f"<lastmod>{today}</lastmod>")
        xml.append("<changefreq>daily</changefreq>")
        xml.append("<priority>0.7</priority>")
        xml.append("</url>")
    xml.append("</urlset>")
    (ROOT_DIR / "sitemap.xml").write_text("\n".join(xml), encoding="utf-8")


def generar_rss(posts_files):
    print("📻 Generando rss.xml...")
    items = []
    for p in sorted(posts_files, key=lambda x: x.name, reverse=True)[:20]:
        try:
            with open(p, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
            title = soup.find("h1", class_="article-title").get_text(strip=True)
            desc = soup.find("div", class_="article-content").get_text(" ", strip=True)[:300]
            link = f"{SITE_URL}/{p.as_posix()}"
            pubdate = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
            items.append(
                f"<item><title>{escape(title)}</title><link>{link}</link><description>{escape(desc)}</description><pubDate>{pubdate}</pubDate></item>"
            )
        except Exception:
            continue
    rss = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<rss version=\"2.0\"><channel>
<title>{SITE_TITLE}</title><link>{SITE_URL}</link><description>{SITE_DESC}</description>
{''.join(items)}
</channel></rss>"""
    (ROOT_DIR / "rss.xml").write_text(rss, encoding="utf-8")


# --- MAIN ---
if __name__ == "__main__":
    contenido_final = None

    # 1) Obtener noticia real o fallback a IA
    noticia_real = obtener_noticia_real_de_rss()
    if noticia_real:
        contenido_final = reescribir_noticia_con_ia(noticia_real)
    else:
        print("ℹ️ No hubo noticias reales nuevas, se generará contenido IA original.")
        temas_opinion = [
            "una columna de opinión sobre el Rabbit R1.",
            "un análisis crítico de las gafas Ray-Ban Meta.",
            "una opinión sobre Suno AI.",
        ]
        temas_herramientas = [
            "una comparativa detallada: Midjourney vs. Stable Diffusion.",
            "una guía de las 5 mejores IAs para editar video.",
            "una reseña a fondo de Notion AI.",
        ]
        categoria_ia, temas_ia = random.choice([
            ("Opinión", temas_opinion),
            ("Herramientas IA", temas_herramientas),
        ])
        tema_elegido = random.choice(temas_ia)
        if temas_ia:
            try:
                temas_ia.remove(tema_elegido)
            except ValueError:
                pass
        contenido_final = generar_contenido_ia(categoria_ia, tema_elegido)

    # 2) Crear post y actualizar páginas
    if contenido_final:
        posts_actuales = sorted(list(POSTS_DIR.glob("*.html")), key=lambda p: p.name, reverse=True)
        crear_archivo_post(contenido_final, posts_actuales)
        posts_actualizados = sorted(list(POSTS_DIR.glob("*.html")), key=lambda p: p.name, reverse=True)
        actualizar_paginas(posts_actualizados)

        # páginas estáticas
        crear_pagina_privacidad()
        crear_pagina_acerca_de()
        crear_pagina_contacto()

        # SEO: sitemap y rss
        generar_sitemap(posts_actualizados)
        generar_rss(posts_actualizados)

        print("\n🎉 ¡Proceso completado exitosamente!")
    else:
        print("\n❌ No se pudo generar ni encontrar contenido. La ejecución fallará.", file=sys.stderr)
        sys.exit(1)

