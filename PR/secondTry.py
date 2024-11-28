import os
import subprocess
import webbrowser
from git import Repo

# Configuración principal
REPO_PATH = "C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx"  # Cambia por la ruta local de tu repositorio
PULL_REQUESTS = [8140]  # Lista de IDs de las Pull Requests

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

def export_diff_to_file(repo, base_commit, target_commit, output_file, cached=False):
    """
    Exporta las diferencias de un rango de commits o cambios locales a un archivo.
    :param repo: Objeto Repo de Git.
    :param base_commit: Commit base para el diff (e.g., "commit1").
    :param target_commit: Commit de comparación (e.g., "commit2").
    :param output_file: Ruta del archivo donde guardar el diff.
    :param cached: Si es True, exporta las diferencias en el área de preparación (--cached).
    """
    try:
        if cached:
            # Differences en el área de preparación
            diff_output = repo.git.diff("--cached", "--unified=0", "--")
        else:
            # Diferencias entre dos commits
            diff_output = repo.git.diff(f"{base_commit}", f"{target_commit}", "--unified=0", "--")
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(diff_output)
        print(f"Diferencias exportadas a {output_file}.")
    except Exception as e:
        print(f"Error exportando diferencias: {e}")

def compare_diff_files(original_diff_file, local_diff_file):
    """
    Compara las diferencias en dos archivos y reporta discrepancias.
    :param original_diff_file: Ruta al archivo con diferencias originales.
    :param local_diff_file: Ruta al archivo con diferencias locales.
    """
    discrepancies_found = False

    with open(original_diff_file, "r", encoding="utf-8") as original_file:
        original_lines = original_file.readlines()

    with open(local_diff_file, "r", encoding="utf-8") as local_file:
        local_lines = local_file.readlines()

    # Comparar línea por línea
    original_set = set(original_lines)
    local_set = set(local_lines)

    extra_in_local = local_set - original_set
    missing_in_local = original_set - local_set

    if extra_in_local:
        discrepancies_found = True
        print("Líneas adicionales en los cambios locales:")
        for line in sorted(extra_in_local):
            print(f"  + {line.strip()}")

    if missing_in_local:
        discrepancies_found = True
        print("Líneas faltantes en los cambios locales:")
        for line in sorted(missing_in_local):
            print(f"  - {line.strip()}")

    if not discrepancies_found:
        print("No se encontraron discrepancias. Las diferencias coinciden exactamente.")


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

def compare_diff_files_with_context(original_diff_file, local_diff_file):
    """
    Compara dos archivos de diferencias y reporta las discrepancias, indicando el archivo donde ocurren.
    :param original_diff_file: Archivo con las diferencias originales (commit).
    :param local_diff_file: Archivo con las diferencias locales (--cached).
    """
    try:
        # Leer las diferencias de los archivos
        with open(original_diff_file, "r", encoding="utf-8") as f:
            original_diff = f.readlines()
        with open(local_diff_file, "r", encoding="utf-8") as f:
            local_diff = f.readlines()

        # Diccionario para rastrear discrepancias por archivo
        discrepancies_by_file = {}

        # Variables temporales para almacenar el contexto
        current_file = None

        # Analizar diferencias originales
        for line in original_diff:
            if line.startswith("diff --git"):
                # Extraer el nombre del archivo
                parts = line.split(" ")
                current_file = parts[2][2:]  # Quitar el prefijo "b/"
                discrepancies_by_file[current_file] = {"original": set(), "local": set()}
            elif line.startswith("+") and not line.startswith("+++"):
                discrepancies_by_file[current_file]["original"].add(line[1:].strip())
            elif line.startswith("-") and not line.startswith("---"):
                discrepancies_by_file[current_file]["original"].add(line[1:].strip())

        # Analizar diferencias locales
        for line in local_diff:
            if line.startswith("diff --git"):
                # Extraer el nombre del archivo
                parts = line.split(" ")
                current_file = parts[2][2:]  # Quitar el prefijo "b/"
                if current_file not in discrepancies_by_file:
                    discrepancies_by_file[current_file] = {"original": set(), "local": set()}
            elif line.startswith("+") and not line.startswith("+++"):
                discrepancies_by_file[current_file]["local"].add(line[1:].strip())
            elif line.startswith("-") and not line.startswith("---"):
                discrepancies_by_file[current_file]["local"].add(line[1:].strip())

        # Comparar las diferencias
        discrepancies_found = False
        for file, diffs in discrepancies_by_file.items():
            original_lines = diffs["original"]
            local_lines = diffs["local"]

            extra_lines = local_lines - original_lines
            missing_lines = original_lines - local_lines

            if extra_lines or missing_lines:
                discrepancies_found = True
                print(f"\n***************************************")
                print(f"\nDiscrepancias detectadas en el archivo: {file}")
                if extra_lines:
                    print("  Líneas adicionales en local:")
                    for line in sorted(extra_lines):
                        print(f"    + {line}")
                if missing_lines:
                    print("  Líneas faltantes en local:")
                    for line in sorted(missing_lines):
                        print(f"    - {line}")

        if not discrepancies_found:
            print("No se encontraron discrepancias entre los cambios originales y los locales.")

    except Exception as e:
        print(f"Error comparando los archivos de diferencias: {e}")


def realizar_cherry_pick_y_validar(repo, commit_id):
    """Realizar el cherry-pick y validar los cambios."""
    try:
        print(f"Realizando cherry-pick del commit {commit_id}...")
        command = f'git cherry-pick -x --no-commit -m 1 {commit_id}'
        run_command(command, cwd=REPO_PATH, ignore_errors=True)

        print("Resolviendo conflictos si los hay...")
        input("Presiona ENTER una vez que hayas resuelto los conflictos y guardado los cambios.")

        # Exportar diffs
        original_diff_file = "original_diff.txt"
        local_diff_file = "local_diff.txt"

        print("Exportando diferencias originales...")
        export_diff_to_file(repo, f"{commit_id}^1", commit_id, original_diff_file)

        print("Exportando diferencias locales...")
        export_diff_to_file(repo, None, None, local_diff_file, cached=True)

        # Comparar los archivos
        print("Comparando diferencias entre original y local...")
        compare_diff_files_with_context(original_diff_file, local_diff_file)

    except Exception as e:
        print(f"Error test {e}")

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
