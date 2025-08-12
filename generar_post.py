print("--- EJECUTANDO SCRIPT v11 'AUTOCONTENIDO' ---")
import os
import datetime
import json
from pathlib import Path
import sys
from groq import Groq

# --- Configuración de Groq ---
try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    print("✅ Cliente de Groq configurado.")
except Exception as e:
    sys.exit(f"❌ Error al configurar el cliente de Groq: {e}")

# --- Rutas de las carpetas ---
POSTS_DIR = Path("posts")
ROOT_DIR = Path(".")

# --- Plantillas HTML como strings de Python ---
HTML_HEADER = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="{css_path}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <div class="logo">
            <img src="{logo_path}" alt="sIA Logo">
            <h1><a href="{index_path}">sIA</a></h1>
        </div>
        <nav>
            <ul>
                <li><a href="#">Noticias</a></li><li><a href="#">Análisis</a></li>
                <li><a href="#">IA para Todos</a></li><li><a href="#">Herramientas IA</a></li>
                <li><a href="#">Opinión</a></li>
            </ul>
        </nav>
        <a href="#" class="subscribe-button">Suscríbete</a>
    </header>
"""

HTML_FOOTER = """
    <footer>
        <p>&copy; 2025 sIA. Todos los derechos reservados.</p>
        <p><a href="#">Política de Privacidad</a></p>
    </footer>
</body>
</html>
"""

# --- Funciones ---

def generar_contenido_ia():
    """Genera el contenido para un artículo usando Groq."""
    print("🤖 Generando contenido con la API de Groq...")
    prompt = "Escribe un artículo de 3 párrafos sobre una noticia de actualidad de Inteligencia Artificial en Latinoamérica."
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192", max_tokens=1024
        )
        response_text = chat_completion.choices[0].message.content
        
        # El script crea la estructura del contenido
        contenido = {
          "title": "Avances de IA en Latinoamérica",
          "summary": "Un resumen de las últimas noticias generadas por IA.",
          "category": "Noticias",
          "content_html": f"<h2>Avances de IA en Latinoamérica</h2><p>{response_text.replace(chr(10), '</p><p>')}</p>",
          "slug": f"avance-ia-latam-{datetime.datetime.now().strftime('%H-%M-%S')}"
        }
        print("✅ Contenido generado con éxito.")
        return contenido
    except Exception as e:
        sys.exit(f"❌ Error al generar contenido con Groq: {e}")

def crear_archivo_post(contenido):
    """Crea un nuevo archivo HTML para el post."""
    POSTS_DIR.mkdir(exist_ok=True)
    fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
    
    article_content = f"""
    <article class="article-body">
        <h1 class="article-title">{contenido['title']}</h1>
        <p class="article-meta">Publicado por Redacción sIA el {fecha_actual} en <span class="category-tag">{contenido['category']}</span></p>
        <div class="article-content">{contenido['content_html']}</div>
    </article>
    """
    
    # Ensamblar el HTML completo del artículo
    full_html = (
        HTML_HEADER.format(title=contenido['title'], css_path="../static/css/style.css", logo_path="../static/img/logo.jpg", index_path="../index.html") +
        article_content +
        HTML_FOOTER
    )
    
    nombre_archivo = f"{datetime.date.today().strftime('%Y-%m-%d')}-{contenido['slug']}.html"
    ruta_archivo = POSTS_DIR / nombre_archivo

    with open(ruta_archivo, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"📄 Archivo de post creado en: {ruta_archivo}")

def actualizar_index():
    """Actualiza la página index.html con los últimos posts."""
    print("🔄 Actualizando la página de inicio (index.html)...")
    posts = sorted(POSTS_DIR.glob("*.html"), key=os.path.getmtime, reverse=True)
    
    grid_html = ""
    for post_path in posts[:10]:
        title = post_path.stem[11:].replace("-", " ").title()
        card_html = f"""<article class="article-card">
            <a href="{post_path.as_posix()}"><img src="https://via.placeholder.com/300x180.png?text=sIA" alt="Imagen del artículo"></a>
            <div class="card-content">
                <span class="category-tag">Noticias</span>
                <h3><a href="{post_path.as_posix()}">{title}</a></h3>
            </div>
        </article>"""
        grid_html += card_html

    hero_html = ""
    if posts:
        hero_title = posts[0].stem[11:].replace("-", " ").title()
        hero_html = f"""<section class="hero-article">
            <h2><a href="{posts[0].as_posix()}">{hero_title}</a></h2>
            <p>Este es el artículo más reciente generado por nuestra IA.</p>
        </section>"""
        
    index_main_content = f"""
    <main>
        {hero_html}
        <div class="content-area">
            <div class="article-grid">{grid_html}</div>
            <aside class="sidebar">
                <div class="widget"><h3>Lo Más Leído</h3></div>
                <div class="widget"><h3>Herramientas IA Destacadas</h3></div>
            </aside>
        </div>
    </main>
    """
    
    # Ensamblar el HTML completo del index
    full_html = (
        HTML_HEADER.format(title="sIA - Inteligencia Artificial en Latinoamérica", css_path="static/css/style.css", logo_path="static/img/logo.jpg", index_path="index.html") +
        index_main_content +
        HTML_FOOTER
    )

    with open(ROOT_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"✅ index.html actualizado. Tamaño: {os.path.getsize(ROOT_DIR / 'index.html') / 1024:.2f} KB")

# --- Ejecución Principal ---
if __name__ == "__main__":
    contenido_nuevo = generar_contenido_ia()
    if contenido_nuevo:
        crear_archivo_post(contenido_nuevo)
        actualizar_index()
        print("\n🎉 ¡Proceso completado!")
