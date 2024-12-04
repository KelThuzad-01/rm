import os
import subprocess
import webbrowser
import re
from git import Repo
import time
from colorama import Fore, Style, init
init(autoreset=True)

# Configuración principal
REPO_PATH = "C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx"  # Cambia por la ruta local de tu repositorio
PULL_REQUESTS = []  # Lista de IDs de las Pull Requests

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
    Exportar el resultado de git diff a un archivo, asegurando compatibilidad con caracteres especiales.
    """
    try:
        # Si repo es un objeto Repo, obtener su directorio de trabajo
        if isinstance(repo, str):
            repo_path = repo
        elif hasattr(repo, "working_dir"):
            repo_path = repo.working_dir
        else:
            raise ValueError(f"repo debe ser una cadena o un objeto Repo. Recibido: {type(repo)}")

        # Validar que la ruta del repositorio sea válida
        if not os.path.isdir(repo_path):
            raise ValueError(f"La ruta '{repo_path}' no apunta a un directorio existente.")

        # Archivos a excluir
        exclude_files = [
            "config/tests-to-run.list",
            "config/core-tests-to-run.list"
        ]

        # Construir el comando base de git diff
        if cached:
            command = f"git diff --cached --unified=0"
        elif commit_base and commit_to:
            command = f"git diff --unified=0 \"{commit_base}\" \"{commit_to}\""
        else:
            raise ValueError("Se requiere commit_base y commit_to para el diff no cached.")

        # Registrar el comando antes de ejecutarlo
        print(f"Ejecutando comando: {command}")

        # Ejecutar el comando con codificación compatible
        result = subprocess.run(
            command,
            cwd=repo_path,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8"  # Asegurarse de usar UTF-8
        )

        # Verificar errores en la ejecución
        if result.returncode != 0:
            print(f"Error ejecutando el comando: {result.stderr.strip()}")
            raise Exception(f"Error exportando diferencias: {result.stderr.strip()}")

        # Filtrar las diferencias para excluir bloques completos de archivos especificados
        lines = result.stdout.splitlines()
        filtered_lines = []
        exclude_pattern = re.compile(r"^diff --git a/(.*) b/(.*)$")
        exclude_active = False

        for line in lines:
            match = exclude_pattern.match(line)
            if match:
                # Detectar el archivo actual
                current_file = match.group(1)
                if any(exclude in current_file for exclude in exclude_files):
                    exclude_active = True
                    continue
                else:
                    exclude_active = False

            if not exclude_active:
                filtered_lines.append(line)

        # Escribir las líneas filtradas al archivo de salida en UTF-8
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(filtered_lines))

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
            # Verificar si hay conflictos
            result = run_command("git status --porcelain", cwd=REPO_PATH, ignore_errors=True)
            conflicts = [line for line in result.splitlines() if line.startswith("UU")]

            if conflicts:
                print("\033[31m\nConflictos detectados:\033[0m")
                for conflict in conflicts:
                    print(f"  - {conflict.split()[-1]}")
                input("\033[31mPresiona ENTER tras resolver los conflictos y añadir los archivos a staged changes\033[0m")
            else:
                print("\033[32mNo se detectaron conflictos. Continuando...\033[0m")


            export_diff_to_file(repo, f"{commit_id}^1", commit_id, original_diff_file)
            export_diff_to_file(repo, None, None, local_diff_file, cached=True)
            contar_lineas_modificadas()
            print("Comparando diferencias entre original y local...")
            if compare_diff_files_with_context(original_diff_file, local_diff_file):
                print("\033[32m\nNo se encontraron discrepancias.\033[0m")
                print("Realizando commit...")
                command = f'git commit --no-verify'
                run_command(command, cwd=REPO_PATH, ignore_errors=True)
                break

            # Validar integración de cambios si hay discrepancias
            print("\nValidando si los cambios de la pull request están correctamente integrados en el archivo local...")
            if verificar_cambios_integrados(pull_request_file="original_diff.txt",local_diff_file="local_diff.txt",repo_path=REPO_PATH,output_file="diferencias_reportadas.txt"):
                print("\033[32mLos cambios parecen estar integrados correctamente.\033[0m")
                print("Realizando commit...")
                command = f'git commit --no-verify'
                run_command(command, cwd=REPO_PATH, ignore_errors=True)
                break

            # Preguntar al usuario si quiere continuar con las discrepancias
            respuesta = input("¿Deseas intentar resolver las discrepancias nuevamente? (s/n): ").lower()
            if respuesta != "s":
                print("Proceso detenido por el usuario.")
                raise Exception("Discrepancias no resueltas.")
    except Exception as e:
        print(f"Error durante el cherry-pick y validación: {e}")
        contar_lineas_modificadas()

def verificar_cambios_integrados(pull_request_file, local_diff_file, repo_path, output_file="diferencias_reportadas.txt"):
    """
    Verifica si los cambios de una pull request están correctamente integrados en los archivos locales,
    manejando nombres de archivos con espacios.

    :param pull_request_file: Ruta al archivo con los cambios de la pull request (original_diff.txt).
    :param local_diff_file: Ruta al archivo con los cambios locales (local_diff.txt).
    :param repo_path: Ruta al repositorio para localizar los archivos afectados.
    :param output_file: Ruta del archivo donde exportar las discrepancias detectadas.
    """
    try:
        # Leer los archivos de diferencias
        with open(pull_request_file, "r", encoding="utf-8") as pr_file:
            pr_lines = pr_file.readlines()

        # Extraer líneas añadidas (verdes) y eliminadas (rojas) del archivo original
        added_lines = {line[1:].strip() for line in pr_lines if line.startswith('+') and not line.startswith('+++') and line.strip()}
        removed_lines = {line[1:].strip() for line in pr_lines if line.startswith('-') and not line.startswith('---') and line.strip()}

        # Identificar los archivos afectados en la pull request
        file_changes = {}
        current_file = None
        for line in pr_lines:
            if line.startswith("diff --git"):
                # Escapar espacios en las rutas
                file_path = line.split()[-1].replace("b/", "").strip()
                current_file = os.path.normpath(file_path)
                file_changes[current_file] = {"added": set(), "removed": set()}
            elif line.startswith('+') and not line.startswith('+++') and line.strip():
                file_changes[current_file]["added"].add(line[1:].strip())
            elif line.startswith('-') and not line.startswith('---') and line.strip():
                file_changes[current_file]["removed"].add(line[1:].strip())

        # Crear un reporte detallado
        discrepancies = []
        discrepancies.append(f"Reporte de validación entre {pull_request_file} y {local_diff_file}\n")
        discrepancies.append("=" * 80 + "\n")

        for file, changes in file_changes.items():
            # Construir la ruta completa escapando espacios
            file_path = os.path.join(repo_path, file)
            if not os.path.exists(file_path):
                discrepancies.append(f"⚠ El archivo \"{file_path}\" no existe en el sistema local.\n")
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                local_file_content = {line.strip() for line in f.readlines()}

            # Verificar líneas añadidas (independiente de la posición)
            missing_added = changes["added"] - local_file_content
            if missing_added:
                discrepancies.append(f"⚠ Líneas añadidas que faltan en el archivo \"{file_path}\":\n")
                for line in missing_added:
                    discrepancies.append(f"  + {line}\n")
            else:
                discrepancies.append(f"✔ Todas las líneas añadidas están presentes en el archivo \"{file_path}\".\n")

            # Verificar líneas eliminadas (independiente de la posición)
            present_removed = changes["removed"] & local_file_content
            if present_removed:
                discrepancies.append(f"⚠ Líneas eliminadas que aún están presentes en el archivo \"{file_path}\":\n")
                for line in present_removed:
                    discrepancies.append(f"  - {line}\n")
            else:
                discrepancies.append(f"✔ Todas las líneas eliminadas han sido correctamente eliminadas del archivo \"{file_path}\".\n")

        # Exportar el reporte a un archivo
        with open(output_file, "w", encoding="utf-8") as report_file:
            report_file.writelines(discrepancies)

        print(f"\n{Fore.YELLOW}Reporte de discrepancias exportado a: {output_file}{Style.RESET_ALL}")
        return len(discrepancies) == 2  # Si solo hay el encabezado, no hubo discrepancias

    except Exception as e:
        print(f"{Fore.RED}Error verificando los cambios: {e}{Style.RESET_ALL}")
        return False


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
def eliminar_lineas_duplicadas(archivo):
    """
    Elimina líneas duplicadas de un archivo, preservando el orden original.

    :param archivo: Ruta al archivo donde eliminar duplicados.
    """
    try:
        print(f"Procesando el archivo: {archivo}")
        
        # Leer el contenido del archivo
        with open(archivo, "r", encoding="utf-8") as f:
            lineas = f.readlines()
        
        # Eliminar duplicados mientras se preserva el orden
        lineas_unicas = list(dict.fromkeys(lineas))
        
        # Sobrescribir el archivo con las líneas únicas
        with open(archivo, "w", encoding="utf-8") as f:
            f.writelines(lineas_unicas)
        
        print(f"Archivo procesado: {archivo}. Se eliminaron líneas duplicadas.")
    
    except FileNotFoundError:
        print(f"El archivo {archivo} no existe. No se puede procesar.")
    except Exception as e:
        print(f"Error procesando el archivo {archivo}: {e}")



def hacer_push_y_abrir_pr(repo):
    """
    Pregunta al usuario si desea hacer push de la rama actual al remoto.
    Si la rama no existe en el remoto, la publica automáticamente.
    Luego, abre la URL para crear una pull request.
    """
    try:
        # Obtener la rama actual
        current_branch = repo.git.rev_parse("--abbrev-ref", "HEAD")
        print(f"Estás en la rama: {current_branch}")

        # Preguntar si se desea hacer push
        respuesta = input("¿Deseas hacer push al remoto? (s/n): ").strip().lower()
        if respuesta != "s":
            print("Push cancelado por el usuario.")
            return

        # Verificar si la rama existe en el remoto
        remote_branches = repo.git.branch("-r")
        remote_branch = f"origin/{current_branch}"
        if remote_branch not in remote_branches:
            print(f"La rama {current_branch} no existe en el remoto. Publicándola...")
            repo.git.push("-u", "origin", current_branch)
            print(f"Rama {current_branch} publicada en el remoto.")
        else:
            print(f"La rama {current_branch} ya existe en el remoto. Haciendo push...")
            repo.git.push()
            print("Push realizado con éxito.")

        # Abrir la URL para crear la pull request
        pr_url = f"https://bitbucket.org/iberdrola-clientes/iberdrola-sfdx/pull-requests/new?source={current_branch}&t=1"
        print(f"Abriendo la URL para crear la pull request: {pr_url}")
        webbrowser.open(pr_url)
    except Exception as e:
        print(f"Error al hacer push o abrir la URL de la pull request: {e}")


def main():
    repo = Repo(REPO_PATH)
    for pr_id in PULL_REQUESTS:
        try:
            print(f"\033[34mProcesando PR #{pr_id}...\033[0m")
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

        # Eliminar los archivos local_diff.txt, original_diff.txt y diferencias_reportadas.txt
        local_diff_file = os.path.join(REPO_PATH, "local_diff.txt")
        original_diff_file = os.path.join(REPO_PATH, "original_diff.txt")
        diferencias_reportadas_file = os.path.join(REPO_PATH, "diferencias_reportadas.txt")

        for diff_file in [local_diff_file, original_diff_file, diferencias_reportadas_file]:
            if os.path.exists(diff_file):
                os.remove(diff_file)
                print(f"Archivo eliminado: {diff_file}")
            else:
                print(f"Archivo no encontrado, no es necesario eliminar: {diff_file}")
        
        eliminar_lineas_duplicadas(os.path.join(REPO_PATH, "config/tests-to-run.list"))

        print("\033[33mRecuerda copiar de las RN la tabla verde + sus pasos manuales. Revisa también la hoja de ProcessBuilder_Flow.\033[0m")
        print("\033[33mCambia el estado de la solicitud en el teams IBD si no quedan más PR\033[0m")
        input("Presiona ENTER para proceder con la siguiente PR tras hacer commit.")
    
    hacer_push_y_abrir_pr(repo)

if __name__ == "__main__":
    main()