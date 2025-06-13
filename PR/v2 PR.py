import os
import subprocess
from git import Repo
from urllib.parse import unquote
from colorama import Fore, Style, init
import codecs
#pip install GitPython; pip install colorama; pip install chardet

init(autoreset=True)
# Ruta al repositorio donde se harán los cherry-picks
REPO_PATH = "C:\\Users\\Alejandro\\Downloads\\iberdrola-sfdx"  # ajustar

# Lista de Pull Requests a aplicar
PULL_REQUESTS = sorted([9698, 9775, 10133, 10274, 10382, 10467, 10525, 10602])
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


def resolver_conflictos_list_usando_mergefile():
    conflicted_files = run_command("git diff --name-only --diff-filter=U").splitlines()
    for file_path in conflicted_files:
        
        import urllib.parse

        if file_path.endswith(".profile-meta.xml") or file_path.endswith(".permissionset-meta.xml") or file_path.endswith(".app-meta.xml"):
            try:
                quoted_path = f":2:{file_path}".replace("\\", "/").replace('"', r'\"')
                current_content = run_command(f'git show "{quoted_path}"')

                if current_content is None:
                    raise ValueError("No se pudo obtener el contenido de current")

                with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(current_content)

                run_command(f'git add "{file_path}"')
                print(f"\033[93m🛠️ Resuelto con current (requiere revisión manual): {file_path}\033[0m")
            except Exception as e:
                print(f"❌ Error al resolver {file_path} con current: {e}")
            continue


        if file_path.endswith(".validationRule-meta.xml"):
            try:
                incoming_content = run_command_binary(f"git show :3:{file_path}")
                with open(file_path, 'wb') as f:
                    f.write(incoming_content)
                run_command(f'git add "{file_path}"')
                print(f"\033[94m✅ Resuelto con incoming: {file_path}\033[0m")
            except Exception as e:
                print(f"❌ Error al resolver {file_path} con incoming: {e}")
            continue

        if file_path.endswith(".md-meta.xml") and "force" in file_path:
            try:
                incoming_content = run_command_binary(f"git show :3:{file_path}")
                with open(file_path, 'wb') as f:
                    f.write(incoming_content)
                run_command(f'git add "{file_path}"')
                print(f"\033[94m✅ Resuelto con incoming: {file_path}\033[0m")
            except Exception as e:
                print(f"❌ Error al resolver {file_path} con incoming: {e}")
            continue

        if file_path.endswith(".flow-meta.xml"):
            try:
                incoming_content = run_command_binary(f"git show :3:{file_path}")
                with open(file_path, 'wb') as f:
                    f.write(incoming_content)
                run_command(f'git add "{file_path}"')
                print(f"\033[94m✅ Resuelto con incoming: {file_path}\033[0m")

            except Exception as e:
                print(f"❌ Error al resolver {file_path} con incoming: {e}")
            continue
        
        if file_path.endswith(".field-meta.xml"):
            try:
                incoming_content = run_command_binary(f"git show :3:{file_path}")
                with open(file_path, 'wb') as f:
                    f.write(incoming_content)
                run_command(f'git add "{file_path}"')
                print(f"\033[94m✅ Resuelto con incoming: {file_path}\033[0m")

            except Exception as e:
                print(f"❌ Error al resolver {file_path} con incoming: {e}")
            continue

        if not (
            file_path.endswith(".list") or 
            file_path.endswith(".globalValueSet-meta.xml") or 
            file_path.endswith(".flexipage-meta.xml") or
            file_path.endswith(".asset-meta.xml") or
            file_path.endswith(".layout-meta.xml") or
            file_path.endswith(".listView-meta.xml") or
            file_path.endswith(".businessProcess-meta.xml") or
            file_path.endswith(".compactLayout-meta.xml") or
            file_path.endswith(".audience-meta.xml") or
            file_path.endswith(".translation-meta.xml") or
            file_path.endswith(".recordType-meta.xml")
        ):
            continue

        
        base_path = f"{file_path}.base"
        current_path = f"{file_path}.current"
        incoming_path = f"{file_path}.incoming"
        
        try:
            try:
                base_content = run_command(f"git show :1:{file_path}", ignore_errors=True)
            except Exception:
                base_content = ''  # ⚠️ Si no existe en stage 1, asumimos vacío

            with open(base_path, 'w', encoding='utf-8') as f:
                f.write(git_show_stage(1, file_path))

            with open(current_path, 'w', encoding='utf-8') as f:
                f.write(git_show_stage(2, file_path))

            with open(incoming_path, 'w', encoding='utf-8') as f:
                f.write(git_show_stage(3, file_path))


            merged_content = run_command(
                f'git merge-file -p "{current_path}" "{base_path}" "{incoming_path}"',
                ignore_errors=True
            )


            if any(marker in merged_content for marker in ("<<<<<<<", "=======", ">>>>>>>")):
                merged_content = limpiar_conflictos_both(merged_content)

            if any(marker in merged_content for marker in ("<<<<<<<", "=======", ">>>>>>>")):
                print(f"🛑 {file_path} aún tiene conflictos complejos. Revisión manual necesaria.")
                continue

            with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(merged_content)

            run_command(f'git add "{file_path}"')
            print(f"\033[92m✅ Resuelto como Accept Both: {file_path}\033[0m")
        except Exception as e:
            print(f"❌ Error al resolver {file_path}: {e}")
        finally:
            for temp in [base_path, current_path, incoming_path]:
                if os.path.exists(temp):
                    os.remove(temp)

def aplicar_cherry_pick(repo, commit_id, pr_id):
    print(f"\n🔹 Aplicando cherry-pick de PR #{pr_id} (commit {commit_id})...")
    try:
        run_command(f"git cherry-pick -x --no-commit -m 1 {commit_id}")
        run_command("git commit --no-verify --no-edit")
        run_command("git reset --hard")
    except Exception as e:
        print(f"❌ Cherry-pick con conflictos. {e}")
        resolver_conflictos_list_usando_mergefile()
        print(f"URL: https://bitbucket.org/iberdrola-clientes/iberdrola-sfdx/pull-requests/{pr_id}/diff")
        input(f"PR actual: #{pr_id} {Fore.BLUE}🔹 Presiona ENTER para hacer commit y continuar con el siguiente cherry-pick...{Style.RESET_ALL}")
        run_command("git commit --no-verify --no-edit")
        run_command("git reset --hard")

def ejecutar_cherry_picks():
    run_command("git fetch --all")
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