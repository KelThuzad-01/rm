#!/usr/bin/env python3

import subprocess
from pathlib import Path
from datetime import datetime

# ==============================
# CONFIGURACIÓN (EDITA ESTO)
# ==============================

REPO_PATH = Path(r"C://Users//aberdun.SEIDORBCN//Downloads//ajbcn")

MERGE_COMMITS = [
    "",
    "",
]

# ==============================


def run_git_command(args):
    result = subprocess.run(
        ["git", "-C", str(REPO_PATH)] + args,
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.strip()


def validate_repo():
    try:
        output = run_git_command(["rev-parse", "--is-inside-work-tree"])
        if output != "true":
            raise ValueError("La ruta no es un repositorio git válido.")
    except Exception:
        raise ValueError("La ruta no es un repositorio git válido.")


def is_merge_commit(commit_id):
    output = run_git_command(["rev-list", "--parents", "-n", "1", commit_id])
    parts = output.split()
    return len(parts) > 2


def get_commit_timestamp(commit_id):
    ts = run_git_command(["show", "-s", "--format=%ct", commit_id])
    return int(ts)


def main():
    validate_repo()

    commit_data = []

    for commit_id in MERGE_COMMITS:
        try:
            if not is_merge_commit(commit_id):
                print(f"⚠️  {commit_id} NO es un merge commit.")
            timestamp = get_commit_timestamp(commit_id)
            commit_data.append((commit_id, timestamp))
        except Exception as e:
            print(f"Error con commit {commit_id}: {e}")
            return

    # Ordenar por timestamp ascendente
    commit_data.sort(key=lambda x: x[1])

    print("\nOrden correcto para cherry-pick (antiguo → nuevo):\n")

    for commit_id, ts in commit_data:
        readable_date = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{commit_id}  |  {readable_date}")

    print("\nComandos sugeridos:\n")

    for commit_id, _ in commit_data:
        print(f"git cherry-pick -m 1 {commit_id}")


if __name__ == "__main__":
    main()