#1 - ajustar rutas de archivos
#2- invocar python desde la carpeta del proyecto con python
#3- ajustar órden SF para atacar entorno correcto 

import os
import subprocess
import webbrowser
import re
from git import Repo
import time
import unicodedata
from colorama import Fore, Style, init
init(autoreset=True)

setDelta = False

PULL_REQUESTS = [
]  # Lista de IDs de las Pull Requests.

REPO_PATH = "C:\\Users\\Alejandro\\Downloads\\ibd\\iberdrola-sfdx"  # ajustar
#git clone --branch release/UAT2_20250317 --single-branch https://alejandroberdun1@bitbucket.org/iberdrola-clientes/iberdrola-sfdx.git; git remote set-branches origin '*';git fetch --all
#REPO_PATH = "C:\\Users\\Alejandro\\Downloads\\uat2\\iberdrola-sfdx"
profile_path = "C:\\Users\\Alejandro\\Downloads\\ibd\\iberdrola-sfdx\\force-app\\main\\default\\profiles"
permission_set_path = "C:\\Users\\Alejandro\\Downloads\\ibd\\iberdrola-sfdx\\force-app\\main\\default\\permissionsets"
errors_log_path = r'C:\\Users\\Alejandro\\Downloads\\rm\\Metadata Management\\Errors\\errors_list.txt'

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
    'field_specific': r'node "C:\\Users\\Alejandro\\Downloads\\rm\\Metadata Management\\Errors\\deleteFieldSpecificPermissions.mjs" "{profile_path}" "{object_name}" "{field_name}"',
    'record_type': r'node "C:\\Users\\Alejandro\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileRecordTypepermissionsReferences.mjs" "{profile_path}" "{record_type_name}"',
    'object': r'node "C:\\Users\\Alejandro\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileObjectpermissionsReferences.mjs" "{profile_path}" "{object_name}"',
    'class': r'node "C:\\Users\\Alejandro\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileClasspermissionsReferencesByObjectOrField.mjs" "{profile_path}" "{class_name}"',
    'apex_page': r'node "C:\\Users\\Alejandro\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileApexPagepermissionsReferencesByObjectOrField.mjs" "{profile_path}" "{apex_page_name}"',
    'flow_access': r'node "C:\\Users\\Alejandro\Downloads\\rm\\Metadata Management\\Errors\deleteProfileFlowaccessesReferencesByFlow.mjs" "{profile_path}" "{flow_access_name}',
    'layout': r'node "C:\\Users\\Alejandro\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileLayoutAssignmentsReferences.mjs" "{profile_path}" "{layout_name}"',
    'tab_visibility': r'node "C:\\Users\\Alejandro\\Downloads\\rm\\Metadata Management\\Errors\\deletePermissionSetProfileTabVisibilitiesReferences.mjs" "{profile_path}" "{tab_name}"',
    'custom_metadata_access': r'node "C:\\Users\\Alejandro\\Downloads\\rm\\Metadata Management\\Errors\\deleteCustomMetadataAccesses.mjs" "{profile_path}" "{metadata_name}"',
    'custom_permission': r'node "C:\\Users\\Alejandro\\Downloads\\rm\\Metadata Management\\Errors\\deleteCustomPermissions.mjs" "{profile_path}" "{custom_permission_name}"',
    'user_permission': r'node "C:\\Users\\Alejandro\\Downloads\\rm\\Metadata Management\\Errors\\deleteUserPermissions.mjs" "{profile_path}" "{user_permission_name}"',
    'mdt_fields': r'node "C:\\Users\\Alejandro\\Downloads\\rm\\Metadata Management\\Errors\\deleteMDTFieldPermissions.mjs" "{profile_path}" "{object_name}"',
    'mdt_layouts': r'node "C:\\Users\\Alejandro\\Downloads\\rm\\Metadata Management\\Errors\\deleteMDTLayoutAssignments.mjs" "{profile_path}" "{object_name}"',
    'fix_field_permissions': r'node "C:\\Users\\Alejandro\\Downloads\\rm\\Metadata Management\\Errors\\fixFieldPermissions.mjs" "{profile_path}"'
}

error_patterns = {
        'field_specific': r'In field: field - no CustomField named\s+([^.]+)\.([\w\d_]+)\s+found',
        'record_type': r'In field:\s+recordType\s+-\s+no RecordType named\s+([\w\d_.-]+)\s+found',
        'object': r'In field:\s+field\s+-\s+no CustomObject named\s+([\w\d_.-]+)\s+found',
        'class': r'In field:\s+apexClass\s+-\s+no ApexClass named\s+([\w\d_.-]+)\s+found',
        'apex_page': r'In field:\s+apexPage\s+-\s+no ApexPage named\s+([\w\d_.-]+)\s+found',
        'flow_access': r'In field:\s+flow\s+-\s+no FlowDefinition named\s+([\w\d_.-]+)\s+found',
        'layout': r'In field:\s+layout\s+-\s+no Layout named\s+([\w\d_.-]+(?:\s+[\w\d_.-]+)*)\s+found',
        'user_permission': r'Unknown user permission:\s+([\w\d_.-]+)',
        'tab_visibility': r'In field:\s+tab\s+-\s+no CustomTab named\s+([\w\d_.-]+)\s+found',
        'custom_metadata_access': r'In field:\s+customMetadataType\s+-\s+no CustomObject named\s+([\w\d_.-]+)\s+found',
        'custom_permission': r'In field: customPermission - no CustomPermission named\s+([\w\d_.-]+)\s+found',
        'fix_field_permissions': r'A field has to be readable to be editable'
    }

def extract_errors(output):
    """Extrae los errores del despliegue y los devuelve en un diccionario."""
    if not output:
        print("⚠ Advertencia: No se recibió salida del despliegue.")
        return {}

    error_patterns = {
        'field_specific': r'(In field: field - no CustomField named\s+([^.]+)\.([\w\d_]+)\s+found)',
        'record_type': r'(In field:\s+recordType\s+-\s+no RecordType named\s+([\w\d_.-]+)\s+found)',
        'object': r'(In field:\s+field\s+-\s+no CustomObject named\s+([\w\d_.-]+)\s+found)',
        'class': r'(In field:\s+apexClass\s+-\s+no ApexClass named\s+([\w\d_.-]+)\s+found)',
        'apex_page': r'(In field:\s+apexPage\s+-\s+no ApexPage named\s+([\w\d_.-]+)\s+found)',
        'flow_access': r'(In field:\s+flow\s+-\s+no FlowDefinition named\s+([\w\d_.-]+)\s+found)',
        'layout': r'(In field:\s+layout\s+-\s+no Layout named\s+([\w\d_.-]+(?:\s+[\w\d_.-]+)*)\s+found)',
        'user_permission': r'(Unknown user permission:\s+([\w\d_.-]+))',
        'tab_visibility': r'(In field:\s+tab\s+-\s+no CustomTab named\s+([\w\d_.-]+)\s+found)',
        'custom_metadata_access': r'(In field:\s+customMetadataType\s+-\s+no CustomObject named\s+([\w\d_.-]+)\s+found)',
        'custom_permission': r'(In field: customPermission - no CustomPermission named\s+([\w\d_.-]+)\s+found)',
        'fix_field_permissions': r'(A field has to be readable to be editable)'
    }

    errors = {}
    for key, pattern in error_patterns.items():
        matches = re.findall(pattern, output)
        for match in matches:
            error_text = match[0]  # 🔹 Guardamos el error completo
            if key not in errors:
                errors[key] = set()
            errors[key].add(error_text)  # 🔹 Guardamos la línea completa en lugar de solo la parte extraída

    return errors

    """ Extrae solo los errores relevantes de la salida del despliegue. """
    if not output:
        print("⚠ Advertencia: No se recibió salida del despliegue.")
        return {}

    errors = {key: set() for key in error_patterns.keys()}

    for line in output.split("\n"):  # Recorremos línea por línea la salida del despliegue
        for key, pattern in error_patterns.items():
            match = re.search(pattern, line)
            if match:
                if key == 'field_specific':
                    if len(match.groups()) == 2:
                        errors[key].add((match.group(1), match.group(2)))  # Guardar como tupla (Objeto, Campo)
                    else:
                        print(f"⚠ Advertencia: Formato inesperado en field_specific -> {line}")
                else:
                    errors[key].add(match.group(1) if match.groups() else line.strip())

    return errors

def run_command(command, cwd=None, ignore_errors=False):
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, shell=True, encoding="utf-8")
    
    if result.returncode != 0:
        if ignore_errors:
            return result.stdout.strip()  # Devuelve la salida, incluso con error
        else:
            print(f"Error ejecutando {command}:\n{result.stderr}")
            return result.stdout.strip()  # ⬅️ Cambiado para devolver la salida en lugar de lanzar excepción
    
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


def save_errors_to_file(errors, file_path):
    """ Guarda los errores en un archivo de texto sin borrar los anteriores. """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            for key, error_list in errors.items():
                for error in error_list:
                    f.write(f"{key}: {error}\n")  # 🔹 Guardamos el tipo de error y su valor
        print("✅ Errores guardados en el archivo de logs correctamente.")
    except Exception as e:
        print(f"⚠ Error guardando los errores en archivo: {e}")


def load_previous_errors(file_path):
    """Carga los errores previos desde un archivo de texto."""
    errors = {key: set() for key in error_patterns.keys()}  # Inicializa los errores como un diccionario vacío
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue  # Evitar líneas vacías
                    
                    parts = line.split(": ", 1)  # Separa la clave del mensaje
                    if len(parts) != 2:
                        print(f"⚠ Formato inesperado en archivo de errores: {line}")
                        continue
                    
                    key, value = parts
                    if key in errors:
                        # Si es field_specific, intentamos convertirlo en una tupla
                        match = re.search(r'In field: field - no CustomField named\s+([^.]+)\.([\w\d_]+)\s+found', value)
                        if match and key == "field_specific":
                            errors[key].add((match.group(1), match.group(2)))
                        else:
                            errors[key].add(value)
        except Exception as e:
            print(f"⚠ Error cargando los errores previos: {e}")

    return errors


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

        return True

    except Exception as e:
        print(f"Error resolviendo conflictos en {archivo}: {e}")
        return False

def normalize_text(text):
    return unicodedata.normalize("NFC", text)

        
def process_deploymentPROD():
    
    deploy_command = "sf project deploy start --target-org mobility --manifest deploy-manifest/package/package.xml --post-destructive-changes deploy-manifest/destructiveChanges/destructiveChanges.xml --dry-run --wait 240 --ignore-warnings --concise --ignore-conflicts"

    fields_found = True
    deployment_attempts = 0

    # Cargar errores previos una sola vez
    previous_errors_output = load_previous_errors(errors_log_path)
    errors_processed = False  # Asegura que los errores previos solo se usen una vez

    while fields_found:
        deployment_attempts += 1
        print(f'Starting deployment... (Attempt {deployment_attempts})')

        output = run_command(deploy_command)
        print('🔹 Deployment output:', output)

        extracted_errors = extract_errors(output) or {}  # Aseguramos que no sea None
        print('🔹 Extracted errors:', extracted_errors)

        # 🔹 Unimos errores previos y nuevos para asegurarnos de no perder ninguno
        errors = {}

        for key in error_patterns.keys():
            prev_errors = previous_errors_output.get(key, set()) if isinstance(previous_errors_output, dict) else set()
            new_errors = extracted_errors.get(key, set())

            cleaned_errors = set()
            for error in new_errors:
                match = re.search(error_patterns[key], error)
                if match:
                    if key == 'field_specific':
                        cleaned_errors.add((match.group(1), match.group(2)))
                    else:
                        cleaned_errors.add(match.group(1))

            errors[key] = prev_errors.union(cleaned_errors)


        save_errors_to_file(errors, errors_log_path)  # Guardamos los errores combinados
        print('✅ Errores final combinados:', errors)  # Confirmación de los errores que se están guardando

        action_taken = False
        for key, items in errors.items():
            for item in items:
                print(f'Extracted {key}:', item)

                for path in [profile_path, permission_set_path]:
                    if key == 'field_specific':
                        # 🔹 Asegurar que item es una tupla
                        if isinstance(item, tuple):
                            object_name, field_name = item
                        else:
                            print(f"⚠ Formato inesperado en field_specific: {item}, ignorando...")
                            continue  # Evitamos errores y pasamos a la siguiente iteración

                        delete_script = delete_script_templates['field_specific'].format(
                            profile_path=path, object_name=object_name, field_name=field_name
                        )

                    elif key == 'object' and item.endswith('__mdt'):
                        delete_script = delete_script_templates['mdt_fields'].format(profile_path=path, object_name=item)
                        run_command(delete_script)
                        delete_script = delete_script_templates['mdt_layouts'].format(profile_path=path, object_name=item)

                    elif key == 'custom_metadata_access':
                        delete_script = delete_script_templates[key].format(profile_path=path, metadata_name=item)

                    elif key == 'tab_visibility':
                        delete_script = delete_script_templates[key].format(profile_path=path, tab_name=item)

                    elif key == 'fix_field_permissions':
                        delete_script = delete_script_templates[key].format(profile_path=path)

                    else:
                        delete_script = delete_script_templates[key].format(profile_path=path, **{f'{key}_name': item})

                    print(f'Running delete script for {key} at {path}...')
                    delete_output = run_command(delete_script)
                    print('Delete script output:', delete_output)


                action_taken = True


        if not action_taken:
            print('No further action required.')
            print('\a')  # Beep sound
            fields_found = False


def ejecutar_pre_push():
    #custom_labels_path = "force-app\\main\\default\\labels\\CustomLabels.labels-meta.xml"
    #run_command(f'node C:\\Users\\Alejandro\\Downloads\\rm\\Metadata Management\\Errors\\removeDuplicateLabels.mjs "{custom_labels_path}"')


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

        # Detectar entorno basado en la rama
        if setDelta:
            print("\nGenerando delta...")
            comandos = [
            "git fetch --all",
            "sf sgd source delta --from $(git log --merges -n 1 --format='%H' origin/ci/mobility) --output-dir deploy-manifest --ignore-file .deltaignore --ignore-whitespace --source-dir force-app"
        ]
        
        process_deploymentPROD()
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
            raise Exception(f"\033[31mEl archivo {output_file} no se generó o está vacío.\033[0m")

    except Exception as e:
        print(f"\033[31mError exportando diferencias: {e}\033[0m")
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
                # Guardar diferencias en el archivo de reporte, excluyendo las líneas de EXCLUDE_LINES
                with open(output_file, "w", encoding="utf-8") as report_file:
                    report_file.writelines(filtered_differences)

                print(f"\n{Fore.YELLOW}Reporte de discrepancias exportado a: {output_file}{Style.RESET_ALL}")
                return False
            else:
                return True
    except Exception as e:
        print(f"Error comparando archivos: {e}")
        return False

def realizar_cherry_pick_y_validar(repo, commit_id, pr_id):
    try:
        command = f'git cherry-pick -x --no-commit -m 1 {commit_id}'
        run_command(command, cwd=REPO_PATH, ignore_errors=True)

        archivo_conflicto = os.path.join(REPO_PATH, "config/tests-to-run.list")
        # Resolver automáticamente conflictos en `config/tests-to-run.list`
        if os.path.exists(archivo_conflicto):
            if resolver_conflictos_tests_to_run(archivo_conflicto):
                run_command(f"git add {archivo_conflicto}", cwd=REPO_PATH)

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
            if compare_diff_files_with_context(original_diff_file, local_diff_file):
                print("\033[32m\nNo se encontraron discrepancias.\033[0m")
                print("Realizando commit...")
                command = f'git commit --no-verify --no-edit'
                run_command(command, cwd=REPO_PATH, ignore_errors=True)
                print("Realizando git reset --hard...")
                command = f'git reset --hard'
                run_command(command, cwd=REPO_PATH, ignore_errors=True)
                break

            if verificar_cambios_integrados(original_diff_file, local_diff_file, REPO_PATH, output_file="diferencias_reportadas.txt"):
                print("\033[32mLos cambios parecen estar integrados correctamente.\033[0m")
                print("Realizando commit...")
                command = f'git commit --no-verify --no-edit'
                run_command(command, cwd=REPO_PATH, ignore_errors=True)
                print("Realizando git reset --hard...")
                command = f'git reset --hard'
                run_command(command, cwd=REPO_PATH, ignore_errors=True)
                break

            respuesta = input("¿Deseas intentar resolver las discrepancias nuevamente? (s/n): ").lower()
            if respuesta != "s":
                # Nueva pregunta: ¿Quieres hacer commit de todas formas?
                commit_confirm = input("¿Deseas realizar el commit con los cambios? (s/n): ").lower()
                if commit_confirm == "s":
                    # ✅ Intentamos obtener el mensaje del commit original
                    commit_message = run_command(f"git log -1 --format=%B {commit_id}", cwd=REPO_PATH).strip()

                    # ✅ Si no hay mensaje, usamos el PR_ID con `#` delante
                    if not commit_message:
                        commit_message = f"#{pr_id}"
                        print(f"\033[33mNo se encontró mensaje en el commit original. Usando {commit_message} como mensaje de commit.\033[0m")

                    # ✅ Verificamos si hay cambios en staged antes de hacer commit
                    staged_changes = run_command("git diff --cached --name-only", cwd=REPO_PATH)
                    if not staged_changes.strip():
                        print("\033[33mNo hay cambios en staged. No se necesita commit.\033[0m")
                        break
                    print("Realizando commit...")
                    commit_command = f'git commit --no-verify -m "{commit_message}"'
                    run_command(commit_command, cwd=REPO_PATH, ignore_errors=True)
                    print("Realizando git reset --hard...")
                    command = f'git reset --hard'
                    run_command(command, cwd=REPO_PATH, ignore_errors=True)
                    break
                else:
                    raise Exception("Discrepancias no resueltas y commit cancelado.")

    except Exception as e:
        print(f"Error durante el cherry-pick y validación: {e}")
        print("Realizando git reset --hard...")
        command = f'git reset --hard'
        run_command(command, cwd=REPO_PATH, ignore_errors=True)


def verificar_cambios_integrados(pull_request_file, local_diff_file, repo_path, output_file="discrepancias_detectadas.txt"):
    try:
        # Leer los archivos de diferencias
        with open(pull_request_file, "r", encoding="utf-8") as pr_file:
            pr_lines = pr_file.readlines()

        with open(local_diff_file, "r", encoding="utf-8") as local_file:
            local_lines = local_file.readlines()

        # Diccionarios para almacenar diferencias por archivo
        discrepancies_by_file = {}
        local_removed = {}

        current_file = None

        # Extraer líneas eliminadas en la PR
        for line in pr_lines:
            if line.startswith("diff --git"):
                current_file = line.split(" b/")[-1].strip()
                discrepancies_by_file[current_file] = {"removed": set()}
            elif current_file:
                if line.startswith("-") and not line.startswith("---"):
                    discrepancies_by_file[current_file]["removed"].add(line[1:].strip())

        # Extraer líneas eliminadas en el cherry-pick
        current_file = None
        for line in local_lines:
            if line.startswith("diff --git"):
                current_file = line.split(" b/")[-1].strip()
                if current_file not in local_removed:
                    local_removed[current_file] = set()
            elif current_file:
                if line.startswith("-") and not line.startswith("---"):
                    local_removed[current_file].add(line[1:].strip())

        # Comparar diferencias por archivo
        discrepancies = []

        for file, changes in discrepancies_by_file.items():
            pr_removed = changes["removed"]
            local_removed_set = local_removed.get(file, set())

            # **Verificar si las líneas que no se eliminaron aún existen en el archivo**
            file_path = os.path.join(repo_path, file)
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read()
                
                missing_removed = {line for line in pr_removed if line in file_content}
                if missing_removed:
                    discrepancies.append("\n🚨 **Líneas que deberían haberse eliminado y no lo fueron:**")

                    for line in missing_removed:
                        file_path = os.path.join(repo_path, current_file)

                        if os.path.exists(file_path):
                            with open(file_path, "r", encoding="utf-8") as f:
                                file_contents = f.readlines()

                            # Contamos cuántas veces la línea aparece en el archivo después del cherry-pick
                            count_in_file = sum(1 for l in file_contents if line.strip() in l.strip())

                            # Contamos cuántas veces la línea estaba en la PR marcada para eliminarse
                            count_removed_in_pr = sum(1 for l in pr_removed if line.strip() in l.strip())

                            if count_removed_in_pr > 0:
                                if count_in_file >= count_removed_in_pr:
                                    # No se eliminaron todas las ocurrencias necesarias
                                    discrepancies.append(f"  - {line}")
                        else:
                            # Si el archivo no existe, asumimos que se eliminó correctamente
                            discrepancies.append(f"  - {line} (Archivo eliminado, posible eliminación correcta)")


        # Guardar el reporte de discrepancias
        if discrepancies:
            with open(output_file, "w", encoding="utf-8") as report_file:
                report_file.writelines("\n".join(discrepancies))
            return False  # Indica que hay discrepancias
        else:
            print("✅ Todas las eliminaciones esperadas se realizaron correctamente.")
            return True  # Todo está correcto

    except Exception as e:
        print(f"❌ Error verificando los cambios: {e}")
        return False


def eliminar_lineas_duplicadas(archivo):
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            lineas = f.readlines()
        
        lineas_unicas = list(dict.fromkeys(lineas))
        
        with open(archivo, "w", encoding="utf-8") as f:
            f.writelines(lineas_unicas)
    
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
                for i, commit_id in enumerate(commit_ids, 1):
                    commit_id = commit_ids[-1]  # Seleccionar el último commit (más reciente)
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