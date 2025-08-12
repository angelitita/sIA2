print("--- EJECUTANDO SCRIPT v17: VERSIÓN FINAL Y ROBUSTA ---")
import os
import datetime
import json
from pathlib import Path
import sys
from groq import Groq
import random
from bs4 import BeautifulSoup

# --- CONFIGURACIÓN ---
# ¡MUY IMPORTANTE! MODIFICA ESTA LISTA con los nombres exactos de tus imágenes.
# Asegúrate de que coincidan con los archivos que subiste a la carpeta `static/img`.
LISTA_DE_IMAGENES = [
    "imagen-1.jpg", "imagen-2.jpg", "imagen-3.jpg", "imagen-4.jpg",
    "imagen-5.jpg", "imagen-6.jpg", "imagen-8.jpg", "imagen-9.jpg",
    "imagen-10.jpg", "imagen-11.jpg"
]

try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    print("✅ Cliente de Groq configurado.")
except Exception as e:
    sys.exit(f"❌ Error al configurar el cliente de Groq: {e}")

POSTS_DIR = Path("posts")
ROOT_DIR = Path(".")

# --- PLANTILLAS HTML ---
HTML_HEADER = """<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{title}</title><link rel="stylesheet" href="{css_path}"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet"></head><body><header><div class="logo"><img src="{logo_path}" alt="sIA Logo"><h1><a href="{index_path}">sIA</a></h1></div><nav><ul><li><a href="#">Noticias</a></li><li><a href="#">Análisis</a></li><li><a href="#">IA para Todos</a></li><li><a href="#">Herramientas IA</a></li><li><a href="#">Opinión</a></li></ul></nav><a href="https://docs.google.com/forms/d/e/1FAIpQLSeNl4keU0p1eDMvzUpM5p57Naf5qBMsl5MSJNBMxPnWbofshQ/viewform?usp=header" target="_blank" class="subscribe-button">Suscríbete</a></header>"""
HTML_FOOTER = """<footer><p>&copy; 2025 sIA. Todos los derechos reservados.</p><p><a href="/privacy.html">Política de Privacidad</a></p></footer></body></html>"""
PRIV
