print("--- EJECUTANDO SCRIPT v10: RESTAURANDO DISEÑO CON PRUEBA ---")
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
    """Genera contenido de prueba SIN llamar a la IA."""
    print("⚙️ Generando contenido de prueba localmente...")
    contenido = {
      "title": "¡El Sistema Funciona!",
      "summary": "Este post fue generado automáticamente para probar que el diseño y la estructura del sitio funcionan correctamente.",
      "category": "Noticias",
      "content_html": "<p>Este es el cuerpo del artículo de prueba. Fue generado para verificar que el sistema de creación de archivos, el uso de plantillas, el commit y el despliegue funcionan correctamente sin depender de una API externa.</p><h2>Siguientes Pasos</h2><p>El próximo paso será reactivar la conexión con la Inteligencia Artificial para generar contenido real.</p>",
      "slug": f"post-prueba-exitoso-{datetime.datetime.now().strftime('%H-%M-%S')}"
    }
    print("✅ Contenido de prueba generado.")
    return contenido

def crear_archivo_post(contenido):
    """Crea un nuevo archivo HTML para el post usando la plantilla."""
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
    """Actualiza la página index.html con los últimos posts usando la plantilla."""
    print("🔄 Actualizando la página de inicio (index.html)...")
    posts = sorted(POSTS_DIR.glob("*.html"), key=os.path.getmtime, reverse=True)
    grid_html = ""
    for post_path in posts[:10]:
        title_from_slug = "Post de Prueba" # Simplificado para la prueba
        card_html = f"""
        <article class="article-card">
            <a href="{post_path.as_posix()}"><img src="https://via.placeholder.com/300x180.png?text=sIA" alt="Imagen del artículo"></a>
            <div class="card-content">
                <span class="category-tag">Pruebas</span>
                <h3><a href="{post_path.as_posix()}">{title_from_slug}</a></h3>
            </div>
        </article>
        """
        grid_html += card_html
    hero_html = ""
    if posts:
        hero_post_path = posts[0]
        hero_title = "¡El Sistema Funciona!" # Simplificado para la prueba
        hero_html = f"""
        <section class="hero-article">
            <h2><a href="{hero_post_path.as_posix()}">{hero_title}</a></h2>
            <p>Este es el artículo más reciente generado automáticamente. El sistema de despliegue y diseño está funcionando.</p>
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
    contenido_nuevo = generar_contenido_de_prueba()
    if contenido_nuevo:
        crear_archivo_post(contenido_nuevo)
        actualizar_index()
        print("\n🎉 ¡Proceso de restauración de diseño completado!")
