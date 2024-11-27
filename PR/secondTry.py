import os
import subprocess
import webbrowser
from git import Repo

# Configuración principal
REPO_PATH = "C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx"  # Cambia por la ruta local de tu repositorio
REMOTE_NAME = "origin"  # Cambiar si el remoto no es "origin"
BRANCH_DESTINO = "release/PROD_20241202"  # Rama donde aplicar los cherry-picks
BITBUCKET_API_URL = "https://api.bitbucket.org/2.0"
WORKSPACE = "iberdrola-clientes"  # Nombre de tu espacio de trabajo
REPO_SLUG = "iberdrola-sfdx"  # Nombre del repositorio
BITBUCKET_USERNAME = "alejandroberdun1"  # Tu nombre de usuario en Bitbucket
BITBUCKET_PASSWORD = "ATBBkWxmrgHJrjFDWQegmVZyKZA3BA6D12E4"  # Tu contraseña (o token de aplicación)
PULL_REQUESTS = [8803]  # Lista de IDs de las Pull Requests


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

def normalizar_linea(linea):
    """Normalizar una línea para ignorar diferencias de espacios, saltos de línea, y orden."""
    return ''.join(linea.split()).lower()

def obtener_diffs(repo, rango=None, cached=False):
    """
    Obtener diferencias (líneas añadidas y eliminadas) entre dos estados del repositorio.
    
    :param repo: Objeto del repositorio.
    :param rango: Rango de commits para el diff (ej. 'commit1 commit2'). Si es None, usa cambios locales.
    :param cached: Si es True, usa los cambios indexados ('--cached').
    :return: Diccionario con el archivo como clave y un par de conjuntos (líneas añadidas, líneas eliminadas).
    """
    diffs = {}
    try:
        command = ['git', 'diff', '--unified=0']
        if cached:
            command.append('--cached')
        elif rango:
            command.extend(rango.split())
        command.append('--')

        diff_output = subprocess.run(
            command, cwd=REPO_PATH, capture_output=True, text=True, shell=True
        ).stdout.splitlines()

        current_file = None
        added_lines = set()
        removed_lines = set()

        for line in diff_output:
            if line.startswith('+++ ') or line.startswith('--- '):
                continue
            elif line.startswith('diff --git'):
                if current_file:
                    diffs[current_file] = (added_lines, removed_lines)
                    added_lines = set()
                    removed_lines = set()
                current_file = line.split(' ')[2].strip('b/')
            elif line.startswith('+') and not line.startswith('+++'):
                added_lines.add(normalizar_linea(line[1:]))
            elif line.startswith('-') and not line.startswith('---'):
                removed_lines.add(normalizar_linea(line[1:]))

        if current_file:
            diffs[current_file] = (added_lines, removed_lines)

    except Exception as e:
        print(f"Error obteniendo diffs: {e}")

    return diffs


def obtener_diffs_por_archivo(repo, commit_base, commit_to=None):
    """
    Obtener las diferencias añadidas y eliminadas por archivo entre dos commits.

    :param repo: Objeto del repositorio.
    :param commit_base: Commit base para el diff (puede ser '--cached' para cambios locales).
    :param commit_to: Commit de comparación. Si es None, se usa solo el commit_base.
    :return: Diccionario con el archivo como clave y un par de conjuntos (líneas añadidas, líneas eliminadas) como valor.
    """
    diffs = {}
    try:
        # Separar correctamente el rango de commits y los archivos
        diff_range = f"{commit_base}..{commit_to}" if commit_to else commit_base
        diff_output = repo.git.diff(diff_range, '--', unified=0).splitlines()

        current_file = None
        added_lines = set()
        removed_lines = set()

        for line in diff_output:
            if line.startswith('+++ ') or line.startswith('--- '):
                continue
            elif line.startswith('diff --git'):
                # Guardar los datos del archivo anterior si existe
                if current_file:
                    diffs[current_file] = (added_lines, removed_lines)
                    added_lines = set()
                    removed_lines = set()
                # Obtener el nombre del archivo del encabezado del diff
                current_file = line.split(' ')[2].strip('b/')
            elif line.startswith('+') and not line.startswith('+++'):
                added_lines.add(normalizar_linea(line[1:]))
            elif line.startswith('-') and not line.startswith('---'):
                removed_lines.add(normalizar_linea(line[1:]))

        # Agregar el último archivo procesado
        if current_file:
            diffs[current_file] = (added_lines, removed_lines)

    except Exception as e:
        print(f"Error obteniendo diffs: {e}")

    return diffs


def comparar_diferencias(original_diffs, local_diffs):
    """Comparar las diferencias originales con las diferencias locales."""
    discrepancies_found = False

    for file, (original_added, original_removed) in original_diffs.items():
        local_added, local_removed = local_diffs.get(file, (set(), set()))

        print(f"\nArchivo: {file}")
        if extra_lines := local_added - original_added:
            discrepancies_found = True
            print(f"  Líneas añadidas extra en local: {extra_lines}")
        if missing_lines := original_added - local_added:
            discrepancies_found = True
            print(f"  Líneas añadidas faltantes en local: {missing_lines}")
        if extra_removed := local_removed - original_removed:
            discrepancies_found = True
            print(f"  Líneas eliminadas extra en local: {extra_removed}")
        if missing_removed := original_removed - local_removed:
            discrepancies_found = True
            print(f"  Líneas eliminadas faltantes en local: {missing_removed}")

    if discrepancies_found:
        print("\nDiscrepancias detectadas.")
        return False
    print("\nTodas las diferencias coinciden.")
    return True

def realizar_cherry_pick_y_validar(repo, commit_id):
    """Realizar el cherry-pick y validar los cambios."""
    try:
        print(f"Realizando cherry-pick del commit {commit_id}...")
        command = f'git cherry-pick -x --no-commit -m 1 {commit_id}'
        run_command(command, cwd=REPO_PATH, ignore_errors=True)

        print("Resolviendo conflictos si los hay...")
        input("Presiona ENTER una vez que hayas resuelto los conflictos y guardado los cambios.")

        print("Obteniendo diferencias originales del commit...")
        original_diffs = obtener_diffs(repo, rango=f"{commit_id}^1 {commit_id}")

        print("Obteniendo diferencias locales...")
        local_diffs = obtener_diffs(repo, cached=True)

        if not comparar_diferencias(original_diffs, local_diffs):
            raise Exception("Discrepancias detectadas.")
    except Exception as e:
        print(f"Error durante el cherry-pick y validación: {e}")
        raise

def main():
    repo = Repo(REPO_PATH)
    for pr_id in PULL_REQUESTS:
        try:
            print(f"Procesando PR #{pr_id}...")
            command = f'git log --all --grep="#{pr_id}" --format="%H"'
            result = run_command(command, cwd=REPO_PATH)
            commit_ids = result.splitlines()

            if not commit_ids:
                print(f"No se encontró un commit para la PR #{pr_id}.")
                continue

            if len(commit_ids) > 1:
                print("Múltiples commits encontrados:")
                for i, commit_id in enumerate(commit_ids, 1):
                    print(f"  {i}. {commit_id}")
                choice = int(input("Selecciona el commit a usar: ")) - 1
                commit_id = commit_ids[choice]
            else:
                commit_id = commit_ids[0]

            realizar_cherry_pick_y_validar(repo, commit_id)
        except Exception as e:
            print(f"Error procesando la PR #{pr_id}: {e}")

if __name__ == "__main__":
    main()
