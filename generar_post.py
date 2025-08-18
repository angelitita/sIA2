# --- EJECUTANDO SCRIPT v18.0: REPARADOR INTELIGENTE ---
import os
import datetime
import json
from pathlib import Path
import sys
import random
import feedparser
from groq import Groq
from bs4 import BeautifulSoup

print("--- INICIANDO SCRIPT DE GENERACIÓN DE CONTENIDO v18.0 ---")

# --- INTERRUPTOR DE REPARACIÓN ---
RECONSTRUIR_POSTS_ANTIGUOS = True

# --- CONFIGURACIÓN ---
try:
    api_key_main = os.getenv("GROQ_API_KEY")
    if not api_key_main: sys.exit("❌ Error: La variable GROQ_API_KEY no está configurada.")
    client_groq = Groq(api_key=api_key_main)
    print("✅ Cliente de Groq configurado.")
except Exception as e:
    sys.exit(f"❌ Error al configurar el cliente de Groq: {e}")
POSTS_DIR = Path("posts")
ROOT_DIR = Path(".")

# --- PLANTILLAS HTML ---
HTML_HEADER = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{title}</title><link rel="stylesheet" href="/static/css/style.css"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet"><link rel="icon" href="/static/img/logo.png" type="image/png"></head><body><header><div class="logo"><img src="/static/img/logo.png" alt="sIA Logo"><h1><a href="/index.html">sIA</a></h1></div><nav><a href="https://docs.google.com/forms/d/e/1FAIpQLSeNl4keU0p1eDMvzUpM5p57Naf5qBMsl5MSJNBMxPnWbofshQ/viewform?usp=header" target="_blank" class="subscribe-button">Suscríbete</a></nav></header>"""
HTML_FOOTER = """<footer><p>&copy; 2025 sIA. Todos los derechos reservados.</p></footer></body></html>"""

# --- FUNCIONES ---
def generar_noticia_desde_api():
    print("🤖 Generando un nuevo post de noticias...")
    system_prompt = "Eres un periodista para 'sIA'. Escribe un artículo de noticias en español sobre un avance reciente en IA en Latinoamérica. Tu respuesta DEBE ser únicamente un objeto JSON válido."
    user_prompt = f"""Escribe un artículo de noticias. Formato JSON: {{"title": "Un titular atractivo", "summary": "Un resumen corto", "content_html": "El cuerpo del artículo en HTML..."}}"""
    try:
        chat_completion = client_groq.chat.completions.create(messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], model="llama3-8b-8192", response_format={"type": "json_object"})
        contenido = json.loads(chat_completion.choices[0].message.content)
        if not all(k in contenido for k in ["title", "content_html"]): raise ValueError("JSON incompleto.")
        print(f"✅ Contenido generado: '{contenido['title']}'")
        return contenido
    except Exception as e:
        print(f"❌ Error al generar contenido: {e}", file=sys.stderr)
        return None

def crear_archivo_post(contenido):
    POSTS_DIR.mkdir(exist_ok=True)
    fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
    slug_base = contenido["title"].lower().replace(" ", "-").replace(":", "").replace("?", "").replace("¿", "")
    slug = f"{slug_base[:50]}-{datetime.datetime.now().strftime('%H%M%S')}"
    nombre_archivo = f"{datetime.date.today().strftime('%Y-%m-%d')}-{slug}.html"
    article_html = f"""<main class="article-body"><article><h1 class="article-title">{contenido['title']}</h1><p class="article-meta">Publicado por Redacción sIA el {fecha_actual}</p><div class="article-content">{contenido['content_html']}</div></article></main>"""
    full_html = HTML_HEADER.format(title=contenido['title']) + article_html + HTML_FOOTER
    with open(POSTS_DIR / nombre_archivo, "w", encoding="utf-8") as f: f.write(full_html)
    print(f"📄 Archivo de post creado: {nombre_archivo}")

def actualizar_index():
    print("🔄 Actualizando la página de inicio...")
    try:
        posts = sorted(list(POSTS_DIR.glob("*.html")), key=lambda p: p.name, reverse=True)
        grid_html = ""
        for post_path in posts:
            with open(post_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
                title_tag = soup.find("h1", class_="article-title")
                title = title_tag.string.strip() if title_tag and title_tag.string else "Artículo sin Título"
            
            imagen_aleatoria = random.choice(os.listdir(IMG_DIR)) if os.listdir(IMG_DIR) else ""
            grid_html += f"""<article class="article-card"><a href="/{post_path.as_posix()}"><img src="/static/img/{imagen_aleatoria}" alt="Artículo"></a><div class="card-content"><h3><a href="/{post_path.as_posix()}">{title}</a></h3></div></article>"""
        
        main_content = f"""<div class="main-container"><h1 class="page-title">Últimas Noticias</h1><div class="article-grid">{grid_html}</div></div>"""
        full_html = HTML_HEADER.format(title="sIA - Inteligencia Artificial en Latinoamérica") + main_content + HTML_FOOTER
        with open(ROOT_DIR / "index.html", "w", encoding="utf-8") as f: f.write(full_html)
        print("✅ index.html actualizado.")
    except Exception as e:
        print(f"❌ Error al actualizar index.html: {e}", file=sys.stderr)

def reparar_posts_antiguos():
    print("🛠️ INICIANDO MODO DE RESCATE Y REPARACIÓN DE POSTS...")
    posts_a_reparar = list(POSTS_DIR.glob("*.html"))
    if not posts_a_reparar:
        print("No se encontraron posts para reparar.")
        return

    for post_path in posts_a_reparar:
        try:
            print(f"Rescatando texto de: {post_path.name}")
            with open(post_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")
            
            # Extrae todo el texto legible del post, sin importar si el HTML está roto
            texto_rescatado = soup.get_text(separator=' ', strip=True)
            # Limita el texto para no exceder el límite del prompt
            texto_para_ia = texto_rescatado[:2000]

            print("🤖 Pidiendo a la IA que genere un nuevo título y resumen...")
            system_prompt = "Eres un editor para el blog 'sIA'. Te daré el texto de un artículo dañado. Tu trabajo es leerlo y crear un título y un cuerpo de artículo limpio en formato JSON. La respuesta DEBE estar en español."
            user_prompt = f"""He rescatado este texto de un archivo dañado: "{texto_para_ia}". Basándote en este texto, crea un título atractivo y reescribe el contenido principal en un formato HTML limpio. Formato JSON: {{"title": "Un título nuevo y relevante", "content_html": "El cuerpo del artículo en HTML limpio..."}}"""
            
            chat_completion = client_groq.chat.completions.create(messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], model="llama3-8b-8192", response_format={"type": "json_object"})
            contenido_reparado = json.loads(chat_completion.choices[0].message.content)
            
            if not all(k in contenido_reparado for k in ["title", "content_html"]):
                print(f"⚠️  La IA no pudo reparar {post_path.name}. Saltando.")
                continue

            # Reconstruye el post desde cero con la estructura correcta
            crear_archivo_post(contenido_reparado)
            # Borra el archivo viejo y dañado
            os.remove(post_path)
            print(f"✅ Post reconstruido y guardado: '{contenido_reparado['title']}'")

        except Exception as e:
            print(f"⚠️  Error irreparable en {post_path.name}: {e}")

    print("✅ REPARACIÓN COMPLETADA.")

if __name__ == "__main__":
    if RECONSTRUIR_POSTS_ANTIGUOS:
        reparar_posts_antiguos()
    else:
        contenido_nuevo = generar_noticia_desde_api()
        if contenido_nuevo:
            crear_archivo_post(contenido_nuevo)
    
    # Siempre actualizamos el index al final
    actualizar_index()
    print("\n🎉 ¡Proceso completado exitosamente!")
