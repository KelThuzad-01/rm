import os
import subprocess
import webbrowser
import re
from git import Repo
import time


# Configuración principal
REPO_PATH = "C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx"  # Cambia por la ruta local de tu repositorio
PULL_REQUESTS = [6854, 7209, 8968, 8958, 8991]  # Lista de IDs de las Pull Requests

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

def export_diff_to_file(repo, commit_base, commit_to, output_file, cached=False):
    """
    Exportar el resultado de git diff a un archivo.
    """
    try:
        if cached:
            command = f"git diff --cached --unified=0 > {output_file}"
        elif commit_base and commit_to:
            # Asegurar que los commits estén correctamente formateados
            command = f"git diff --unified=0 \"{commit_base}\" \"{commit_to}\" > \"{output_file}\""
        else:
            raise ValueError("Se requiere commit_base y commit_to para el diff no cached.")

        # Registrar el comando antes de ejecutarlo
        print(f"Ejecutando comando: {command}")
        
        # Ejecutar el comando
        result = subprocess.run(
            command, cwd=REPO_PATH, shell=True, capture_output=True, text=True
        )

        # Verificar errores en la ejecución
        if result.returncode != 0:
            print(f"Error ejecutando el comando: {result.stderr.strip()}")
            raise Exception(f"Error exportando diferencias: {result.stderr.strip()}")

        # Confirmar que el archivo fue generado
        if not os.path.exists(output_file) or os.stat(output_file).st_size == 0:
            raise Exception(f"El archivo {output_file} no se generó o está vacío.")

        print(f"Diferencias exportadas a {output_file}.")
    except Exception as e:
        print(f"Error exportando diferencias: {e}")
        raise



def verificar_archivo_no_vacio(archivo):
    """Verifica si el archivo tiene contenido."""
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            contenido = f.read().strip()
            if not contenido:
                raise ValueError(f"El archivo {archivo} está vacío.")
        print(f"El archivo {archivo} tiene contenido.")
    except Exception as e:
        print(f"Error verificando el archivo {archivo}: {e}")
        raise



def abrir_pull_request_en_navegador(pr_id):
    """
    Abrir la Pull Request en el navegador.
    
    :param pr_id: ID de la Pull Request.
    """
    url = f"https://bitbucket.org/iberdrola-clientes/iberdrola-sfdx/pull-requests/{pr_id}/diff"
    print(f"Abriendo la Pull Request #{pr_id} en el navegador: {url}")
    webbrowser.open(url)

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
        contar_lineas_modificadas()

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
        diff_range = f"{commit_base} {commit_to}" if commit_to else commit_base
        diff_output = repo.git.diff(diff_range, '--', unified=0).splitlines()

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
                added_lines.add(line[1:])  # Respetar espacios y tabulaciones
            elif line.startswith('-') and not line.startswith('---'):
                removed_lines.add(line[1:])  # Respetar espacios y tabulaciones

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

def compare_diff_files_with_context(file1, file2):
    """
    Comparar dos archivos línea por línea e imprimir diferencias, omitiendo los números de línea.
    """
    try:
        with open(file1, "r", encoding="utf-8") as f1, open(file2, "r", encoding="utf-8") as f2:
            lines1 = [line for line in f1 if not line.startswith("@@")]
            lines2 = [line for line in f2 if not line.startswith("@@")]

            # Mostrar diferencias línea por línea
            import difflib
            diff = difflib.unified_diff(
                lines1, lines2,
                fromfile=file1,
                tofile=file2,
                lineterm=""
            )
            differences = list(diff)

            if differences:
                contar_lineas_modificadas()
                print("\n¡Se detectaron discrepancias! Detalles:")
                current_file = None
                for line in differences:
                    # Detecta cambios de archivo
                    if line.startswith("--- ") or line.startswith("+++ "):
                        # Imprime la línea separadora antes de cada archivo
                        if current_file != line:
                            print("\n" + "*" * 40)
                            current_file = line
                    print(line.strip())
                return False
            else:
                print("\n¡No se detectaron discrepancias! Los cambios coinciden exactamente.")
                return True
    except Exception as e:
        print(f"Error comparando archivos: {e}")
        return False




def verificar_conflictos(repo):
    """Verificar si aún hay conflictos en el repositorio."""
    try:
        status_output = repo.git.status()
        if "Unmerged paths:" in status_output:
            return True
        return False
    except Exception as e:
        print(f"Error verificando conflictos: {e}")
        return True

def normalizar_contenido(lines):
    """
    Normalizar contenido para evitar diferencias debido a caracteres invisibles.
    """
    return [line.replace("\r\n", "\n").replace("\r", "\n").strip() for line in lines]

def realizar_cherry_pick_y_validar(repo, commit_id):
    """Realizar el cherry-pick y validar los cambios."""
    try:
        print(f"Realizando cherry-pick del commit {commit_id}...")
        command = f'git cherry-pick -x --no-commit -m 1 {commit_id}'
        run_command(command, cwd=REPO_PATH, ignore_errors=True)

        # Usar rutas completas para los archivos de diferencias
        original_diff_file = os.path.join(REPO_PATH, "original_diff.txt")
        local_diff_file = os.path.join(REPO_PATH, "local_diff.txt")

        while True:
            input("Presiona ENTER si no hay conflictos. En caso contrario, solucionalos y añadelos en Staged Changes")
            
            # Exportar diffs
            print("Exportando diferencias originales...")
            export_diff_to_file(repo, f"{commit_id}^1", commit_id, original_diff_file)

            print("Exportando diferencias locales...")
            export_diff_to_file(repo, None, None, local_diff_file, cached=True)

            # Comparar los archivos
            contar_lineas_modificadas()
            print("Comparando diferencias entre original y local...")
            if compare_diff_files_with_context(original_diff_file, local_diff_file):
                print("\nNo se encontraron discrepancias. Realizando commit...")
                command = f'git commit --no-verify'
                run_command(command, cwd=REPO_PATH, ignore_errors=True)
                break

            respuesta = input("¿Deseas intentar resolver las discrepancias nuevamente? (s/n): ").lower()
            if respuesta != "s":
                print("Proceso detenido por el usuario.")
                raise Exception("Discrepancias no resueltas.")
    except Exception as e:
        print(f"Error durante el cherry-pick y validación: {e}")
        contar_lineas_modificadas()
def contar_lineas_modificadas():
    try:
        # Ejecuta el comando git diff con estadísticas
        result = subprocess.run(
            ["git", "diff", "--numstat", "--cached"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.stderr:
            print(f"Error al ejecutar git diff: {result.stderr}")
            return
        
        archivos = []
        total_agregadas = 0
        total_eliminadas = 0

        # Procesa la salida del comando git diff
        for linea in result.stdout.splitlines():
            match = re.match(r"(\d+|-)\s+(\d+|-)\s+(.*)", linea)
            if match:
                agregadas = int(match.group(1)) if match.group(1) != '-' else 0
                eliminadas = int(match.group(2)) if match.group(2) != '-' else 0
                archivo = match.group(3)

                archivos.append({
                    "archivo": archivo,
                    "lineas_agregadas": agregadas,
                    "lineas_eliminadas": eliminadas
                })

                total_agregadas += agregadas
                total_eliminadas += eliminadas

        # Muestra el resumen por archivo
        print(f"{'Archivo':<50} {'Líneas Añadidas':<15} {'Líneas Eliminadas':<15}")
        print("="*80)
        for archivo in archivos:
            print(f"{archivo['archivo']:<50} {archivo['lineas_agregadas']:<15} {archivo['lineas_eliminadas']:<15}")
        
        # Muestra el total
        print("="*80)
        print(f"{'TOTAL':<50} {total_agregadas:<15} {total_eliminadas:<15}")
        print(f"Líneas modificadas en total (añadidas + eliminadas): {total_agregadas + total_eliminadas}")

    except Exception as e:
        print(f"Error al contar líneas modificadas: {e}")

def main():
    repo = Repo(REPO_PATH)
    for pr_id in PULL_REQUESTS:
        try:
            print(f"Procesando PR #{pr_id}...")
            abrir_pull_request_en_navegador(pr_id)
            command = f'git log --all --grep="#{pr_id}" --format="%H"'
            result = run_command(command, cwd=REPO_PATH)
            commit_ids = result.splitlines()

            if not commit_ids:
                print(f"No se encontró un commit para la PR #{pr_id}.")
                print(f"Ejecutando git fetch, por favor vuelve a lanzar esta PR")
                command = f'git fetch --all'
                run_command(command, cwd=REPO_PATH, ignore_errors=True)
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

        input("Presiona ENTER para proceder con la siguiente PR tras hacer commit")

if __name__ == "__main__":
    main()