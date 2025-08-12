import os
import google.generativeai as genai
import datetime
import json
from pathlib import Path

# --- Configuración ---
# Carga la API Key desde un archivo .env para seguridad
# Crea un archivo llamado .env y pon: GEMINI_API_KEY="TU_API_KEY_AQUI"
from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Rutas de las carpetas
POSTS_DIR = Path("posts")
TEMPLATES_DIR = Path("templates")
ROOT_DIR = Path(".")

# --- Funciones ---

def generar_contenido_ia():
    """Genera el contenido de un nuevo artículo usando la API de Gemini."""
    
    # Prompt optimizado para obtener una respuesta estructurada en JSON
    prompt = """
    Actúa como un periodista experto en tecnología e inteligencia artificial, con un enfoque en Latinoamérica.
    Tu tarea es generar un artículo de noticias completo y original sobre un tema de actualidad en IA relevante para la región.
    
    Por favor, proporciona la respuesta exclusivamente en formato JSON con la siguiente estructura:
    {
      "title": "Un titular atractivo y optimizado para SEO",
      "summary": "Un resumen corto de 1-2 frases para la tarjeta de la página de inicio.",
      "category": "Una de las siguientes categorías: 'Noticias', 'Análisis', 'IA para Todos', 'Opinión'",
      "content_html": "El cuerpo completo del artículo en formato HTML. Usa párrafos <p>, subtítulos <h2> y <h3>, y listas <ul> o <ol> si es necesario. No incluyas etiquetas <html>, <head>, o <body>.",
      "slug": "un-slug-para-la-url-sin-espacios-y-en-minusculas"
    }
    
    Algunos temas de ejemplo para tu inspiración (pero crea algo nuevo):
    - El impacto de los nuevos modelos de lenguaje en las startups de Colombia.
    - La startup argentina que utiliza IA para optimizar la agricultura.
    - El debate sobre la regulación de la IA en Chile y México.
    - Un tutorial sencillo explicando qué es la 'IA generativa' para dueños de PYMES.
    """
    
    try:
        print("🤖 Generando nuevo contenido con la API de Gemini...")
        response = model.generate_content(prompt)
        # Limpiar la respuesta para que sea un JSON válido
        json_response = response.text.strip().replace("```json", "").replace("```", "")
        contenido = json.loads(json_response)
        print(f"✅ Contenido generado con éxito: '{contenido['title']}'")
        return contenido
    except Exception as e:
        print(f"❌ Error al generar contenido: {e}")
        return None

def crear_archivo_post(contenido):
    """Crea un nuevo archivo HTML para el post a partir de una plantilla."""
    
    # Cargar la plantilla del artículo
    with open(TEMPLATES_DIR / "template_article.html", "r", encoding="utf-8") as f:
        template_str = f.read()

    # Reemplazar los placeholders con el contenido de la IA
    fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
    template_str = template_str.replace("{{TITULO}}", contenido["title"])
    template_str = template_str.replace("{{FECHA}}", fecha_actual)
    template_str = template_str.replace("{{CATEGORIA}}", contenido["category"])
    template_str = template_str.replace("{{CONTENIDO_HTML}}", contenido["content_html"])
    
    # Crear el nombre del archivo
    nombre_archivo = f"{datetime.datetime.now().strftime('%Y-%m-%d')}-{contenido['slug']}.html"
    ruta_archivo = POSTS_DIR / nombre_archivo

    # Guardar el nuevo archivo HTML
    with open(ruta_archivo, "w", encoding="utf-8") as f:
        f.write(template_str)
    
    print(f"📄 Archivo de post creado en: {ruta_archivo}")

def actualizar_index():
    """Actualiza la página index.html con los últimos posts."""
    
    print("🔄 Actualizando la página de inicio (index.html)...")
    
    # Obtener la lista de todos los posts y ordenarlos por fecha (más nuevo primero)
    posts = sorted(POSTS_DIR.glob("*.html"), key=os.path.getmtime, reverse=True)
    
    # Generar el HTML para el grid de artículos
    grid_html = ""
    for i, post_path in enumerate(posts[:10]): # Limitar a los 10 más recientes
        # Para extraer el título, etc., necesitaríamos parsear el HTML.
        # Por simplicidad, usaremos el nombre del archivo como título temporal.
        # Una versión más avanzada usaría BeautifulSoup para parsear el título real.
        title_from_slug = post_path.stem[11:].replace("-", " ").title()
        
        card_html = f"""
        <article class="article-card">
            <a href="{post_path.as_posix()}"><img src="https://via.placeholder.com/300x180.png?text=sIA" alt="Imagen del artículo"></a>
            <div class="card-content">
                <span class="category-tag">Noticias</span>
                <h3><a href="{post_path.as_posix()}">{title_from_slug}</a></h3>
            </div>
        </article>
        """
        grid_html += card_html

    # Generar el HTML para el artículo Héroe (el más reciente)
    hero_html = ""
    if posts:
        hero_post_path = posts[0]
        hero_title = hero_post_path.stem[11:].replace("-", " ").title()
        hero_html = f"""
        <section class="hero-article">
            <h2><a href="{hero_post_path.as_posix()}">{hero_title}</a></h2>
            <p>Este es el artículo más reciente generado por nuestra IA. Explora las últimas tendencias y análisis del ecosistema de inteligencia artificial en la región.</p>
        </section>
        """

    # Cargar la plantilla del index
    with open(TEMPLATES_DIR / "template_index.html", "r", encoding="utf-8") as f:
        index_template_str = f.read()

    # Reemplazar los placeholders y guardar el nuevo index.html
    index_template_str = index_template_str.replace("", hero_html)
    index_template_str = index_template_str.replace("", grid_html)

    with open(ROOT_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(index_template_str)
        
    print("✅ index.html actualizado con los últimos posts.")


# --- Ejecución Principal ---
if __name__ == "__main__":
    contenido_nuevo = generar_contenido_ia()
    if contenido_nuevo:
        crear_archivo_post(contenido_nuevo)
        actualizar_index()
        print("\n🎉 ¡Proceso completado! Un nuevo post ha sido creado y la página de inicio está actualizada.")