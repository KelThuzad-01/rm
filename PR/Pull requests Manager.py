import os
import subprocess
import webbrowser
import re
from git import Repo
import time
from colorama import Fore, Style, init
init(autoreset=True)


# Configuración principal

PULL_REQUESTS = [
]  # Lista de IDs de las Pull Requests.

REPO_PATH = "C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx"
profile_path = "C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\force-app\\main\\default\\profiles"
permission_set_path = "C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx\\force-app\\main\\default\\permissionsets"

EXCLUDE_LINES = [
    "<default>false</default>", "<default>true</default>", "+++ b/", "--- a/", "force-app/main/default",
    "<isActive>false</isActive>", "<isActive>true</isActive>", "<editable>", "- <editable>",
    "  - <fieldPermissions>", "  - <readable>true</readable>", "  - </fieldPermissions>",
    "  - <readable>true</readable>", "  - <editable>false</editable>", "<fieldPermissions>",
    "</fieldPermissions>", "<readable>", "force-app", " force-app", ".xml", "diff --cc", "}", "{",
    "else", "<locationY>", "- <locationY>", "<locationX>", "<conditionLogic>", "<valueSettings>",
    "<picklistValues>", "<standardValue>", "</values>", "<values>", "</standardValue>",
    "</picklistValues>", "<inputAssignments>", "</inputAssignments>", " <locationY>",
    "<collectionProcessors>", " <collectionProcessors>", " <rightValue>", " </rightValue>",
    "<editable>false</editable>", "<readable>true</readable>", " <default>false</default>",
    " <values>", "<connector>", "</connector>", "<assignmentItems>", "</assignmentItems>", 
    "<defaultConnectorLabel>", "<readable>", "<editable>", "<elementReference>", " <readable>",
    "<conditionLogic>"
]

delete_script_templates = {
    'field': r'node "C:\\Users\\aberdun\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileFieldpermissionsReferencesByObjectOrField.mjs" "{profile_path}" "{field_name}"',
    'record_type': r'node "C:\\Users\\aberdun\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileRecordTypepermissionsReferences.mjs" "{profile_path}" "{record_type_name}"',
    'object': r'node "C:\\Users\\aberdun\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileObjectpermissionsReferences.mjs" "{profile_path}" "{object_name}"',
    'class': r'node "C:\\Users\\aberdun\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileClasspermissionsReferencesByObjectOrField.mjs" "{profile_path}" "{class_name}"',
    'apex_page': r'node "C:\\Users\\aberdun\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileApexPagepermissionsReferencesByObjectOrField.mjs" "{profile_path}" "{apex_page_name}"',
    'flow_access': r'node "C:\\Users\\aberdun\Downloads\\rm\\Metadata Management\\Errors\deleteProfileFlowaccessesReferencesByFlow.mjs" "{profile_path}" "{flow_access_name}',
    'layout': r'node "C:\\Users\\aberdun\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileLayoutAssignmentsReferences.mjs" "{profile_path}" "{layout_name}"',
    'user_permission': r'node "C:\\Users\\aberdun\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileUserPermissionsReferences.mjs" "{profile_path}" "{user_permission_name}"'
}

def run_command(command, cwd=None, ignore_errors=False):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        if ignore_errors:
            print(f"")
        else:
            print(f"Error ejecutando {command}:\n{result.stderr}")
            raise Exception(result.stderr)
    return result.stdout.strip()


    try:
        if not os.path.exists(conflicts_file):
            print(f"Archivo de conflictos no encontrado: {conflicts_file}")
            return

        if not os.path.exists(original_diff_file):
            print(f"Archivo original_diff no encontrado: {original_diff_file}")
            return

        def clean_lines(lines):
            """Limpia y normaliza las líneas para comparación."""
            cleaned = []
            for line in lines:
                line = line.strip()
                if line.startswith('<<<<<<<') or line.startswith('=======') or line.startswith('>>>>>>>'):
                    continue
                cleaned.append(' '.join(line.split()))  # Normaliza espacios
            return set(cleaned)

        # Leer y limpiar conflictos
        with open(conflicts_file, "r", encoding="utf-8") as conflicts:
            conflict_lines = clean_lines(conflicts.readlines())

        # Leer y limpiar original_diff
        with open(original_diff_file, "r", encoding="utf-8") as original_diff:
            original_lines = clean_lines(original_diff.readlines())

        # Filtrar líneas excluidas
        original_lines = {
            line for line in original_lines
            if not any(exclude in line for exclude in EXCLUDE_LINES)
        }

        # Encontrar coincidencias
        matching_lines = conflict_lines & original_lines

        if matching_lines:
            print("\033[33mCoincidencias encontradas en los conflictos:\033[0m")
            for line in matching_lines:
                print(f"  - {line}")
        else:
            print("\033[32mNo se encontraron coincidencias entre los conflictos y original_diff.txt. No aceptes incoming, mantén current\033[0m")

            # Resolver conflictos utilizando "Accept Current"
            try:
                print("Resolviendo conflictos con la estrategia 'Accept Current'...")
                command = "git diff --name-only --diff-filter=U"
                result = subprocess.run(command, cwd=REPO_PATH, shell=True, capture_output=True, text=True, check=True)
                files = result.stdout.strip().splitlines()

                for file in files:
                    resolve_command = f"git checkout --ours {file}"
                    subprocess.run(resolve_command, cwd=REPO_PATH, shell=True, check=True)
                    add_command = f"git add {file}"
                    subprocess.run(add_command, cwd=REPO_PATH, shell=True, check=True)

                print("\033[32mConflictos resueltos automáticamente con 'Accept Current' y añadidos al stage.\033[0m")
            except subprocess.CalledProcessError as e:
                print(f"\033[31mError al resolver conflictos automáticamente: {e}\033[0m")

    except Exception as e:
        print(f"Error comparando conflictos con original_diff: {e}")

    try:
        if not os.path.exists(conflicts_file):
            print(f"Archivo de conflictos no encontrado: {conflicts_file}")
            return

        if not os.path.exists(original_diff_file):
            print(f"Archivo original_diff no encontrado: {original_diff_file}")
            return

        def clean_line(line):
            """Limpia y normaliza una línea para comparación."""
            line = line.strip()
            if line.startswith(('<<<<<<<', '=======', '>>>>>>>')):
                return ""  # Ignorar marcas de conflicto
            if line.startswith(('+', '-')):
                line = line[1:]  # Remover prefijos '+' o '-'
            return ' '.join(line.split())  # Normaliza espacios

        # Leer y limpiar conflictos
        with open(conflicts_file, "r", encoding="utf-8") as conflicts:
            conflict_lines = {}
            current_file = None
            for line in conflicts:
                line = clean_line(line)
                if line.startswith("diff --git a/"):
                    current_file = line.split()[-1]
                elif line and current_file:
                    conflict_lines.setdefault(current_file, set()).add(line)

        # Leer y limpiar original_diff
        with open(original_diff_file, "r", encoding="utf-8") as original_diff:
            original_lines = {clean_line(line) for line in original_diff if clean_line(line)}

        # Filtrar líneas excluidas para comparación
        filtered_original_lines = {
            line for line in original_lines
            if not any(exclude in line for exclude in EXCLUDE_LINES)
        }

        # Encontrar coincidencias y asociarlas con archivos
        matching_files = {}
        for file, lines in conflict_lines.items():
            matching_lines = lines & filtered_original_lines
            if matching_lines:
                matching_files[file] = matching_lines

        if matching_files:
            print("\033[33mCoincidencias encontradas en los conflictos:\033[0m")
            for file, lines in matching_files.items():
                print(f"\033[36mArchivo: {file}\033[0m")
                for line in lines:
                    print(f"  - {line}")
        else:
            print("\033[32mNo se encontraron coincidencias entre los conflictos y original_diff.txt.No aceptes incoming, mantén current\033[0m")

    except subprocess.CalledProcessError as e:
        print(f"\033[31mError al resolver conflictos automáticamente: {e}\033[0m")
    except Exception as e:
        print(f"Error comparando conflictos con original_diff: {e}")

    try:
        if not os.path.exists(conflicts_file):
            print(f"Archivo de conflictos no encontrado: {conflicts_file}")
            return
        if not os.path.exists(original_diff_file):
            print(f"Archivo original_diff no encontrado: {original_diff_file}")
            return

        def clean_line(line):
            line = line.strip()
            if line.startswith(('<<<<<<<', '=======', '>>>>>>>')):
                return ""
            if line.startswith(('+', '-')):
                line = line[1:]
            return ' '.join(line.split())

        # Leer y limpiar los archivos de conflictos y original_diff
        conflict_lines_by_file = {}
        current_file = None
        with open(conflicts_file, "r", encoding="utf-8") as conflicts:
            for line in conflicts:
                if line.startswith("diff --git a/"):
                    current_file = line.split(" b/")[-1].strip()
                    conflict_lines_by_file[current_file] = set()
                elif current_file:
                    cleaned_line = clean_line(line)
                    if cleaned_line and not any(exclude in cleaned_line for exclude in EXCLUDE_LINES):
                        conflict_lines_by_file[current_file].add(cleaned_line)

        original_lines = set()
        with open(original_diff_file, "r", encoding="utf-8") as original_diff:
            for line in original_diff:
                cleaned_line = clean_line(line)
                if cleaned_line and not any(exclude in cleaned_line for exclude in EXCLUDE_LINES):
                    original_lines.add(cleaned_line)

        found_conflicts = False
        for file, conflict_lines in conflict_lines_by_file.items():
            matching_lines = conflict_lines & original_lines
            if matching_lines:
                found_conflicts = True
                print(f"\033[33mCoincidencias encontradas, acepta las siguientes líneas incoming y el resto current en el archivo: {file}\033[0m")
                for line in matching_lines:
                    print(f"  - {line}")

        if not found_conflicts:
            print("\033[32mNo se encontraron coincidencias entre los conflictos y original_diff.txt.No aceptes incoming, mantén current\033[0m")

    except Exception as e:
        print(f"Error comparando conflictos con original_diff: {e}")


def compare_conflicts_with_original_diff(conflicts_file, original_diff_file):
    try:
        if not os.path.exists(conflicts_file):
            print(f"{Fore.RED}Archivo de conflictos no encontrado: {conflicts_file}{Style.RESET_ALL}")
            return
        if not os.path.exists(original_diff_file):
            print(f"{Fore.RED}Archivo original_diff no encontrado: {original_diff_file}{Style.RESET_ALL}")
            return

        def clean_line(line):
            """Limpia y normaliza una línea para comparación."""
            line = line.strip()

            # Ignorar marcas de conflicto y prefijos de git
            if line.startswith(('<<<<<<<', '=======', '>>>>>>>', '@@', 'diff --cc', 'index', '--- a/', '+++ b/')):
                return ""

            # Remover indicadores de cambios en la comparación (`+`, `-`, `++`)
            if line.startswith(('+', '-', '++')):
                line = line[1:]

            return ' '.join(line.split())  # Normaliza espacios

        # Leer y limpiar los archivos de conflictos y original_diff
        conflict_lines_by_file = {}
        current_file = None
        with open(conflicts_file, "r", encoding="utf-8") as conflicts:
            for line in conflicts:
                if line.startswith("diff --cc "):  # Detección correcta del inicio de un archivo
                    current_file = line.split("diff --cc ")[-1].strip()
                    conflict_lines_by_file[current_file] = set()
                elif current_file:
                    cleaned_line = clean_line(line)
                    if cleaned_line:
                        conflict_lines_by_file[current_file].add(cleaned_line)

        # Filtrar archivos sin líneas en conflicto
        conflict_lines_by_file = {file: lines for file, lines in conflict_lines_by_file.items() if lines}

        # Depuración: Mostrar solo archivos que realmente tienen líneas en conflicto
        if conflict_lines_by_file:
            print("\n🔍 Archivos con conflictos detectados:")
            for file, lines in conflict_lines_by_file.items():
                print(f"  - {file} ({len(lines)} líneas)")

        original_lines = set()
        with open(original_diff_file, "r", encoding="utf-8") as original_diff:
            for line in original_diff:
                cleaned_line = clean_line(line)
                if cleaned_line:
                    original_lines.add(cleaned_line)

        found_conflicts = False
        for file, conflict_lines in conflict_lines_by_file.items():
            matching_lines = conflict_lines & original_lines
            if matching_lines:
                found_conflicts = True
                print(f"\n\033[33mCoincidencias encontradas, acepta incoming en lo siguiente y el resto current en el archivo: {file}\033[0m")
                for line in matching_lines:
                    print(f"  - {line}")

        if not found_conflicts:
            print("\n\033[32mNo se encontraron coincidencias entre los conflictos y original_diff.txt.\033[0m")

    except Exception as e:
        print(f"Error comparando conflictos con original_diff: {e}")


def export_conflicts_to_file(repo_path, conflicts_file):
    try:
        # Ejecutar git diff para detectar conflictos
        command = "git diff --diff-filter=U"
        result = subprocess.run(
            command,
            cwd=repo_path,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8"  # Aseguramos que se use UTF-8
        )
        if result.returncode != 0:
            raise Exception(f"Error ejecutando git diff: {result.stderr}")
        
        # Guardar el resultado en el archivo con codificación UTF-8
        with open(conflicts_file, "w", encoding="utf-8") as f:
            f.write(result.stdout)

        print(f"Conflictos guardados en: {conflicts_file}")
    except Exception as e:
        print(f"Error guardando conflictos: {e}")


def resolver_conflictos_tests_to_run(archivo):
    """
    Resolver automáticamente los conflictos en el archivo `config/tests-to-run.list` 
    aceptando únicamente las líneas añadidas y omitiendo las eliminadas.
    """
    try:
        if not os.path.exists(archivo):
            print(f"El archivo {archivo} no existe. No hay conflictos que resolver.")
            return False

        with open(archivo, "r", encoding="utf-8") as f:
            lines = f.readlines()

        resolved_lines = []
        in_conflict = False
        current_section = []  # Almacena líneas de una sección de conflicto

        for line in lines:
            if line.startswith("<<<<<<<"):
                in_conflict = True
                current_section = []  # Inicializa la sección de conflicto
            elif line.startswith("======="):
                # Termina la primera parte del conflicto, comienza la segunda
                continue
            elif line.startswith(">>>>>>>"):
                # Final del conflicto, resolver aceptando únicamente líneas nuevas
                in_conflict = False
                # Filtrar solo las líneas que no comienzan con "-"
                resolved_lines.extend([l for l in current_section if not l.startswith("-")])
                current_section = []
            else:
                if in_conflict:
                    # Agregar línea en conflicto a la sección actual
                    current_section.append(line.strip())
                else:
                    # Línea fuera de conflicto, agregarla al resultado
                    resolved_lines.append(line.strip())

        # Sobrescribir el archivo con los cambios resueltos
        with open(archivo, "w", encoding="utf-8") as f:
            f.write("\n".join(resolved_lines) + "\n")

        print(f"Conflictos resueltos automáticamente en el archivo: {archivo}")
        return True

    except Exception as e:
        print(f"Error resolviendo conflictos en {archivo}: {e}")
        return False

def extract_errors(output):
    patterns = {
        'field': re.findall(r'In field: field - no CustomField named\s+([^\s]+)\s+found', output),
        'record_type': re.findall(r'In field: recordType - no RecordType named\s+([^\s]+)\s+found', output),
        'object': re.findall(r'In field: field - no CustomObject named\s+([^\s]+)\s+found', output),
        'class': re.findall(r'In field: apexClass - no ApexClass named\s+([^\s]+)\s+found', output),
        'apex_page': re.findall(r'In field: apexPage - no ApexPage named\s+([^\s]+)\s+found', output),
        'flow_access': re.findall(r'In field: flow - no FlowDefinition named\s+([^\s]+)\s+found', output),
        'layout': re.findall(r'In field: layout - no Layout named\s+([^\s]+)\s+found', output),
        'user_permission': re.findall(r'Unknown user permission:\s+([^\s]+)', output)
    }
    return patterns

def process_deployment():
    fields_found = True
    deployment_attempts = 0

    while fields_found:
        deployment_attempts += 1
        print(f'Starting deployment... (Attempt {deployment_attempts})')
        output = execute_command(deploy_command)
        print('Deployment output:', output)

        errors = extract_errors(output)
        action_taken = False

        for key, items in errors.items():
            for item_name in items:
                print(f'Extracted {key}:', item_name)
                
                for path in [profile_path, permission_set_path]:
                    delete_script = delete_script_templates[key].format(profile_path=path, **{f'{key}_name': item_name})
                    print(f'Running delete script for {key} at {path}...')
                    delete_output = execute_command(delete_script)
                    print('Delete script output:', delete_output)
                
                action_taken = True
        
        if not action_taken:
            print('No further action required.')
            print('\a')  # Beep sound
            fields_found = False

def ejecutar_pre_push():
    """
    Detecta automáticamente el entorno de despliegue basado en la rama actual
    y ejecuta los comandos correspondientes.
    """
    try:
        # Obtener la rama actual
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=REPO_PATH,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Error obteniendo la rama actual: {result.stderr}")
            return

        current_branch = result.stdout.strip()
        print(f"Estás en la rama: {current_branch}")

        # Detectar entorno basado en la rama
        if "UAT2" in current_branch:
            print("\nDetectado entorno UAT2. Ejecutando comandos para QA...")
            comandos = [
                "git fetch --all",
                "sf sgd source delta --from origin/develop --output-dir deploy-manifest --ignore-file .deltaignore --ignore-whitespace --source-dir force-app"
            ]
            for comando in comandos:
                print(f"Ejecutando: {comando}")
                result = subprocess.run(comando, shell=True, text=True)
                if result.returncode != 0:
                    print(f"Error ejecutando el comando: {comando}")
                    return

            print("\nComandos ejecutados correctamente.")
            deploy_command = "sf project deploy start --target-org QA-IBD --manifest deploy-manifest/package/package.xml --post-destructive-changes deploy-manifest/destructiveChanges/destructiveChanges.xml --dry-run --wait 240 --ignore-warnings --concise --ignore-conflicts"
            process_deployment()

        elif "PROD" in current_branch:
            print("\nDetectado entorno PROD. Ejecutando comandos para PROD...")
            comandos = [
                "git fetch --all",
                "sf sgd source delta --from origin/master --output-dir deploy-manifest --ignore-file .deltaignore --ignore-whitespace --source-dir force-app",
            ]
            for comando in comandos:
                print(f"Ejecutando: {comando}")
                result = subprocess.run(comando, shell=True, text=True)
                if result.returncode != 0:
                    print(f"Error ejecutando el comando: {comando}")
                    return

            print("\nComandos ejecutados correctamente.")
            deploy_command = "sf project deploy start --target-org IBD-prod --manifest deploy-manifest/package/package.xml --post-destructive-changes deploy-manifest/destructiveChanges/destructiveChanges.xml --dry-run --wait 240 --ignore-warnings --concise --ignore-conflicts"
            process_deployment()
            
        else:
            print("\nNo se detectó un entorno compatible en la rama actual. Por favor, verifica la rama.")
            return

    except Exception as e:
        print(f"Error en ejecutar_pre_push: {e}")

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

def compare_diff_files_with_context(file1, file2, output_file="diferencias_reportadas.txt"):
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

            # Filtrar diferencias excluidas
            filtered_differences = [
                line for line in differences
                if not any(exclude in line for exclude in EXCLUDE_LINES)
            ]

            if filtered_differences:
                print("\n¡Se detectaron discrepancias tras aplicar exclusiones!")

                # Guardar diferencias en el archivo de reporte, excluyendo las líneas de EXCLUDE_LINES
                with open(output_file, "w", encoding="utf-8") as report_file:
                    report_file.writelines(filtered_differences)

                print(f"\n{Fore.YELLOW}Reporte de discrepancias exportado a: {output_file}{Style.RESET_ALL}")
                return False
            else:
                print("\n¡No se detectaron discrepancias relevantes tras aplicar exclusiones!")
                return True
    except Exception as e:
        print(f"Error comparando archivos: {e}")
        return False

def realizar_cherry_pick_y_validar(repo, commit_id, pr_id):
    try:
        print(f"Realizando cherry-pick del commit {commit_id}...")
        command = f'git cherry-pick -x --no-commit -m 1 {commit_id}'
        run_command(command, cwd=REPO_PATH, ignore_errors=True)

        archivo_conflicto = os.path.join(REPO_PATH, "config/tests-to-run.list")
        # Resolver automáticamente conflictos en `config/tests-to-run.list`
        if os.path.exists(archivo_conflicto):
            print("Detectando conflictos en config/tests-to-run.list...")
            if resolver_conflictos_tests_to_run(archivo_conflicto):
                run_command(f"git add {archivo_conflicto}", cwd=REPO_PATH)
                print(f"Conflictos resueltos automáticamente y {archivo_conflicto} añadido a staged changes.")

        eliminar_lineas_duplicadas(os.path.join(REPO_PATH, "config/tests-to-run.list"))
        # Usar rutas completas para los archivos de diferencias
        original_diff_file = os.path.join(REPO_PATH, "original_diff.txt")
        export_diff_to_file(repo, f"{commit_id}^1", commit_id, original_diff_file)

        while True:
            # Verificar si hay conflictos
            result = run_command("git status --porcelain", cwd=REPO_PATH, ignore_errors=True)
            conflicts = [line for line in result.splitlines() if line.startswith("UU")]

            if conflicts:
                print("\033[31m\nConflictos detectados:\033[0m")
                abrir_pull_request_en_navegador(pr_id)
                conflicts_file = os.path.join(REPO_PATH, "conflicts.txt")
                export_conflicts_to_file(REPO_PATH, conflicts_file)
                compare_conflicts_with_original_diff(conflicts_file, original_diff_file)
                
                for conflict in conflicts:
                    print(f"  - {conflict.split()[-1]}")
                input("\033[31mPresiona ENTER tras resolver los conflictos y añadir los archivos a staged changes\033[0m")

            local_diff_file = os.path.join(REPO_PATH, "local_diff.txt")
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
                command = f'git commit --no-verify --no-edit'
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
        # Leer los archivos de diferencias
        with open(pull_request_file, "r", encoding="utf-8") as pr_file:
            pr_lines = pr_file.readlines()

        # Extraer líneas añadidas (verdes) y eliminadas (rojas)
        added_lines = {line[1:].strip() for line in pr_lines if line.startswith('+') and not line.startswith('+++')}
        removed_lines = {line[1:].strip() for line in pr_lines if line.startswith('-') and not line.startswith('---')}

        # Identificar líneas movidas (presentes tanto en añadidas como en eliminadas)
        moved_lines = removed_lines & added_lines
        removed_lines -= moved_lines  # Excluir líneas movidas de las eliminadas

        # Identificar los archivos afectados
        file_changes = {}
        current_file = None
        for line in pr_lines:
            if line.startswith("diff --git"):
                file_path = line.split()[-1].replace("b/", "").strip()
                current_file = os.path.normpath(file_path)
                file_changes[current_file] = {"added": set(), "removed": set()}
            elif line.startswith('+') and not line.startswith('+++'):
                file_changes[current_file]["added"].add(line[1:].strip())
            elif line.startswith('-') and not line.startswith('---'):
                file_changes[current_file]["removed"].add(line[1:].strip())

        # Crear un reporte detallado
        discrepancies = []
        discrepancies.append(f"Reporte de validación entre {pull_request_file} y {local_diff_file}\n")
        discrepancies.append("=" * 80 + "\n")

        all_changes_integrated = True

        for file, changes in file_changes.items():
            file_path = os.path.join(repo_path, file)
            # Ignorar archivos que no existen
            if not os.path.exists(file_path):
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                local_file_content = {line.strip() for line in f.readlines()}

            # Verificar líneas añadidas
            missing_added = changes["added"] - local_file_content
            if missing_added:
                all_changes_integrated = False
                discrepancies.append(f"⚠ Líneas añadidas que faltan en el archivo \"{file_path}\":\n")
                for line in missing_added:
                    discrepancies.append(f"  + {line}\n")

            # Verificar líneas eliminadas, excluyendo líneas movidas
            present_removed = (changes["removed"] - moved_lines) & local_file_content
            if present_removed:
                all_changes_integrated = False
                discrepancies.append(f"⚠ Líneas eliminadas que aún están presentes en el archivo \"{file_path}\":\n")
                for line in present_removed:
                    discrepancies.append(f"  - {line}\n")

        # Exportar el reporte a un archivo
        with open(output_file, "w", encoding="utf-8") as report_file:
            report_file.writelines(discrepancies)

        print(f"\n{Fore.YELLOW}Reporte de discrepancias exportado a: {output_file}{Style.RESET_ALL}")
        return all_changes_integrated

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
    PULL_REQUESTS.sort()
    command = f'git fetch --all'
    run_command(command, cwd=REPO_PATH, ignore_errors=True)
    command = f'git pull'
    run_command(command, cwd=REPO_PATH, ignore_errors=True)
    repo = Repo(REPO_PATH)
    for pr_id in PULL_REQUESTS:
        try:
            print(f"\033[34mProcesando PR #{pr_id}...\033[0m")
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
                print("Múltiples commits encontrados. Seleccionando automáticamente el commit de merge más reciente:")
                for i, commit_id in enumerate(commit_ids, 1):
                    print(f"  {i}. {commit_id}")
                    commit_id = commit_ids[-1]  # Seleccionar el último commit (más reciente)
                    print(f"Seleccionado automáticamente el commit más reciente: {commit_id}")
            else:
                commit_id = commit_ids[0]

            realizar_cherry_pick_y_validar(repo, commit_id, pr_id)
        except Exception as e:
            print(f"Error procesando la PR #{pr_id}: {e}")

        # Eliminar los archivos local_diff.txt, original_diff.txt y diferencias_reportadas.txt
        local_diff_file = os.path.join(REPO_PATH, "local_diff.txt")
        original_diff_file = os.path.join(REPO_PATH, "original_diff.txt")
        diferencias_reportadas_file = os.path.join(REPO_PATH, "diferencias_reportadas.txt")
        conflicts_file = os.path.join(REPO_PATH, "conflicts.txt")

        for diff_file in [local_diff_file, original_diff_file, diferencias_reportadas_file, conflicts_file]:
            if os.path.exists(diff_file):
                os.remove(diff_file)
      
        print(f"\033[34mFinalizada la PR #{pr_id}...\033[0m")
        print("\033[33mRecuerda copiar de las RN la tabla verde + sus pasos manuales. Revisa también la hoja de ProcessBuilder_Flow.\033[0m")
        print("\033[33mCambia el estado de la solicitud en el teams IBD si no quedan más PR\033[0m")
        input("Presiona ENTER para proceder con la siguiente PR tras hacer commit.")
    ejecutar_pre_push()
    hacer_push_y_abrir_pr(repo)

if __name__ == "__main__":
    main()