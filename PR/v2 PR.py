import os
import subprocess
from git import Repo
from urllib.parse import unquote
from colorama import Fore, Style, init

init(autoreset=True)  # Para usar colores en PowerShell

# Ruta al repositorio donde se harán los cherry-picks
REPO_PATH = "C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx"

# Lista de Pull Requests a aplicar (ordenada de menor a mayor)
PULL_REQUESTS = sorted([9756, 9763])  # Reemplazar con PRs reales

def run_command(command, cwd=REPO_PATH, ignore_errors=False):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, cwd=cwd)
        return result.stdout
    except subprocess.CalledProcessError as e:
        if ignore_errors:
            return e.stdout or e.stderr or ''
        print(f"{Fore.RED}Error ejecutando {command}: {e.stderr}{Style.RESET_ALL}")
        return None

def obtener_commit_de_pr(pr_id):
    command = f'git log --all --grep="#{pr_id}" --format="%H"'
    result = run_command(command)
    commit_ids = result.splitlines() if result else []
    if not commit_ids:
        print(f"{Fore.YELLOW}⚠ No se encontró un commit para la PR #{pr_id}. Ejecuta `git fetch` y vuelve a intentarlo.{Style.RESET_ALL}")
        return None
    return commit_ids[-1]

def verificar_diferencias(commit_id):
    run_command("git diff --cached > local_diff.txt")
    expected_diff = run_command(f"git show {commit_id} --pretty=format:'' --diff-filter=AM")

    local_diff_path = os.path.join(REPO_PATH, "local_diff.txt")
    if not os.path.exists(local_diff_path):
        print(f"{Fore.YELLOW}⚠ No se encontró el archivo local_diff.txt{Style.RESET_ALL}")
        return False

    with open(local_diff_path, "r", encoding="utf-8") as f:
        applied_diff = f.read()

    if applied_diff.strip() != (expected_diff or '').strip():
        print(f"{Fore.YELLOW}⚠ Diferencias inesperadas en el cherry-pick. Revisión manual requerida.{Style.RESET_ALL}")
        print(f"🔍 {Fore.CYAN}Diffs aplicados:{Style.RESET_ALL}\n", applied_diff[:1000])
        print(f"🔍 {Fore.CYAN}Diffs esperados:{Style.RESET_ALL}\n", expected_diff[:1000])
        return False
    return True

def identificar_conflictos():
    output = run_command("git status --porcelain")
    conflictos = []
    for line in output.splitlines():
        if line.startswith('UU'):
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                conflictos.append(parts[1].strip().strip('"'))
    return conflictos


def analizar_conflictos(conflict_files):
    conflicts_report = []
    conflicto_num = 1
    for file in conflict_files:
        file_path = os.path.normpath(os.path.join(REPO_PATH, file))
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            print(f"{Fore.RED}❌ Error abriendo archivo con conflicto: {file_path} → {e}{Style.RESET_ALL}")
            continue

        conflicts_report.append(f"\n📂 Archivo: {file}\n")

        conflicto = []
        dentro_conflicto = False
        current_block = []
        incoming_block = []
        leyendo_current = True

        for line in lines:
            if line.startswith("<<<<<<<"):
                conflicto.append(f"{Fore.MAGENTA}🔹 Conflicto {conflicto_num} en `{file}`:{Style.RESET_ALL}\n")
                conflicto.append(f"{Fore.YELLOW}🔻 Comienzo del conflicto{Style.RESET_ALL}")
                dentro_conflicto = True
                leyendo_current = True
                current_block = []
                incoming_block = []
            elif line.startswith("=======" ) and dentro_conflicto:
                conflicto.extend([f"   {l}" for l in current_block])
                conflicto.append(f"{Fore.CYAN}\n🟰 Separador entre versiones{Style.RESET_ALL}")
                leyendo_current = False
            elif line.startswith(">>>>>>>") and dentro_conflicto:
                conflicto.extend([f"   {l}" for l in incoming_block])
                conflicto.append(f"{Fore.GREEN}🔺 Fin del conflicto{Style.RESET_ALL}\n")

                if incoming_block and not current_block:
                    conflicto.append(f"{Fore.BLUE}✅ Acción recomendada: Aceptar Incoming (PR){Style.RESET_ALL}\n")
                elif current_block and not incoming_block:
                    conflicto.append(f"{Fore.BLUE}✅ Acción recomendada: Mantener Current (actual){Style.RESET_ALL}\n")
                elif current_block == incoming_block:
                    conflicto.append(f"{Fore.BLUE}✅ Acción recomendada: Ambas versiones son idénticas. Usa cualquiera.{Style.RESET_ALL}\n")
                elif all(line not in incoming_block for line in current_block):
                    conflicto.append(f"{Fore.CYAN}💡 Sugerencia: Ninguna línea actual aparece como eliminada en la PR. Recomendado combinar ambas versiones.{Style.RESET_ALL}")
                    conflicto.append(f"{Fore.BLUE}✅ Acción recomendada: Combinar cambios (mantener ambas líneas){Style.RESET_ALL}\n")
                else:
                    conflicto.append(f"{Fore.YELLOW}\n📄 Vista previa - Versión actual (HEAD):{Style.RESET_ALL}")
                    conflicto.extend([f"   {line}" for line in current_block])
                    conflicto.append(f"{Fore.GREEN}\n📄 Vista previa - Versión de la PR (Incoming):{Style.RESET_ALL}")
                    conflicto.extend([f"   {line}" for line in incoming_block])
                    conflicto.append(f"{Fore.CYAN}💡 Sugerencia: Analiza cuidadosamente qué líneas deseas mantener.{Style.RESET_ALL}")
                    conflicto.append(f"{Fore.BLUE}✅ Acción recomendada: Resolución manual requerida.{Style.RESET_ALL}\n")

                conflicts_report.extend(conflicto)
                conflicto = []
                dentro_conflicto = False
                conflicto_num += 1
            elif dentro_conflicto:
                stripped = line.rstrip("\n")
                if leyendo_current:
                    current_block.append(stripped)
                else:
                    incoming_block.append(stripped)

    path_out = os.path.join(REPO_PATH, "conflicts_resolution_guide.txt")
    with open(path_out, "w", encoding="utf-8") as f:
        f.write("\n".join(conflicts_report))

    print(f"{Fore.GREEN}✅ Recomendaciones de resolución guardadas en conflicts_resolution_guide.txt\n{Style.RESET_ALL}")
    print("\n".join(conflicts_report))

def aplicar_cherry_pick(repo, commit_id, pr_id):
    print(f"\n🔹 Aplicando cherry-pick de PR #{pr_id} (commit {commit_id})...")

    try:
        run_command(f"git cherry-pick -x --no-commit -m 1 {commit_id}")

        conflictos = identificar_conflictos()
        if conflictos:
            print(f"{Fore.YELLOW}⚠ Se detectaron conflictos en {len(conflictos)} archivo(s). Generando recomendaciones...{Style.RESET_ALL}")
            analizar_conflictos(conflictos)
        elif verificar_diferencias(commit_id):
            print(f"{Fore.GREEN}✅ Cherry-pick de PR #{pr_id} aplicado correctamente.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Error: PR #{pr_id} tiene diferencias inesperadas.{Style.RESET_ALL}")
            print("🛠 Por favor, resuelve los conflictos manualmente, haz 'git add .' y luego 'git commit'.")
            print("⚠ El cherry-pick no ha sido abortado para que puedas continuar con la resolución manual.")
    except Exception as e:
        print(f"{Fore.RED}❌ Error en cherry-pick de PR #{pr_id}: {e}{Style.RESET_ALL}")
        if not identificar_conflictos():
            run_command("git cherry-pick --abort")

    input(f"{Fore.BLUE}🔹 Presiona ENTER para continuar con el siguiente cherry-pick...{Style.RESET_ALL}")

def ejecutar_cherry_picks():
    print(f"\n{Fore.CYAN}📥 Actualizando el repositorio...{Style.RESET_ALL}")
    run_command("git fetch --all")
    run_command("git pull")

    repo = Repo(REPO_PATH)

    for pr_id in PULL_REQUESTS:
        commit_id = obtener_commit_de_pr(pr_id)
        if commit_id:
            aplicar_cherry_pick(repo, commit_id, pr_id)
        else:
            print(f"{Fore.YELLOW}⚠ Saltando PR #{pr_id} por falta de commit asociado.{Style.RESET_ALL}")

    print(f"\n{Fore.GREEN}🎯 Todos los cherry-picks han sido procesados.{Style.RESET_ALL}")

ejecutar_cherry_picks()
