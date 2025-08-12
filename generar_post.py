print("--- EJECUTANDO SCRIPT v6 CON API DE GROQ ---")
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
    # Configuración del cliente de Groq
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
    """Genera el contenido de un nuevo artículo usando la API de Groq."""
    
    # Prompt de sistema para darle un rol a la IA
    system_prompt = """
    Eres un periodista de tecnología para el portal de noticias 'sIA', especializado en el impacto de la Inteligencia Artificial en Latinoamérica.
    Tu respuesta debe ser EXCLUSIVAMENTE un objeto JSON válido, sin texto adicional, explicaciones o markdown.
    """

    # Prompt de usuario con las instrucciones
    user_prompt = """
    Por favor, genera UN SOLO artículo de noticias sobre un tema de actualidad en IA relevante para Latinoamérica.
    El artículo debe ser conciso, entre 350 y 550 palabras.
    El HTML debe ser simple, usando solo etiquetas <p>, <h2> y <h3>.
    NO incluyas imágenes.
    
    Usa la siguiente estructura JSON para tu respuesta:
    {
      "title": "Un titular de noticia atractivo y actual",
      "summary": "Un resumen corto de 1-2 frases del artículo.",
      "category": "Noticias",
      "content_html": "El cuerpo completo del artículo en HTML.",
      "slug": "un-slug-para-la-url-basado-en-el-titulo"
    }
    """
    
    try:
        print("🤖 Contactando la API de Groq para generar contenido...")
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
            model="llama3-8b-8192", # Un modelo rápido y eficiente
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stop=None,
            stream=False,
        )

        response_content = chat_completion.choices[0].message.content
        contenido = json.loads(response_content)
        print(f"✅ Contenido generado con éxito: '{contenido['title']}'")
        return contenido
        
    except Exception as e:
        print(f"❌ Error al generar contenido con Groq: {e}")
        return None

# El resto de las funciones (crear_archivo_post, actualizar_index, etc.) no necesitan cambios.
# Aquí las pego para que tengas el archivo completo y sin errores.

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
    if not TEMPLATES_DIR.exists():
        print(f"❌ Error Crítico: La carpeta '{TEMPLATES_DIR}' no se encuentra. Abortando.")
        sys.exit(1)

    contenido_nuevo = generar_contenido_ia()
    
    if contenido_nuevo:
        crear_archivo_post(contenido_nuevo)
        actualizar_index()
        print("\n🎉 ¡Proceso completado! Un nuevo post ha sido creado y la página de inicio está actualizada.")
