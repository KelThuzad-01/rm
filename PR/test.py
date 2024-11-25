import os
import requests
import subprocess
from datetime import datetime

# Configuración inicial
BITBUCKET_URL = "https://api.bitbucket.org/2.0"  # URL de Bitbucket Cloud
AUTH = ("alejandroberdun1", "ATBBkWxmrgHJrjFDWQegmVZyKZA3BA6D12E4")  # Solo el token de acceso personal como contraseña
WORKSPACE = "iberdrola-clientes"  # Nombre de tu espacio de trabajo
REPO_SLUG = "iberdrola-sfdx"  # Nombre del repositorio
PULL_REQUESTS = [8943]  # Lista de PRs a procesar

DEFAULT_AUTHOR_EMAIL = "no-reply@example.com"

def obtener_diff(pr_id):
    """Descarga el diff de una pull request específica"""
    url = f"{BITBUCKET_URL}/repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests/{pr_id}/diff"
    print(f"Descargando diff para PR {pr_id} desde: {url}")
    response = requests.get(url, auth=AUTH)
    if response.status_code == 401:
        raise Exception("Error de autenticación: verifica tu token de acceso personal.")
    elif response.status_code != 200:
        raise Exception(f"Error al obtener el diff: {response.status_code}")
    print(f"Diff descargado correctamente para PR {pr_id}")
    return response.text

def obtener_informacion_pr(pr_id):
    """Obtiene información adicional de la pull request"""
    url = f"{BITBUCKET_URL}/repositories/{WORKSPACE}/{REPO_SLUG}/pullrequests/{pr_id}"
    print(f"Obteniendo información de la PR {pr_id} desde: {url}")
    response = requests.get(url, auth=AUTH)
    if response.status_code != 200:
        raise Exception(f"Error al obtener información de la PR: {response.status_code}")
    pr_info = response.json()
    title = pr_info.get("title", f"PR {pr_id}")
    author_info = pr_info.get("author", {})
    author_name = author_info.get("display_name", "Unknown Author")
    author_email = author_info.get("email", DEFAULT_AUTHOR_EMAIL)
    return title, author_name, author_email

def formatear_patch(diff, pr_id):
    """Agrega encabezados necesarios para convertir el diff en un parche válido para git am"""
    title, author_name, author_email = obtener_informacion_pr(pr_id)
    fecha = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
    encabezado = f"""From 0000000000000000000000000000000000000000 Mon Sep 17 00:00:00 2001
From: {author_name} <{author_email}>
Date: {fecha}
Subject: [PATCH] PR #{pr_id} - {title}

"""
    return encabezado + diff

def guardar_patch(diff, pr_id):
    """Guarda el diff como un archivo de parche"""
    patch_file = f"pr_{pr_id}.patch"
    with open(patch_file, "w") as f:
        f.write(diff)
    print(f"Parche guardado como: {patch_file}")
    return patch_file

def aplicar_patch_como_commit(patch_file, pr_id):
    """Aplica el parche como un commit usando git am"""
    try:
        print(f"Aplicando el parche como commit: {patch_file}")
        subprocess.run(["git", "am", "--whitespace=fix", patch_file], check=True)
        print(f"Parche aplicado exitosamente como commit para PR #{pr_id}.")
    except subprocess.CalledProcessError as e:
        print(f"Error al aplicar el parche con git am: {e}")
        print("Intentando abortar git am...")
        subprocess.run(["git", "am", "--abort"], check=True)
        print("Parche abortado. Revisa manualmente los conflictos.")

def mostrar_diferencias_totales_y_por_archivo():
    """Muestra las diferencias totales y por archivo del commit más reciente"""
    try:
        print("\n--- Diferencias Totales en el Repositorio ---")
        result = subprocess.run(["git", "diff", "--numstat", "HEAD~1"], capture_output=True, text=True, check=True)
        
        total_additions = 0
        total_deletions = 0
        print("\n--- Diferencias por Archivo ---")
        for line in result.stdout.strip().split("\n"):
            additions, deletions, file_name = line.split("\t")
            additions = int(additions)
            deletions = int(deletions)
            total_additions += additions
            total_deletions += deletions
            print(f"{file_name}: +{additions}, -{deletions}")

        print("\n--- Totales ---")
        print(f"Líneas añadidas: {total_additions}")
        print(f"Líneas eliminadas: {total_deletions}")
    except subprocess.CalledProcessError as e:
        print(f"Error al mostrar las diferencias: {e}")

def deshacer_commit():
    """Deshace el último commit si el usuario lo solicita"""
    respuesta = input("\n¿Deseas deshacer el commit más reciente? (s/n): ").strip().lower()
    if respuesta == "s":
        try:
            subprocess.run(["git", "reset", "--hard", "HEAD~1"], check=True)
            print("Commit deshecho exitosamente.")
        except subprocess.CalledProcessError as e:
            print(f"Error al deshacer el commit: {e}")
    else:
        print("El commit se mantiene.")

def main():
    for pr_id in PULL_REQUESTS:
        print(f"\nProcesando PR {pr_id}...")
        try:
            # Descargar el diff
            diff = obtener_diff(pr_id)

            # Formatear el diff como un parche compatible con git am
            diff_formateado = formatear_patch(diff, pr_id)

            # Guardar el diff como un archivo de parche
            patch_file = guardar_patch(diff_formateado, pr_id)

            # Aplicar el parche como commit
            aplicar_patch_como_commit(patch_file, pr_id)

            # Mostrar las diferencias del commit
            mostrar_diferencias_totales_y_por_archivo()

            # Preguntar si se debe deshacer el commit
            deshacer_commit()
        except Exception as e:
            print(f"Error procesando PR {pr_id}: {e}")
            continue

if __name__ == "__main__":
    main()
