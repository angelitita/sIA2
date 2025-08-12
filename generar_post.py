print("--- EJECUTANDO SCRIPT v9 'A PRUEBA DE BALAS' ---")
from pathlib import Path
import sys

# Definir las carpetas
POSTS_DIR = Path("posts")
ROOT_DIR = Path(".")

# Crear el contenido del post de prueba (HTML simple)
post_html_content = """
<!DOCTYPE html>
<html lang="es">
<head><title>Post de Prueba</title><meta charset="UTF-8"></head>
<body>
    <h1>Este es un post de prueba</h1>
    <p>Si puedes ver esto, el sistema de creación de archivos, commit y despliegue funciona.</p>
    <a href="../index.html">Volver al inicio</a>
</body>
</html>
"""

# Crear el contenido del index de prueba (HTML simple)
index_html_content = """
<!DOCTYPE html>
<html lang="es">
<head><title>sIA - Página de Prueba</title><meta charset="UTF-8"></head>
<body>
    <h1>Bienvenido a sIA</h1>
    <p>Sitio en construcción. El sistema de despliegue automático funciona.</p>
    <a href="posts/post-de-prueba.html">Ver el post de prueba</a>
</body>
</html>
"""

try:
    print("⚙️ Creando archivos de prueba simples...")
    # Asegurarse de que la carpeta posts exista
    POSTS_DIR.mkdir(exist_ok=True)

    # Escribir el archivo del post
    with open(POSTS_DIR / "post-de-prueba.html", "w", encoding="utf-8") as f:
        f.write(post_html_content)
    print("✅ Archivo de post de prueba creado.")

    # Escribir el archivo index
    with open(ROOT_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html_content)
    print("✅ Archivo index de prueba creado.")
    
    print("\n🎉 ¡Proceso de prueba 'a prueba de balas' completado!")

except Exception as e:
    print(f"❌ Error durante la creación de archivos de prueba: {e}")
    sys.exit(1)
