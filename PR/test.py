import os
import requests
import subprocess
from datetime import datetime
from unidiff import PatchSet
import chardet  # Para detectar la codificación automáticamente
import webbrowser

# Configuración inicial
BITBUCKET_URL = "https://api.bitbucket.org/2.0"  # URL de Bitbucket Cloud
AUTH = ("alejandroberdun1", "ATBBkWxmrgHJrjFDWQegmVZyKZA3BA6D12E4")  # Solo el token de acceso personal como contraseña
WORKSPACE = "iberdrola-clientes"  # Nombre de tu espacio de trabajo
REPO_SLUG = "iberdrola-sfdx"  # Nombre del repositorio
PULL_REQUESTS = [8964, 8944, 8951, 8961, 8959, 8956]  # Lista de PRs a procesar

def aplicar_cherry_pick(commit_hash):
    """Aplica el commit usando git cherry-pick, manejando merges"""
    try:
        print(f"Verificando si el commit {commit_hash} es un merge...")
        result = subprocess.run(
            ["git", "rev-list", "--parents", "-n", "1", commit_hash],
            capture_output=True,
            text=True,
            check=True
        )
        parents = result.stdout.strip().split()
        is_merge = len(parents) > 2  # Si tiene más de 2 hashes, es un merge

        if is_merge:
            print(f"El commit {commit_hash} es un merge. Aplicando cherry-pick con -m 1...")
            subprocess.run(["git", "cherry-pick", "-m", "1", commit_hash], check=True)
        else:
            print(f"El commit {commit_hash} no es un merge. Aplicando cherry-pick normalmente...")
            subprocess.run(["git", "cherry-pick", commit_hash], check=True)

        print(f"Cherry-pick aplicado exitosamente para el commit {commit_hash}.")
    except subprocess.CalledProcessError as e:
        print(f"Error al aplicar cherry-pick: {e}")
        print("Resuelve manualmente los conflictos y continúa con:")
        print("  git cherry-pick --continue")

def obtener_commit_pr(pr_id):
    """Obtiene el commit de merge más reciente que incluye la pull request, o lo solicita al usuario"""
    try:
        # Buscar commits de merge relacionados con la PR
        pr_tag = f"#{pr_id}"
        print(f"Buscando commit de merge más reciente relacionado con PR {pr_id}...")
        result = subprocess.run(
            ["git", "log", "--all", "--merges", f"--grep={pr_tag}", "--format=%H"],
            capture_output=True,
            text=True,
            check=True
        )
        commit_hashes = result.stdout.strip().splitlines()

        # Verificar si se encontraron commits de merge
        if commit_hashes:
            commit_hash = commit_hashes[0]  # Seleccionar el más reciente
            print(f"Commit de merge encontrado automáticamente para PR {pr_id}: {commit_hash}")
            return commit_hash

        # Si no se encuentra ningún commit, solicitar al usuario
        print(f"No se encontró automáticamente ningún commit de merge relacionado con PR #{pr_id}.")
        while True:
            commit_hash = input("Por favor, introduce el hash del commit de merge: ").strip()
            if len(commit_hash) == 40 and all(c in "0123456789abcdefABCDEF" for c in commit_hash):
                return commit_hash
            print("El hash introducido no es válido. Por favor, verifica e inténtalo de nuevo.")

    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar git log: {e}")
        raise
    except Exception as e:
        print(f"Error en obtener_commit_pr: {e}")
        raise


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

def aplicar_parche_automatico(patch_file, pr_id):
    """Aplica el parche usando varios métodos en caso de fallos"""
    try:
        print(f"Intentando aplicar el parche con git am: {patch_file}")
        subprocess.run(["git", "am", "--whitespace=fix", patch_file], check=True)
        print(f"Parche aplicado exitosamente con git am para PR #{pr_id}.")
    except subprocess.CalledProcessError:
        print("git am falló. Intentando con git apply...")
        try:
            subprocess.run(["git", "apply", "--whitespace=fix", patch_file], check=True)
            print("Parche aplicado parcialmente con git apply. Revisa los archivos .rej.")
        except subprocess.CalledProcessError:
            print("git apply falló. Intentando con git apply --3way...")
            try:
                subprocess.run(["git", "apply", "--3way", "--whitespace=fix", patch_file], check=True)
                print("Parche aplicado exitosamente con git apply --3way.")
            except subprocess.CalledProcessError:
                    print("git apply --3way falló. Intentando con cherry-pick...")
            try:
                commit_hash = obtener_commit_pr(pr_id)
                aplicar_cherry_pick(commit_hash)
            except Exception as e:
                print(f"Error al aplicar cherry-pick: {e}")
                print("Los cambios no se pudieron aplicar automáticamente.")


def aplicar_con_patch(patch_file):
    """Aplica el parche usando la herramienta patch"""
    try:
        print(f"Intentando aplicar el parche con patch: {patch_file}")
        subprocess.run(["patch", "-p1", "-i", patch_file], check=True)
        print("Parche aplicado exitosamente con patch.")
    except subprocess.CalledProcessError as e:
        print(f"Error al aplicar el parche con patch: {e}")
        print("Revisa los archivos .rej para resolver conflictos manualmente.")

def preguntar_continuar():
    """Pregunta si desea continuar con la siguiente PR"""
    while True:
        respuesta = input("¿Deseas continuar con la siguiente PR? (s/n): ").strip().lower()
        if respuesta in ["s", "n"]:
            return respuesta == "s"
        print("Por favor, responde con 's' (sí) o 'n' (no).")

def detectar_codificacion(file_path):
    """Detecta la codificación de un archivo usando chardet"""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    result = chardet.detect(raw_data)
    return result['encoding']

def aplicar_con_unidiff(patch_file):
    """Aplica los cambios del parche usando la librería unidiff con manejo de codificación"""
    try:
        # Detectar codificación del parche
        encoding_patch = detectar_codificacion(patch_file)
        print(f"Codificación detectada para el parche: {encoding_patch}")

        # Leer el parche con la codificación detectada
        with open(patch_file, "r", encoding=encoding_patch, errors='replace') as f:
            patch = PatchSet(f)

        for patched_file in patch:
            file_path = patched_file.path
            print(f"Procesando archivo: {file_path}")

            # Detectar codificación del archivo afectado
            encoding_file = detectar_codificacion(file_path)
            print(f"Codificación detectada para el archivo {file_path}: {encoding_file}")

            # Leer el archivo original
            with open(file_path, "r", encoding=encoding_file, errors='replace') as original_file:
                original_lines = original_file.readlines()

            # Aplicar los cambios del parche
            new_lines = []
            for hunk in patched_file:
                for line in hunk:
                    if line.is_added:
                        new_lines.append(line.value)
                    elif not line.is_removed:
                        new_lines.append(line.value)

            # Guardar los cambios en el archivo
            with open(file_path, "w", encoding=encoding_file, errors='replace') as updated_file:
                updated_file.writelines(new_lines)

            print(f"Cambios aplicados al archivo: {file_path}")
        print("Parche aplicado exitosamente con unidiff.")
    except Exception as e:
        print(f"Error al aplicar el parche con unidiff: {e}")


def main():
    for pr_id in PULL_REQUESTS:
        # URL que deseas abrir
        url = f'https://bitbucket.org/{WORKSPACE}/{REPO_SLUG}/pull-requests/{pr_id}/diff'
        # Abre la URL en el navegador predeterminado del sistema
        webbrowser.open(url)
        print(f"\nProcesando PR {pr_id}...")
        try:
            # Descargar el diff
            diff = obtener_diff(pr_id)

            # Formatear el diff como un parche compatible con git am
            diff_formateado = formatear_patch(diff, pr_id)

            # Guardar el diff como un archivo de parche
            patch_file = guardar_patch(diff_formateado, pr_id)

            # Aplicar el parche como commit
            aplicar_parche_automatico(patch_file, pr_id)

            if not preguntar_continuar():
                print("Deteniendo el proceso por solicitud del usuario.")
                break
        except Exception as e:
            print(f"Error procesando PR {pr_id}: {e}")
            continue

if __name__ == "__main__":
    main()
