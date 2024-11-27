import os
import subprocess
import webbrowser
import requests
from git import Repo

# Configuración principal
REPO_PATH = "C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx"  # Cambia por la ruta local de tu repositorio
PULL_REQUESTS = [8969, 8971]  # Lista de IDs de las Pull Requests
REMOTE_NAME = "origin"  # Cambiar si el remoto no es "origin"
BRANCH_DESTINO = "release/UAT2_20241202"  # Rama donde aplicar los cherry-picks
BITBUCKET_API_URL = "https://api.bitbucket.org/2.0"
WORKSPACE = "iberdrola-clientes"  # Nombre de tu espacio de trabajo
REPO_SLUG = "iberdrola-sfdx"  # Nombre del repositorio
BITBUCKET_USERNAME = "alejandroberdun1"  # Tu nombre de usuario en Bitbucket
BITBUCKET_PASSWORD = "ATBBkWxmrgHJrjFDWQegmVZyKZA3BA6D12E4"  # Tu contraseña (o token de aplicación)

def run_command(command, cwd=None, ignore_errors=False):
    """Ejecutar un comando en la terminal."""
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        if ignore_errors:
            print(f"Advertencia: el comando falló, pero se ignora el error:\n{result.stderr}")
        else:
            print(f"Error ejecutando {command}:\n{result.stderr}")
            raise Exception(result.stderr)
    return result.stdout.strip()

def buscar_commit_de_merge(pr_id):
    """Buscar el commit de merge más reciente usando git log y el número de PR."""
    print(f"Buscando el commit de merge más reciente para la PR #{pr_id}...")
    command = f'git log --all --grep="#{pr_id}" --format="%H"'
    result = run_command(command, cwd=REPO_PATH)
    commit_ids = result.splitlines()
    if not commit_ids:
        raise Exception(f"No se encontró un commit asociado a la PR #{pr_id}.")
    commit_id = commit_ids[0]
    print(f"Commit de merge más reciente encontrado: {commit_id}")
    return commit_id

def abrir_pull_request_en_navegador(pr_id):
    """Abrir la Pull Request en el navegador."""
    url = f"https://bitbucket.org/{WORKSPACE}/{REPO_SLUG}/pull-requests/{pr_id}"
    print(f"Abriendo la Pull Request #{pr_id} en el navegador: {url}")
    webbrowser.open(url)

def listar_archivos_afectados(repo, commit_id):
    """Listar los archivos afectados por un commit."""
    print(f"Archivos afectados por el commit {commit_id}:")
    archivos = repo.git.diff(f"{commit_id}^!", name_only=True).split("\n")
    for archivo in archivos:
        print(f" - {archivo}")
    return archivos

def registrar_progreso(pr_id, commit_id, estado):
    """Registrar el progreso de cada Pull Request."""
    with open("progreso_cherry_pick.log", "a") as log_file:
        log_file.write(f"PR #{pr_id}, Commit: {commit_id}, Estado: {estado}\n")
    print(f"Progreso registrado: PR #{pr_id}, Estado: {estado}")

def comparar_cambios(repo, commit_id):
    """Comparar los cambios del cherry-pick con el diff original, archivo por archivo."""
    print(f"Comparando cambios del commit {commit_id} con los aplicados...")

    # Obtener la lista de archivos modificados en el commit original
    original_files = repo.git.diff(f"{commit_id}^!", name_only=True).splitlines()

    # Verificar cada archivo individualmente
    discrepancies_found = False
    for file in original_files:
        print(f"Comparando cambios en el archivo: {file}")
        
        # Extraer los diffs del archivo en el commit original
        original_diff = repo.git.diff(f"{commit_id}^!", file, unified=0)
        # Extraer los diffs del archivo local tras el cherry-pick
        local_diff = repo.git.diff(file, unified=0)

        if original_diff != local_diff:
            discrepancies_found = True
            print(f"Discrepancias detectadas en el archivo {file}:")
            
            original_lines = set(original_diff.splitlines())
            local_lines = set(local_diff.splitlines())

            # Identificar líneas que están en local pero no en el original
            extra_lines = local_lines - original_lines
            if extra_lines:
                print("Líneas adicionales detectadas:")
                for line in extra_lines:
                    print(f"  + {line}")

            # Identificar líneas que están en el original pero no en local
            missing_lines = original_lines - local_lines
            if missing_lines:
                print("Líneas faltantes detectadas:")
                for line in missing_lines:
                    print(f"  - {line}")
    
    if discrepancies_found:
        print("Discrepancias detectadas. Por favor, corrige las diferencias.")
        return False
    print("Los cambios coinciden exactamente con el commit original.")
    return True


def confirmar_proceder(pr_id):
    """Preguntar al usuario si desea proceder con la PR actual."""
    respuesta = input(f"¿Deseas proceder con la Pull Request #{pr_id}? (s/n): ").lower()
    return respuesta == "s"

def confirmar_continuar():
    """Preguntar al usuario si desea continuar después de resolver conflictos o discrepancias."""
    respuesta = input("¿Has resuelto los conflictos/discrepancias y deseas continuar? (s/n): ").lower()
    return respuesta == "s"

def realizar_cherry_pick(commit_id, repo):
    """Realizar cherry-pick del commit de merge usando -m 1."""
    print(f"Realizando cherry-pick del commit {commit_id}...")
    try:
        command = f'git cherry-pick -x --no-commit -m 1 {commit_id}'
        run_command(command, cwd=REPO_PATH, ignore_errors=True)
        print(f"Cherry-pick del commit {commit_id} realizado con éxito.")
        command = "code -r ."
        run_command(command, cwd=REPO_PATH)
    except Exception as e:
        print(f"Error durante el cherry-pick: {e}")
        print("Por favor, resuelve los conflictos manualmente.")
        input("Presiona ENTER cuando hayas resuelto los conflictos y continúes manualmente.")

    # Validación precisa: comparar archivo por archivo hasta que no haya discrepancias
    while not comparar_cambios(repo, commit_id):
        print("Corrige las discrepancias manualmente y guarda los cambios.")
        input("Presiona ENTER cuando hayas corregido las discrepancias y guardado los cambios.")
        if not confirmar_continuar():
            print("Proceso detenido por el usuario. Resuelve los problemas antes de continuar.")
            raise Exception("El usuario no confirmó la continuación.")


def realizar_commit(repo, commit_id):
    """Realizar el commit reutilizando el mensaje del commit original."""
    respuesta = input("¿Deseas hacer commit de los cambios con el mensaje original? (s/n): ").lower()
    if respuesta == "s":
        repo.git.commit(reuse_message=commit_id)
        print("Commit realizado con el mensaje original del cherry-pick.")
    else:
        print("El commit no se realizó.")

def realizar_push(repo):
    """Preguntar al usuario si desea hacer push de los cambios."""
    respuesta = input("¿Deseas hacer push al repositorio remoto? (s/n): ").lower()
    if respuesta == "s":
        repo.git.push(REMOTE_NAME, BRANCH_DESTINO)

def main():
    repo = Repo(REPO_PATH)
    print("Iniciando proceso de cherry-pick para las Pull Requests...")
    for pr_id in PULL_REQUESTS:
        command = f'git fetch --all'
        result = run_command(command, cwd=REPO_PATH)
        command = f'git pull'
        result = run_command(command, cwd=REPO_PATH)
        abrir_pull_request_en_navegador(pr_id)
        if not confirmar_proceder(pr_id):
            print(f"Saltando la Pull Request #{pr_id}.")
            continue
        try:
            commit_id = buscar_commit_de_merge(pr_id)
            listar_archivos_afectados(repo, commit_id)
            realizar_cherry_pick(commit_id, repo)
            realizar_commit(repo, commit_id)
        except Exception as e:
            print(f"Error procesando la PR #{pr_id}: {e}")
            registrar_progreso(pr_id, commit_id, "Conflictos detectados")
            continue
        if not confirmar_continuar():
            print("Finalizando el proceso por solicitud del usuario.")
            break
    realizar_push(repo)
    print("Proceso finalizado.")

if __name__ == "__main__":
    main()
