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
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        if ignore_errors:
            print(f"")
        else:
            print(f"Error ejecutando {command}:\n{result.stderr}")
            raise Exception(result.stderr)
    return result.stdout.strip()

def export_diff_to_file(repo, commit_base, commit_to, output_file, cached=False):
    try:
        if isinstance(repo, str):
            repo_path = repo
        elif hasattr(repo, "working_dir"):
            repo_path = repo.working_dir
        else:
            raise ValueError(f"repo debe ser una cadena o un objeto Repo. Recibido: {type(repo)}")

        if not os.path.isdir(repo_path):
            raise ValueError(f"La ruta '{repo_path}' no apunta a un directorio existente.")

        exclude_files = [
            "config/tests-to-run.list",
            "config/core-tests-to-run.list"
        ]

        if cached:
            command = f"git diff --cached --unified=0"
        elif commit_base and commit_to:
            command = f"git diff --unified=0 \"{commit_base}\" \"{commit_to}\""
        else:
            raise ValueError("Se requiere commit_base y commit_to para el diff no cached.")

        print(f"Ejecutando comando: {command}")
        result = subprocess.run(
            command,
            cwd=repo_path,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )

        if result.returncode != 0:
            print(f"Error ejecutando el comando: {result.stderr.strip()}")
            raise Exception(f"Error exportando diferencias: {result.stderr.strip()}")

        lines = result.stdout.splitlines()
        filtered_lines = []
        exclude_pattern = re.compile(r"^diff --git a/(.*) b/(.*)$")
        exclude_active = False

        for line in lines:
            match = exclude_pattern.match(line)
            if match:
                current_file = match.group(1)
                if any(exclude in current_file for exclude in exclude_files):
                    exclude_active = True
                    continue
                else:
                    exclude_active = False

            if not exclude_active:
                filtered_lines.append(line)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(filtered_lines))

        if not os.path.exists(output_file) or os.stat(output_file).st_size == 0:
            raise Exception(f"El archivo {output_file} no se generó o está vacío.")

    except Exception as e:
        print(f"Error exportando diferencias: {e}")
        raise

def abrir_pull_request_en_navegador(pr_id):
    url = f"https://bitbucket.org/iberdrola-clientes/iberdrola-sfdx/pull-requests/{pr_id}/diff"
    print(f"Abriendo la Pull Request #{pr_id} en el navegador: {url}")
    webbrowser.open(url)

def compare_diff_files(original_diff_file, local_diff_file):
    discrepancies_found = False

    with open(original_diff_file, "r", encoding="utf-8") as original_file:
        original_lines = original_file.readlines()

    with open(local_diff_file, "r", encoding="utf-8") as local_file:
        local_lines = local_file.readlines()

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

def compare_diff_files_with_context(file1, file2):
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
                print("\n¡Se detectaron discrepancias!")
                contar_lineas_modificadas()
                return False
            else:
                print("\n¡No se detectaron discrepancias! Los cambios coinciden exactamente.")
                return True
    except Exception as e:
        print(f"Error comparando archivos: {e}")
        return False

def realizar_cherry_pick_y_validar(repo, commit_id):
    try:
        print(f"Realizando cherry-pick del commit {commit_id}...")
        command = f'git cherry-pick -x --no-commit -m 1 {commit_id}'
        run_command(command, cwd=REPO_PATH, ignore_errors=True)
        eliminar_lineas_duplicadas(os.path.join(REPO_PATH, "config/tests-to-run.list"))
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
            if compare_diff_files_with_context(original_diff_file, local_diff_file):
                print("\033[32m\nNo se encontraron discrepancias.\033[0m")
                print("Realizando commit...")
                command = f'git commit --no-verify --no-edit'
                run_command(command, cwd=REPO_PATH, ignore_errors=True)
                break

            print("\nValidando si los cambios de la pull request están correctamente integrados en el archivo local...")
            if verificar_cambios_integrados(pull_request_file="original_diff.txt",local_diff_file="local_diff.txt",repo_path=REPO_PATH,output_file="diferencias_reportadas.txt"):
                print("\033[32mLos cambios parecen estar integrados correctamente.\033[0m")
                print("Realizando commit...")
                command = f'git commit --no-verify'
                run_command(command, cwd=REPO_PATH, ignore_errors=True)
                break

            respuesta = input("¿Deseas intentar resolver las discrepancias nuevamente? (s/n): ").lower()
            if respuesta != "s":
                raise Exception("Discrepancias no resueltas.")
    except Exception as e:
        print(f"Error durante el cherry-pick y validación: {e}")
        contar_lineas_modificadas()

def verificar_cambios_integrados(pull_request_file, local_diff_file, repo_path, output_file="diferencias_reportadas.txt"):
    try:
        with open(pull_request_file, "r", encoding="utf-8") as pr_file:
            pr_lines = pr_file.readlines()

        added_lines = {line[1:].strip() for line in pr_lines if line.startswith('+') and not line.startswith('+++') and line.strip()}
        removed_lines = {line[1:].strip() for line in pr_lines if line.startswith('-') and not line.startswith('---') and line.strip()}

        file_changes = {}
        current_file = None
        for line in pr_lines:
            if line.startswith("diff --git"):
                file_path = line.split()[-1].replace("b/", "").strip()
                current_file = os.path.normpath(file_path)
                file_changes[current_file] = {"added": set(), "removed": set()}
            elif line.startswith('+') and not line.startswith('+++') and line.strip():
                file_changes[current_file]["added"].add(line[1:].strip())
            elif line.startswith('-') and not line.startswith('---') and line.strip():
                file_changes[current_file]["removed"].add(line[1:].strip())

        discrepancies = []
        discrepancies.append(f"Reporte de validación entre {pull_request_file} y {local_diff_file}\n")
        discrepancies.append("=" * 80 + "\n")

        for file, changes in file_changes.items():
            file_path = os.path.join(repo_path, file)
            if not os.path.exists(file_path):
                discrepancies.append(f"⚠ El archivo \"{file_path}\" no existe en el sistema local.\n")
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                local_file_content = {line.strip() for line in f.readlines()}

            missing_added = changes["added"] - local_file_content
            if missing_added:
                discrepancies.append(f"⚠ Líneas añadidas que faltan en el archivo \"{file_path}\":\n")
                for line in missing_added:
                    discrepancies.append(f"  + {line}\n")

            present_removed = changes["removed"] & local_file_content
            if present_removed:
                discrepancies.append(f"⚠ Líneas eliminadas que aún están presentes en el archivo \"{file_path}\":\n")
                for line in present_removed:
                    discrepancies.append(f"  - {line}\n")

        with open(output_file, "w", encoding="utf-8") as report_file:
            report_file.writelines(discrepancies)

        print(f"\n{Fore.YELLOW}Reporte de discrepancias exportado a: {output_file}{Style.RESET_ALL}")
        return len(discrepancies) == 2

    except Exception as e:
        print(f"{Fore.RED}Error verificando los cambios: {e}{Style.RESET_ALL}")
        return False

def contar_lineas_modificadas():
    try:
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

        print(f"{'Archivo':<50} {'Líneas Añadidas':<15} {'Líneas Eliminadas':<15}")
        print("="*80)
        for archivo in archivos:
            print(f"{archivo['archivo']:<50} {archivo['lineas_agregadas']:<15} {archivo['lineas_eliminadas']:<15}")
        
        print("="*80)
        print(f"{'TOTAL':<50} {total_agregadas:<15} {total_eliminadas:<15}")
        print(f"Líneas modificadas en total (añadidas + eliminadas): {total_agregadas + total_eliminadas}")

    except Exception as e:
        print(f"Error al contar líneas modificadas: {e}")

def eliminar_lineas_duplicadas(archivo):
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            lineas = f.readlines()
        
        lineas_unicas = list(dict.fromkeys(lineas))
        
        with open(archivo, "w", encoding="utf-8") as f:
            f.writelines(lineas_unicas)
        
        print(f"Archivo procesado: {archivo}. Se eliminaron líneas duplicadas.")
    
    except FileNotFoundError:
        print(f"El archivo {archivo} no existe. No se puede procesar.")
    except Exception as e:
        print(f"Error procesando el archivo {archivo}: {e}")

def hacer_push_y_abrir_pr(repo):
    try:
        current_branch = repo.git.rev_parse("--abbrev-ref", "HEAD")
        print(f"Estás en la rama: {current_branch}")

        respuesta = input("¿Deseas hacer push al remoto? (s/n): ").strip().lower()
        if respuesta != "s":
            print("Push cancelado por el usuario.")
            return

        remote_branches = repo.git.branch("-r")
        remote_branch = f"origin/{current_branch}"
        if remote_branch not in remote_branches:
            print(f"La rama {current_branch} no existe en el remoto. Publicándola...")
            repo.git.push("-u", "origin", current_branch)
            print(f"Rama {current_branch} publicada en el remoto.")
            pr_url = f"https://bitbucket.org/iberdrola-clientes/iberdrola-sfdx/pull-requests/new?source={current_branch}&t=1"
            webbrowser.open(pr_url)
        else:
            repo.git.push()
            print("Push realizado con éxito.")

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
      
        
        print(f"\033[34mFinalizada la PR #{pr_id}...\033[0m")
        print("\033[33mRecuerda copiar de las RN la tabla verde + sus pasos manuales. Revisa también la hoja de ProcessBuilder_Flow.\033[0m")
        print("\033[33mCambia el estado de la solicitud en el teams IBD si no quedan más PR\033[0m")
        input("Presiona ENTER para proceder con la siguiente PR tras hacer commit.")
    
    hacer_push_y_abrir_pr(repo)

if __name__ == "__main__":
    main()