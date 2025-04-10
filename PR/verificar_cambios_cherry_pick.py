import os
from git import Repo

REPO_PATH = "C:/Users/aberdun/Downloads/iberdrola-sfdx"
ARCHIVO_DIFF_PR = os.path.join(REPO_PATH, "diff_pr_actual.txt")

def obtener_diff_actual_vs_head():
    repo = Repo(REPO_PATH)
    return repo.git.diff("HEAD", "--unified=0")

def cargar_diff_pr():
    if not os.path.exists(ARCHIVO_DIFF_PR):
        print(f"[ERROR] No se encontró el archivo con el diff original: {ARCHIVO_DIFF_PR}")
        return []
    with open(ARCHIVO_DIFF_PR, "r", encoding="utf-8") as f:
        return f.readlines()

def analizar_cambios(diff_pr_lines, diff_actual):
    bloques_pr = {"+": set(), "-": set()}
    for line in diff_pr_lines:
        if line.startswith("+") and not line.startswith("+++"):
            bloques_pr["+"] .add(line[1:].strip())
        elif line.startswith("-") and not line.startswith("---"):
            bloques_pr["-"].add(line[1:].strip())

    bloques_actual = {"+" : set(), "-" : set()}
    for line in diff_actual.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            bloques_actual["+"] .add(line[1:].strip())
        elif line.startswith("-") and not line.startswith("---"):
            bloques_actual["-"].add(line[1:].strip())

    faltan_por_añadir = bloques_pr["+"] - bloques_actual["+"]
    faltan_por_eliminar = bloques_pr["-"] - bloques_actual["-"]

    return faltan_por_añadir, faltan_por_eliminar

def main():
    print("[INFO] Verificando que se hayan aplicado correctamente los cambios del cherry-pick...")
    diff_pr_lines = cargar_diff_pr()
    if not diff_pr_lines:
        return

    diff_actual = obtener_diff_actual_vs_head()
    faltan_añadir, faltan_eliminar = analizar_cambios(diff_pr_lines, diff_actual)

    if not faltan_añadir and not faltan_eliminar:
        print("[OK] Todos los cambios de la PR se han aplicado correctamente en el cherry-pick.")
    else:
        print("[WARNING] Se detectaron diferencias entre el cherry-pick actual y el contenido esperado de la PR:")
        if faltan_añadir:
            print("  - Líneas que deberían haberse añadido pero no se encuentran:")
            for linea in sorted(faltan_añadir):
                print(f"    + {linea}")
        if faltan_eliminar:
            print("  - Líneas que deberían haberse eliminado pero siguen presentes:")
            for linea in sorted(faltan_eliminar):
                print(f"    - {linea}")
        print("[REVIEW] Por favor, revisa estos cambios manualmente antes de hacer commit.")

if __name__ == "__main__":
    main()
