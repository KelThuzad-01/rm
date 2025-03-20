import os
import subprocess
from git import Repo

# Ruta al repositorio donde se harán los cherry-picks
REPO_PATH = "C:\\Users\\aberdun\\Downloads\\iberdrola-sfdx"

# Lista de Pull Requests a aplicar (ordenada de menor a mayor)
PULL_REQUESTS = sorted([1234, 1235, 1240, 1250])  # Reemplazar con PRs reales

def run_command(command, cwd=REPO_PATH, ignore_errors=False):
    """Ejecuta un comando en el shell y devuelve la salida."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, cwd=cwd)
        return result.stdout
    except subprocess.CalledProcessError as e:
        if ignore_errors:
            return e.stdout or e.stderr or ''
        print(f"Error ejecutando {command}: {e.stderr}")
        return None

def obtener_commit_de_pr(pr_id):
    """Busca el commit de merge asociado a la PR usando git log."""
    command = f'git log --all --grep="#{pr_id}" --format="%H"'
    result = run_command(command)
    commit_ids = result.splitlines()
    
    if not commit_ids:
        print(f"⚠ No se encontró un commit para la PR #{pr_id}. Ejecuta `git fetch` y vuelve a intentarlo.")
        return None
    
    return commit_ids[-1]  # Tomamos el commit más reciente

def verificar_diferencias(commit_id):
    """Compara el diff esperado vs el aplicado tras el cherry-pick."""
    run_command("git diff --cached > local_diff.txt")  # Guarda el diff aplicado
    expected_diff = run_command(f"git show {commit_id} --pretty=format:'' --diff-filter=AM")
    applied_diff = run_command("cat local_diff.txt")
    
    if applied_diff.strip() != expected_diff.strip():
        print("⚠ Diferencias inesperadas en el cherry-pick. Revisión manual requerida.")
        run_command("git reset --hard")  # Revertimos los cambios
        return False
    return True

def aplicar_cherry_pick(repo, commit_id, pr_id):
    """Aplica el cherry-pick del commit indicado en modo no commit."""
    print(f"\n🔹 Aplicando cherry-pick de PR #{pr_id} (commit {commit_id})...")
    
    try:
        run_command(f"git cherry-pick -n -m 1 {commit_id}")  # No confirma los cambios
        if verificar_diferencias(commit_id):
            print(f"✅ Cherry-pick de PR #{pr_id} aplicado correctamente.")
        else:
            print(f"❌ Error: PR #{pr_id} tiene diferencias inesperadas.")
            run_command("git cherry-pick --abort")
    except Exception as e:
        print(f"❌ Error en cherry-pick de PR #{pr_id}: {e}")
        run_command("git cherry-pick --abort")  # Revertir en caso de error
    
    input("🔹 Presiona ENTER para continuar con el siguiente cherry-pick...")

def ejecutar_cherry_picks():
    """Ejecuta el proceso de cherry-picks en orden."""
    print("\n📥 Actualizando el repositorio...")
    run_command("git fetch --all")
    run_command("git pull")
    
    repo = Repo(REPO_PATH)
    
    for pr_id in PULL_REQUESTS:
        commit_id = obtener_commit_de_pr(pr_id)
        if commit_id:
            aplicar_cherry_pick(repo, commit_id, pr_id)
        else:
            print(f"⚠ Saltando PR #{pr_id} por falta de commit asociado.")
    
    print("\n🎯 Todos los cherry-picks han sido procesados.")

ejecutar_cherry_picks()