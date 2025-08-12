print("--- EJECUTANDO SCRIPT v7 'SOLO TEXTO' ---")
import os
import datetime
import json
from pathlib import Path
import sys
from groq import Groq

# --- Configuración ---
from dotenv import load_dotenv
load_dotenv()

try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    print("✅ Cliente de Groq configurado.")
except Exception as e:
    print(f"❌ Error al configurar el cliente de Groq: {e}")
    sys.exit(1)

# Rutas de las carpetas
POSTS_DIR = Path("posts")
TEMPLATES_DIR = Path("templates")
ROOT_DIR = Path(".")

# --- Funciones ---

def generar_contenido_ia():
    """Pide a la IA que genere ÚNICAMENTE el texto para un artículo."""
    
    prompt = "Escribe un artículo de 3 párrafos sobre una noticia de actualidad de Inteligencia Artificial en Latinoamérica."
    
    try:
        print("🤖 Pidiendo solo el texto del artículo a la API de Groq...")
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            max_tokens=1024,
        )

        response_text = chat_completion.choices[0].message.content
        
        # El script ahora crea la estructura, no la IA
        # Primero preparamos el texto HTML
        texto_html = response_text.replace('\n', '</p><p>')
        
        # Luego creamos el diccionario de contenido
        contenido = {
          "title": "Un Nuevo Avance en la IA de Latinoamérica",
          "summary": "Descubre las últimas innovaciones y cómo están cambiando la región.",
          "category": "Noticias",
          "content_html": f"<p>{texto_html}</p>",
          "slug": "nuevo-avance-ia-latam"
        }

        print(f"✅ Texto recibido y estructura JSON creada localmente.")
        return contenido
        
    except Exception as e:
        print(f"❌ Error al generar contenido con Groq: {e}")
        return None

# El resto del código no necesita cambios.
# Aquí se pega completo para asegurar que no haya errores.
def crear_archivo_post(contenido):
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

if __name__ == "__main__":
    if not TEMPLATES_DIR.exists():
        sys.exit(f"❌ Error Crítico: La carpeta de plantillas '{TEMPLATES_DIR}' no se encuentra.")
    contenido_nuevo = generar_contenido_ia()
    if contenido_nuevo:
        crear_archivo_post(contenido_nuevo)
        actualizar_index()
        print("\n🎉 ¡Proceso completado!")

