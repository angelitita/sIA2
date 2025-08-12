print("--- EJECUTANDO SCRIPT v4 'EL PERIODISTA' ---")
import os
import google.generativeai as genai
import datetime
import json
from pathlib import Path
import sys

# --- Configuración ---
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
    
    # --- NUEVO PROMPT INTELIGENTE ---
    prompt = """
    Actúa como un periodista de tecnología para el portal de noticias 'sIA', especializado en el impacto de la Inteligencia Artificial en Latinoamérica.
    Tu tarea es generar UN SOLO artículo de noticias. Para ello, utiliza tu conocimiento sobre eventos recientes, tendencias (como las de Google Trends) y anuncios de empresas tecnológicas en la región para encontrar un tema de actualidad.
    El artículo debe ser una noticia concisa, relevante y actual. No debe ser una página web completa, sino el contenido de un post individual para nuestro sitio.

    REGLAS ESTRICTAS PARA TU RESPUESTA:
    1.  El cuerpo del artículo DEBE tener entre 350 y 550 palabras.
    2.  El HTML generado debe ser simple. Usa únicamente etiquetas <p>, <h2>, y <h3>.
    3.  NO incluyas imágenes ni etiquetas <img>.
    4.  El 'slug' para la URL debe ser corto, en minúsculas y relevante al título.
    5.  Tu respuesta final debe ser EXCLUSIVAMENTE un objeto JSON válido, sin texto adicional.

    La estructura del JSON debe ser:
    {
      "title": "Un titular de noticia atractivo y actual",
      "summary": "Un resumen corto de 1-2 frases del artículo.",
      "category": "Una de las siguientes: 'Noticias', 'Análisis', 'IA para Todos'",
      "content_html": "El cuerpo completo del artículo en HTML, respetando el límite de palabras.",
      "slug": "un-slug-para-la-url-basado-en-el-titulo"
    }
    """
    
    try:
        print("🤖 Actuando como periodista y generando nuevo contenido...")
        response = model.generate_content(prompt)
        json_response = response.text.strip().replace("```json", "").replace("```", "")
        contenido = json.loads(json_response)
        print(f"✅ Contenido generado con éxito: '{contenido['title']}'")
        return contenido
    except Exception as e:
        print(f"❌ Error al generar contenido: {e}")
        return None

def crear_archivo_post(contenido):
    """Crea un nuevo archivo HTML para el post a partir de una plantilla."""
    
    POSTS_DIR.mkdir(exist_ok=True)

    with open(TEMPLATES_DIR / "template_article.html", "r", encoding="utf-8") as f:
        template_str = f.read()

    fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
    template_str = template_str.replace("{{TITULO}}", contenido["title"])
    template_str = template_str.replace("{{FECHA}}", fecha_actual)
    template_str = template_str.replace("{{CATEGORIA}}", contenido["category"])
    template_str = template_str.replace("{{CONTENIDO_HTML}}", contenido["content_html"])
    
    nombre_archivo = f"{datetime.date.today().strftime('%Y-%m-%d')}-{contenido['slug']}.html"
    ruta_archivo = POSTS_DIR / nombre_archivo

    with open(ruta_archivo, "w", encoding="utf-8") as f:
        f.write(template_str)
    
    print(f"📄 Archivo de post creado en: {ruta_archivo}")

def actualizar_index():
    """Actualiza la página index.html con los últimos posts."""
    
    print("🔄 Actualizando la página de inicio (index.html)...")
    
    posts = sorted(POSTS_DIR.glob("*.html"), key=os.path.getmtime, reverse=True)
    
    grid_html = ""
    for post_path in posts[:10]:
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

    with open(TEMPLATES_DIR / "template_index.html", "r", encoding="utf-8") as f:
        index_template_str = f.read()

    index_template_str = index_template_str.replace("", hero_html)
    index_template_str = index_template_str.replace("", grid_html)

    with open(ROOT_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(index_template_str)
        
    print(f"✅ index.html actualizado con los últimos posts. Tamaño: {os.path.getsize(ROOT_DIR / 'index.html') / 1024:.2f} KB")


# --- Ejecución Principal ---
if __name__ == "__main__":
    if not TEMPLATES_DIR.exists() or not (TEMPLATES_DIR / "template_article.html").exists() or not (TEMPLATES_DIR / "template_index.html").exists():
        print(f"❌ Error Crítico: La carpeta '{TEMPLATES_DIR}' o uno de sus archivos de plantilla no existe. Abortando.")
        sys.exit(1)

    contenido_nuevo = generar_contenido_ia()
    
    if contenido_nuevo:
        # ---- VERIFICACIÓN DE SEGURIDAD ----
        if len(contenido_nuevo.get("content_html", "")) > 15000:
            print(f"❌ ERROR CRÍTICO: El contenido generado es demasiado largo ({len(contenido_nuevo.get('content_html', ''))} caracteres). Abortando.")
            sys.exit(1)

        crear_archivo_post(contenido_nuevo)
        actualizar_index()
        print("\n🎉 ¡Proceso completado! Un nuevo post ha sido creado y la página de inicio está actualizada.")
