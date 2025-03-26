import os
import subprocess
from git import Repo
from urllib.parse import unquote
from colorama import Fore, Style, init
import codecs

init(autoreset=True)  # Para usar colores en PowerShell

# Ruta al repositorio donde se harán los cherry-picks
REPO_PATH = "C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx"

# Lista de Pull Requests a aplicar (ordenada de menor a mayor)
PULL_REQUESTS = sorted([9201, 9818, 9761, 9811])  # Reemplazar con PRs reales

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

from colorama import Fore, Style

def generar_ayuda_manual_general(current_block, incoming_block, archivo, conflicto_num):
    ayuda = []

    ayuda.append(f"\n📂 Archivo: {archivo}")
    ayuda.append(f"\033[35m🔹 Conflicto {conflicto_num}:\033[0m\n")

    ayuda.append(f"\033[33m🔻 Código actual (HEAD):\033[0m")
    for line in current_block:
        ayuda.append(f"   {line}")

    ayuda.append(f"\n\033[36m🆚\033[0m\n")

    ayuda.append(f"\033[32m🔺 Código propuesto por la PR:\033[0m")
    for line in incoming_block:
        ayuda.append(f"   {line}")

    ayuda.append(f"\n\033[36m📌 Notas:\033[0m")
    ayuda.append(f"• El bloque actual y el bloque de la PR son significativamente diferentes.")
    ayuda.append(f"• No hay líneas marcadas como eliminadas en la PR que coincidan exactamente con las del bloque actual.")
    ayuda.append(f"• Es probable que la PR reemplace lógica existente por otra simplificada o alternativa.")

    ayuda.append(f"\n\033[36m🔧 Consejos para resolver:\033[0m")
    ayuda.append(f"✔ Asegúrate de no eliminar líneas que no han sido eliminadas en la PR.")
    ayuda.append(f"✔ Verifica si las líneas nuevas ya están presentes antes de añadirlas.")
    ayuda.append(f"✔ Si hay dudas, fusiona cuidadosamente ambas versiones o consulta al autor de la PR.")

    ayuda.append(f"{Fore.BLUE}✅ Acción recomendada: Resolución manual requerida.{Style.RESET_ALL}")

    return ayuda

def formatear_conflicto_manual(current_block, incoming_block, archivo=None, conflicto_num=None, verdes=None, rojas=None):
    conflicto = []

    conflicto.append(f"{Fore.YELLOW}🔻 Comienzo del conflicto (versión actual - HEAD){Style.RESET_ALL}")
    conflicto.extend([f"   {line}" for line in current_block])
    conflicto.append(f"{Fore.CYAN}\n🟰 Separador entre versiones{Style.RESET_ALL}")
    conflicto.append(f"{Fore.MAGENTA}\n🔼 Incoming (desde la Pull Request){Style.RESET_ALL}")
    conflicto.extend([f"   {line}" for line in incoming_block])
    conflicto.append(f"{Fore.GREEN}🔺 Fin del conflicto{Style.RESET_ALL}\n")

    # Añadimos mensaje y líneas verdes/rojas si las hay
    conflicto.append(f"{Fore.CYAN}💡 Sugerencia: La línea actual no coincide con la eliminada en la PR. Revisión detallada requerida.{Style.RESET_ALL}")
    conflicto.append(f"{Fore.BLUE}✅ Acción recomendada: Resolución manual requerida.{Style.RESET_ALL}")

    if verdes or rojas:
        if rojas:
            conflicto.append(f"{Fore.RED}🔻 Líneas eliminadas en la PR (rojas):{Style.RESET_ALL}")
            for l in rojas:
                conflicto.append(f"{Fore.RED}- {l.strip()}{Style.RESET_ALL}")
        if verdes:
            conflicto.append(f"{Fore.GREEN}🔺 Líneas añadidas en la PR (verdes):{Style.RESET_ALL}")
            for l in verdes:
                conflicto.append(f"{Fore.GREEN}+ {l.strip()}{Style.RESET_ALL}")

    return conflicto



def filtrar_conflictos_validos(conflictos):
    vistos = set()
    filtrados = []
    for c in conflictos:
        current = tuple(c.get("current", []))
        incoming = tuple(c.get("incoming", []))
        if not current and not incoming:
            continue
        clave = (current, incoming)
        if clave in vistos:
            continue
        vistos.add(clave)
        filtrados.append(c)
    return filtrados

def extraer_conflictos(lineas):
    conflictos = []
    actual = {"current": [], "incoming": []}
    leyendo = None
    for line in lineas:
        if "Comienzo del conflicto" in line:
            actual = {"current": [], "incoming": []}
            leyendo = "current"
        elif "Separador entre versiones" in line:
            leyendo = "incoming"
        elif "Fin del conflicto" in line:
            conflictos.append(actual)
            leyendo = None
        elif leyendo == "current":
            actual["current"].append(line.strip())
        elif leyendo == "incoming":
            actual["incoming"].append(line.strip())
    return conflictos

def renderizar_conflictos(conflictos):
    bloques = []
    for idx, c in enumerate(conflictos, 1):
        bloques.append(f"{Fore.MAGENTA}🔹 Conflicto {idx}:{Style.RESET_ALL}")
        bloques.append(f"{Fore.YELLOW}🔻 Comienzo del conflicto{Style.RESET_ALL}")
        for l in c["current"]:
            bloques.append(f"   {l}")
        bloques.append(f"{Fore.CYAN}\n🟰 Separador entre versiones{Style.RESET_ALL}")
        for l in c["incoming"]:
            bloques.append(f"   {l}")
        bloques.append(f"{Fore.GREEN}🔺 Fin del conflicto{Style.RESET_ALL}\n")
        if c["incoming"] and not c["current"]:
            bloques.append(f"{Fore.BLUE}✅ Acción recomendada: Aceptar Incoming (PR).{Style.RESET_ALL}\n")
        elif c["current"] and not c["incoming"]:
            bloques.append(f"{Fore.BLUE}✅ Acción recomendada: Mantener Current (rama actual).{Style.RESET_ALL}\n")
        else:
            bloques.append(f"{Fore.CYAN}💡 Sugerencia: Analiza cuidadosamente qué líneas deseas mantener.{Style.RESET_ALL}")
            bloques.append(f"{Fore.BLUE}✅ Acción recomendada: Resolución manual requerida.{Style.RESET_ALL}\n")
    return bloques

def analizar_conflicto(current_block, incoming_block):
    current_set = set(line.strip() for line in current_block if line.strip())
    incoming_set = set(line.strip() for line in incoming_block if line.strip())

    if not current_set and incoming_set:
        return "✅ Acción recomendada: Aceptar Incoming (PR).", "incoming"
    elif current_set and not incoming_set:
        return "✅ Acción recomendada: Mantener Current (rama actual).", "current"
    elif current_set == incoming_set:
        return "✅ Acción recomendada: Cualquiera es válida (ambas versiones son iguales).", "igual"
    elif incoming_set.issubset(current_set):
        return "💡 Sugerencia: La PR solo añade líneas ya presentes. Recomendado mantener Current.", "current"
    elif current_set.issubset(incoming_set):
        return "💡 Sugerencia: La PR añade nuevas líneas sin eliminar ninguna. Recomendado combinar.", "combinar"
    elif current_set.isdisjoint(incoming_set):
        return "💡 Sugerencia: No hay líneas en común. Combina ambas versiones si es necesario.", "combinar"
    else:
        return "💡 Sugerencia: Analiza cuidadosamente qué líneas deseas mantener.", "manual"



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
        print(f"{Fore.GREEN}✅ No se detectaron conflictos en esta PR. ¡Cherry-pick limpio!{Style.RESET_ALL}")
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
                conflict_file = parts[1].strip().strip('"')
                decoded = os.fsdecode(unquote(conflict_file)).encode('latin1').decode('utf-8', errors='replace')
                conflictos.append(decoded)
    return conflictos

def analizar_conflictos(conflict_files):
    conflicts_report = []
    conflicto_num = 1
    for file in conflict_files:
        file_path = os.path.normpath(os.path.join(REPO_PATH, file))
        try:
            import chardet
            with open(file_path, "rb") as raw:
                result = chardet.detect(raw.read(10000))
                encoding = result["encoding"] or "utf-8"

            with open(file_path, "r", encoding=encoding, errors="replace") as f:
                lines = f.readlines()
        except Exception as e:
            print(f"{Fore.RED}❌ Error abriendo archivo con conflicto: {file_path} → {e}{Style.RESET_ALL}")
            continue

        file_conflicts = []
        resumen_acciones = set()

        conflicto = []
        dentro_conflicto = False
        leyendo_current = False
        leyendo_incoming = False
        current_block = []
        incoming_block = []
        conflictos_en_archivo = 0

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped_line = line.rstrip("\n")

            if stripped_line.startswith("<<<<<<<"):
                dentro_conflicto = True
                leyendo_current = True
                leyendo_incoming = False
                current_block = []
                incoming_block = []
                conflicto = [f"{Fore.MAGENTA}🔹 Conflicto {conflicto_num} en `{file}`:{Style.RESET_ALL}\n",
                             f"{Fore.YELLOW}🔻 Comienzo del conflicto{Style.RESET_ALL}"]
                i += 1
                continue

            if stripped_line.startswith("=======") and dentro_conflicto:
                conflicto.extend([f"   {l}" for l in current_block])
                conflicto.append(f"{Fore.CYAN}\n🟰 Separador entre versiones{Style.RESET_ALL}")
                leyendo_current = False
                leyendo_incoming = True
                i += 1
                continue

            if stripped_line.startswith(">>>>>>>") and dentro_conflicto:
                conflicto.extend([f"   {l}" for l in incoming_block])
                conflicto.append(f"{Fore.GREEN}🔺 Fin del conflicto{Style.RESET_ALL}\n")
                conflictos_en_archivo += 1

                mensaje, tipo_accion = analizar_conflicto(current_block, incoming_block)
                resumen_acciones.add(tipo_accion)

                if tipo_accion == "manual":
                    conflicto_manual = formatear_conflicto_manual(current_block, incoming_block, archivo=file, conflicto_num=conflicto_num)

                    # Extraer líneas verdes y rojas
                    verdes = [l for l in incoming_block if l.strip() not in map(str.strip, current_block)]
                    rojas = [l for l in current_block if l.strip() not in map(str.strip, incoming_block)]

                    # Insertarlas debajo del mensaje
                    for idx, line in enumerate(conflicto_manual):
                        if "✅ Acción recomendada: Resolución manual requerida." in line:
                            insert_pos = idx + 1
                            break
                    else:
                        insert_pos = len(conflicto_manual)

                    conflicto_manual[insert_pos:insert_pos] = [
                        f"{Fore.RED}🔻 Líneas eliminadas en la PR (rojas):{Style.RESET_ALL}"] + [
                        f"{Fore.RED}- {l.strip()}{Style.RESET_ALL}" for l in rojas]
                    insert_pos += len(rojas) + 1

                    conflicto_manual[insert_pos:insert_pos] = [
                        f"{Fore.GREEN}🔺 Líneas añadidas en la PR (verdes):{Style.RESET_ALL}"] + [
                        f"{Fore.GREEN}+ {l.strip()}{Style.RESET_ALL}" for l in verdes]

                    conflicto.extend(conflicto_manual)
                else:
                    conflicto.append(f"{Fore.CYAN}{mensaje}{Style.RESET_ALL}")

                file_conflicts.extend(conflicto)
                conflicto = []
                dentro_conflicto = False
                leyendo_current = False
                leyendo_incoming = False
                conflicto_num += 1
                i += 1
                continue

            if dentro_conflicto:
                if leyendo_current:
                    current_block.append(stripped_line)
                elif leyendo_incoming:
                    incoming_block.append(stripped_line)

            i += 1

        # Si no hay conflictos manuales, aplicar limpieza
        if all("Resolución manual requerida" not in line for line in file_conflicts):
            file_conflicts_raw = file_conflicts  # Depuración
            conflictos_limpios = filtrar_conflictos_validos(extraer_conflictos(file_conflicts))
            file_conflicts = renderizar_conflictos(conflictos_limpios)

        conflicts_report.append(f"\n📂 Archivo: {file}")
        if conflictos_en_archivo == 1:
            if resumen_acciones == {"incoming"}:
                conflicts_report.append(f"{Fore.BLUE}✅ Todos los conflictos pueden resolverse aceptando Incoming (PR).{Style.RESET_ALL}\n")
            elif resumen_acciones == {"current"}:
                conflicts_report.append(f"{Fore.BLUE}✅ Todos los conflictos pueden resolverse manteniendo Current (rama actual).{Style.RESET_ALL}\n")
            elif resumen_acciones.issubset({"incoming", "current", "igual"}):
                conflicts_report.append(f"{Fore.BLUE}✅ Todos los conflictos pueden resolverse automáticamente (Incoming o Current).{Style.RESET_ALL}\n")
            else:
                conflicts_report.extend(file_conflicts)
        else:
            conflicts_report.extend(file_conflicts)

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
            analizar_conflictos(conflictos)  # Esta función se asegura de mostrar todos los conflictos necesarios
        elif verificar_diferencias(commit_id):
            print(f"{Fore.GREEN}✅ Cherry-pick de PR #{pr_id} aplicado correctamente.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Error: PR #{pr_id} tiene diferencias inesperadas.{Style.RESET_ALL}")
            print("🛠 Por favor, resuelve los conflictos manualmente.")
            print("⚠ El cherry-pick no ha sido abortado para que puedas continuar con la resolución manual.")
    except Exception as e:
        print(f"{Fore.RED}❌ Error en cherry-pick de PR #{pr_id}: {e}{Style.RESET_ALL}")
        if not identificar_conflictos():
            run_command("git cherry-pick --abort")

    input(f"PR actual: #{pr_id} {Fore.BLUE}🔹 Presiona ENTER para hacer commit y continuar con el siguiente cherry-pick...{Style.RESET_ALL}")
    run_command("python 'C:\\Users\\aberdun\\Downloads\\rm\\PR\\verificar_cambios_cherry_pick.py'")

    # Realizar el commit automático
    run_command("git commit --no-verify --no-edit")

    # Limpiar el estado del repositorio
    run_command("git reset --hard")


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
