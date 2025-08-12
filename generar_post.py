print("--- EJECUTANDO SCRIPT v8 DE PRUEBA (SIN IA) ---")
import os
import datetime
import json
from pathlib import Path
import sys

# --- Rutas de las carpetas ---
POSTS_DIR = Path("posts")
TEMPLATES_DIR = Path("templates")
ROOT_DIR = Path(".")

# --- Funciones ---

def generar_contenido_de_prueba():
    """Esta función ahora genera contenido de prueba SIN llamar a la IA."""
    print("⚙️ Generando contenido de prueba localmente (SIN API).")
    try:
        contenido = {
          "title": "Este es un Post de Prueba",
          "summary": "Si ves esto, la automatización de archivos funciona.",
          "category": "Pruebas",
          "content_html": "<p>Este es el cuerpo del artículo de prueba. Fue generado para verificar que el sistema de creación de archivos, commit y despliegue funciona correctamente sin depender de una API externa.</p><h2>Subtítulo de prueba</h2><p>Más texto de prueba para confirmar el funcionamiento.</p>",
          "slug": f"post-de-prueba-{datetime.datetime.now().strftime('%H-%M-%S')}"
        }
        print("✅ Contenido de prueba generado.")
        return contenido
    except Exception as e:
        print(f"❌ Error al generar contenido de prueba: {e}")
        return None

def crear_archivo_post(contenido):
    """Crea un nuevo archivo HTML para el post."""
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
    if not TEMPLATES_DIR.exists():
        sys.exit(f"❌ Error Crítico: La carpeta de plantillas '{TEMPLATES_DIR}' no se encuentra.")
    
    contenido_nuevo = generar_contenido_de_prueba()
    
    if contenido_nuevo:
        crear_archivo_post(contenido_nuevo)
        actualizar_index()
        print("\n🎉 ¡Proceso de prueba completado!")
