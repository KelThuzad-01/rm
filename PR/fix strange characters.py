import subprocess
import os

REPO_PATH = "C:\\Users\\Alejandro\\Downloads\\iberdrola-sfdx"
RAMA_BASE = "origin/master"

def run_command(cmd, cwd=REPO_PATH):
    result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, cwd=cwd)
    return result.stdout.strip()

def obtener_flows_modificados():
    archivos = run_command(f"git diff --name-only {RAMA_BASE}").splitlines()
    return [f for f in archivos]

def contiene_caracteres_corruptos(texto):
    return any(seq in texto for seq in [
        'Ã¡', 'Ã©', 'Ã­', 'Ã³', 'Ãº', 'Ã±',
        'ÃÁ', 'ÃÉ', 'ÃÍ', 'ÃÓ', 'ÃÚ', 'ÃÑ',
        'Ã', 'Ã‰', 'Ã', 'Ã“', 'Ãš', 'Ã‘',  # estos aparecen por errores de doble codificación
        'Â¿', 'Â¡', 'Â«', 'Â»', 'Â·', 'Â°',
        'Â', '�',  # carácter de reemplazo y símbolos sueltos
    ])

def reemplazar_caracteres_corruptos(texto):
    reemplazos = {
        'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú', 'Ã±': 'ñ',
        'Ã': 'Á', 'Ã‰': 'É', 'Ã': 'Í', 'Ã“': 'Ó', 'Ãš': 'Ú', 'Ã‘': 'Ñ',
        'Ã¨': 'è', 'Ã§': 'ç', 'Ãª': 'ê',
        'â€œ': '“', 'â€': '”', 'â€˜': '‘', 'â€™': '’',
        'â€“': '–', 'â€”': '—', 'â€¦': '…',
        'Â¿': '¿', 'Â¡': '¡', 'Â·': '·', 'Â°': '°', 'Â«': '«', 'Â»': '»',
        'Â': '', '�': '',  # eliminar símbolos basura
    }
    for malo, bueno in reemplazos.items():
        texto = texto.replace(malo, bueno)
    return texto


def reparar_codificacion(file_path):
    full_path = os.path.join(REPO_PATH, file_path)
    try:
        with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
            contenido = f.read()

        if not contiene_caracteres_corruptos(contenido):
            return

        contenido_corregido = reemplazar_caracteres_corruptos(contenido)

        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(contenido_corregido)

        print(f"✅ Reparado (mapeo manual): {file_path}")
    except Exception as e:
        print(f"❌ Error al reparar {file_path}: {e}")



def main():
    flows = obtener_flows_modificados()
    if not flows:
        print("✅ No hay flows modificados respecto a origin/develop.")
        return

    print(f"🩺 Se encontraron {len(flows)} flows modificados:")
    for f in flows:
        print(f" - {f}")
    print("\nIniciando revisión y reparación...\n")

    for flow in flows:
        reparar_codificacion(flow)

main()