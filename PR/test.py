import os
import requests
import subprocess
from datetime import datetime

# Configuración inicial
BITBUCKET_URL = "https://api.bitbucket.org/2.0"  # URL de Bitbucket Cloud
AUTH = ("alejandroberdun1", "ATBBkWxmrgHJrjFDWQegmVZyKZA3BA6D12E4")  # Solo el token de acceso personal como contraseña
WORKSPACE = "iberdrola-clientes"  # Nombre de tu espacio de trabajo
REPO_SLUG = "iberdrola-sfdx"  # Nombre del repositorio
PULL_REQUESTS = []  # Lista de PRs a procesar

def obtener_informacion_git():
    """Obtiene el nombre y correo configurados en Git localmente"""
    try:
        user_name = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True, check=True).stdout.strip()
        user_email = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True, check=True).stdout.strip()
        if not user_name or not user_email:
            raise Exception("El usuario o correo de Git no están configurados.")
        return user_name, user_email
    except Exception as e:
        print(f"Error al obtener información de Git: {e}")
        raise

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

def formatear_patch(diff, pr_id):
    """Agrega encabezados necesarios para convertir el diff en un parche válido para git am"""
    try:
        user_name, user_email = obtener_informacion_git()
    except Exception as e:
        print("Usando valores predeterminados debido a un error al obtener la información de Git.")
        user_name, user_email = "Default User", "no-reply@example.com"

    title = f"PR #{pr_id} - Cambios aplicados"
    fecha = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")
    encabezado = f"""From 0000000000000000000000000000000000000000 Mon Sep 17 00:00:00 2001
From: {user_name} <{user_email}>
Date: {fecha}
Subject: [PATCH] {title}

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
        except Exception as e:
            print(f"Error procesando PR {pr_id}: {e}")
            continue

if __name__ == "__main__":
    main()
