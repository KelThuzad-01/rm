import os
import subprocess
from git import Repo
from urllib.parse import unquote
from colorama import Fore, Style, init
import codecs
#pip install GitPython; pip install colorama; pip install chardet

init(autoreset=True)
# Ruta al repositorio donde se harán los cherry-picks
REPO_PATH = "C:\\Users\\Alejandro\\Downloads\\ibd\\iberdrola-sfdx"  # ajustar

# Lista de Pull Requests a aplicar
PULL_REQUESTS = sorted([10894, 10251, 10262, 10907, 10919, 10879, 10902, 10888, 10866, 10988, 10885])
import subprocess

def run_command(command, cwd=REPO_PATH, ignore_errors=False, show_output=True, suppress_output=False):
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=cwd
        )

        if show_output and not suppress_output:
            # Solo imprime si la salida es razonablemente corta
            output = result.stdout.strip()
            if len(output) > 2500:
                print(f"")
            elif output:
                print(output)
            if result.stderr:
                print(result.stderr)

        return result.stdout

    except subprocess.CalledProcessError as e:
        if ignore_errors:
            return e.stdout or e.stderr or ''
        print(f"[ERROR] Error ejecutando {command}:\n{e.stderr or e.stdout}")
        raise


import unicodedata
from urllib.parse import quote

def git_show_stage(stage: int, file_path: str) -> str:
    # Escapa caracteres especiales y espacios
    encoded_path = quote(file_path.replace("\\", "/"))
    full_ref = f":{stage}:{encoded_path}"
    return run_command(f'git show "{full_ref}"', ignore_errors=True)

def run_command_binary(command, cwd=REPO_PATH):
    result = subprocess.run(command, shell=True, check=True, capture_output=True, cwd=cwd)
    return result.stdout

def obtener_commit_de_pr(pr_id):
    command = f'git log --all --grep="#{pr_id}" --format="%H"'
    result = run_command(command)
    commit_ids = result.splitlines() if result else []
    if not commit_ids:
        print(f"{Fore.YELLOW}⚠ No se encontró un commit para la PR #{pr_id}. Ejecuta `git fetch` y vuelve a intentarlo.{Style.RESET_ALL}")
        return None
    return commit_ids[-1]

from colorama import Fore, Style

def fusionar_lineas_vscode_style(current_content, incoming_content):
    current_lines = current_content.splitlines()
    incoming_lines = incoming_content.splitlines()
    resultado = []
    i = j = 0

    while i < len(current_lines) or j < len(incoming_lines):
        # Si quedan líneas en ambos bloques
        if i < len(current_lines) and j < len(incoming_lines):
            if current_lines[i].strip() == incoming_lines[j].strip():
                resultado.append(current_lines[i])  # líneas iguales
                i += 1
                j += 1
            elif current_lines[i].strip() in incoming_lines[j:]:
                resultado.append(incoming_lines[j])
                j += 1
            elif incoming_lines[j].strip() in current_lines[i:]:
                resultado.append(current_lines[i])
                i += 1
            else:
                # líneas distintas: añadimos ambas (VSCode style)
                resultado.append(current_lines[i])
                resultado.append(incoming_lines[j])
                i += 1
                j += 1
        elif i < len(current_lines):
            resultado.append(current_lines[i])
            i += 1
        elif j < len(incoming_lines):
            resultado.append(incoming_lines[j])
            j += 1

    return '\n'.join(resultado) + '\n'


def limpiar_conflictos_both(content):
    lines = content.splitlines(keepends=True)
    new_lines = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("<<<<<<<"):
            current_block = []
            incoming_block = []
            i += 1
            while i < len(lines) and not lines[i].startswith("======="):
                current_block.append(lines[i])
                i += 1
            i += 1  # skip =======
            while i < len(lines) and not lines[i].startswith(">>>>>>>"):
                incoming_block.append(lines[i])
                i += 1
            i += 1  # skip >>>>>>>
            # 🔥 Siempre combinamos: current + incoming
            new_lines.extend(current_block + incoming_block)
        else:
            new_lines.append(lines[i])
            i += 1
    return "".join(new_lines)

def combinar_conflictos_accept_both(content):
    """
    Sustituye los bloques de conflicto por la combinación secuencial de CURRENT e INCOMING,
    dejando el resto del archivo intacto. Evita duplicados consecutivos.
    """
    result = []
    i = 0
    while i < len(content):
        if content[i].startswith("<<<<<<<"):
            # Saltar línea de inicio del conflicto
            i += 1
            bloque_current = []
            while i < len(content) and not content[i].startswith("======="):
                bloque_current.append(content[i])
                i += 1

            if i >= len(content) or not content[i].startswith("======="):
                raise ValueError("Bloque de conflicto mal formado (falta '=======')")

            i += 1
            bloque_incoming = []
            while i < len(content) and not content[i].startswith(">>>>>>>"):
                bloque_incoming.append(content[i])
                i += 1

            if i >= len(content) or not content[i].startswith(">>>>>>>"):
                raise ValueError("Bloque de conflicto mal formado (falta '>>>>>>>')")

            i += 1  # Saltar línea de cierre del conflicto

            # Combinar los bloques evitando duplicados adyacentes
            combinado = []
            for linea in bloque_current + bloque_incoming:
                if not combinado or linea != combinado[-1]:
                    combinado.append(linea)

            result.extend(combinado)
        else:
            result.append(content[i])
            i += 1
    return result


def combinar_conflictos_both(file_path):

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    resultado = []
    i = 0
    while i < len(lines):
        if lines[i].startswith('<<<<<<<'):
            current = []
            incoming = []
            i += 1
            while i < len(lines) and not lines[i].startswith('======='):
                current.append(lines[i])
                i += 1
            i += 1  # saltar =======
            while i < len(lines) and not lines[i].startswith('>>>>>>>'):
                incoming.append(lines[i])
                i += 1
            i += 1  # saltar >>>>>>>
            resultado.extend(current + incoming)
        else:
            resultado.append(lines[i])
            i += 1

    with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
        f.writelines(resultado)

import re

def combinar_bloques_conflicto_vscode(texto_conflictivo):
    """
    Reemplaza todos los bloques de conflicto en un archivo con la combinación de ambos (current + incoming),
    como hace Visual Studio Code con 'Accept Both Changes'.
    """
    resultado = []
    en_conflicto = False
    bloque_current = []
    bloque_incoming = []
    modo = None

    for linea in texto_conflictivo.splitlines():
        if linea.startswith("<<<<<<<"):
            en_conflicto = True
            bloque_current = []
            bloque_incoming = []
            modo = "current"
            continue
        elif linea.startswith("=======") and en_conflicto:
            modo = "incoming"
            continue
        elif linea.startswith(">>>>>>>") and en_conflicto:
            # Añadir ambos bloques y cerrar conflicto
            resultado.extend(bloque_current)
            resultado.extend(bloque_incoming)
            en_conflicto = False
            modo = None
            continue

        if en_conflicto:
            if modo == "current":
                bloque_current.append(linea)
            elif modo == "incoming":
                bloque_incoming.append(linea)
        else:
            resultado.append(linea)

    return "\n".join(resultado) + "\n"


import urllib.parse
import os

import urllib.parse

import urllib.parse

import os
import subprocess
import urllib.parse

def resolver_conflictos_list_usando_mergefile(pr_id):
    import subprocess
    import urllib.parse
    import os

    def combinar_conflictos_accept_both(content):
        result = []
        i = 0
        while i < len(content):
            if content[i].startswith("<<<<<<<"):
                i += 1
                bloque_current = []
                while i < len(content) and not content[i].startswith("======="):
                    bloque_current.append(content[i])
                    i += 1
                if i >= len(content) or not content[i].startswith("======="):
                    raise ValueError("Bloque mal formado: falta '======='")
                i += 1
                bloque_incoming = []
                while i < len(content) and not content[i].startswith(">>>>>>>"):
                    bloque_incoming.append(content[i])
                    i += 1
                if i >= len(content) or not content[i].startswith(">>>>>>>"):
                    raise ValueError("Bloque mal formado: falta '>>>>>>>")
                i += 1
                combinado = []
                for linea in bloque_current + bloque_incoming:
                    if not combinado or linea != combinado[-1]:
                        combinado.append(linea)
                result.extend(combinado)
            else:
                result.append(content[i])
                i += 1
        return result

    output = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"], stdout=subprocess.PIPE, text=True).stdout
    conflicted_files = output.strip().split("\n")
    conflicted_files = [f for f in conflicted_files if f.strip()]
    resumen = []

    for original_path in conflicted_files:


        decoded_path = urllib.parse.unquote(original_path)

        if not os.path.exists(decoded_path):
            continue

        base_path = decoded_path + ".base"
        current_path = decoded_path + ".current"
        incoming_path = decoded_path + ".incoming"

        try:
            with open(base_path, "wb") as f:
                f.write(subprocess.check_output(["git", "show", f":1:{original_path}"]))
            with open(current_path, "wb") as f:
                f.write(subprocess.check_output(["git", "show", f":2:{original_path}"]))
            with open(incoming_path, "wb") as f:
                f.write(subprocess.check_output(["git", "show", f":3:{original_path}"]))
        except subprocess.CalledProcessError as e:
            print(f"❌ Error extrayendo contenido base/current/incoming: {e}")
            continue


        try:
            resultado_merge = subprocess.run(
                ["merge-file", "-p", current_path, base_path, incoming_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            with open(decoded_path, "w", encoding="utf-8") as f:
                f.write(resultado_merge.stdout)

        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"⚠️ Conflicto no resuelto por merge-file en {decoded_path}, aplicando resolución alternativa...")

            try:
                if original_path.endswith((".flow-meta.xml", ".md-meta.xml", ".validationRule-meta.xml")):
                    print("📥 Resolviendo como 'Accept Incoming'")
                    with open(decoded_path, "wb") as f:
                        f.write(subprocess.check_output(["git", "show", f":3:{original_path}"]))
                else:
                    with open(decoded_path, "r", encoding="utf-8", errors="ignore") as f:
                        original_conflict_content = f.readlines()

                    nuevo_contenido = combinar_conflictos_accept_both(original_conflict_content)
                    print(f"💾 Guardando contenido combinado en {decoded_path}")
                    with open(decoded_path, "w", encoding="utf-8") as f:
                        f.writelines(nuevo_contenido)
            except Exception as e:
                print(f"❌ Error resolviendo conflicto: {e}")
                continue

        subprocess.run(["git", "add", decoded_path])

        # Limpieza
        for tmp_file in [base_path, current_path, incoming_path]:
            if os.path.exists(tmp_file):
                os.remove(tmp_file)

        resumen.append(f"   - {original_path}\nURL: https://bitbucket.org/iberdrola-clientes/iberdrola-sfdx/pull-requests/{pr_id}/diff#chg-{original_path}")

    if resumen:
        print(f"---------------------------------------")
        print(f"🟢 Archivos resueltos: {len(resumen)}")
        for item in resumen:
            print(item)
            print(f"---------------------------------------")

    import subprocess
    import urllib.parse
    import os

    def combinar_conflictos_accept_both(content):
        result = []
        i = 0
        while i < len(content):
            if content[i].startswith("<<<<<<<"):
                i += 1
                bloque_current = []
                while i < len(content) and not content[i].startswith("======="):
                    bloque_current.append(content[i])
                    i += 1

                if i >= len(content) or not content[i].startswith("======="):
                    raise ValueError("Bloque mal formado: falta '======='")

                i += 1
                bloque_incoming = []
                while i < len(content) and not content[i].startswith(">>>>>>>"):
                    bloque_incoming.append(content[i])
                    i += 1

                if i >= len(content) or not content[i].startswith(">>>>>>>"):
                    raise ValueError("Bloque mal formado: falta '>>>>>>>")

                i += 1
                combinado = []
                for linea in bloque_current + bloque_incoming:
                    if not combinado or linea != combinado[-1]:
                        combinado.append(linea)

                result.extend(combinado)
            else:
                result.append(content[i])
                i += 1
        return result


    output = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"], stdout=subprocess.PIPE, text=True).stdout
    conflicted_files = output.strip().split("\n")
    conflicted_files = [f for f in conflicted_files if f.strip()]
    resumen = []

    for original_path in conflicted_files:
       

        decoded_path = urllib.parse.unquote(original_path)

        if not os.path.exists(decoded_path):
            continue

        base_path = decoded_path + ".base"
        current_path = decoded_path + ".current"
        incoming_path = decoded_path + ".incoming"

        try:
            with open(base_path, "wb") as f:
                f.write(subprocess.check_output(["git", "show", f":1:{original_path}"]))
            with open(current_path, "wb") as f:
                f.write(subprocess.check_output(["git", "show", f":2:{original_path}"]))
            with open(incoming_path, "wb") as f:
                f.write(subprocess.check_output(["git", "show", f":3:{original_path}"]))
        except subprocess.CalledProcessError as e:
            print(f"❌ Error extrayendo contenido base/current/incoming: {e}")
            continue

        try:
            resultado_merge = subprocess.run(
                ["merge-file", "-p", current_path, base_path, incoming_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            with open(decoded_path, "w", encoding="utf-8") as f:
                f.write(resultado_merge.stdout)

        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"⚠️ Conflicto no resuelto por merge-file en {decoded_path}, aplicando combinación estilo VS Code...")

            try:
                with open(decoded_path, "r", encoding="utf-8", errors="ignore") as f:
                    original_conflict_content = f.readlines()

                nuevo_contenido = combinar_conflictos_accept_both(original_conflict_content)


                with open(decoded_path, "w", encoding="utf-8") as f:
                    f.writelines(nuevo_contenido)
            except Exception as e:
                print(f"❌ Error aplicando combinación estilo VS Code: {e}")
                continue

        subprocess.run(["git", "add", decoded_path])

        # Limpieza
        for tmp_file in [base_path, current_path, incoming_path]:
            if os.path.exists(tmp_file):
                os.remove(tmp_file)

        resumen.append(f"   - {original_path}\nURL: https://bitbucket.org/iberdrola-clientes/iberdrola-sfdx/pull-requests/{pr_id}/diff#chg-{original_path}")

    if resumen:
        print(f"\n📄 Resumen de resolución de conflictos:")
        print(f"🟢 Resueltos como Accept Both: {len(resumen)} archivos")
        for item in resumen:
            print(item)


def aplicar_cherry_pick(repo, commit_id, pr_id):
    print(f"\n🔹 Aplicando cherry-pick de PR #{pr_id} (commit {commit_id})...")
    try:
        run_command(f"git cherry-pick -x --no-commit -m 1 {commit_id}")
        run_command("git commit --no-verify --no-edit")
        run_command("git reset --hard")
    except Exception as e:
        print(f"❌ Cherry-pick con conflictos. {e}")
        resolver_conflictos_list_usando_mergefile(pr_id)
        input(f"PR actual: #{pr_id} {Fore.BLUE}🔹 Presiona ENTER para hacer commit y continuar con el siguiente cherry-pick...{Style.RESET_ALL}")
        run_command("git commit --no-verify --no-edit")
        run_command("git reset --hard")

def ejecutar_cherry_picks():
    run_command("git fetch")
    try:
        run_command("git pull")
    except Exception as e:
        print(f"{e}")

    repo = Repo(REPO_PATH)

    for pr_id in PULL_REQUESTS:
        commit_id = obtener_commit_de_pr(pr_id)
        if commit_id:
            aplicar_cherry_pick(repo, commit_id, pr_id)
        else:
            print(f"{Fore.YELLOW}⚠ Saltando PR #{pr_id} por falta de commit asociado.{Style.RESET_ALL}")

    print(f"\n{Fore.GREEN}🎯 Todos los cherry-picks han sido procesados.{Style.RESET_ALL}")

ejecutar_cherry_picks()