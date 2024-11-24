# Script para deshacer cambios de PRs específicos en la rama actual
# Configuración inicial: Lista de números de PR
$prNumbers = @("8504", "8418", "8231", "8221", "8211", "7889", "7713", "8317", "8380", "8873", "8411", "8485", "8510", "8521", "8879" )  # Sustituir por tus números de PR
$outputFile = "files_to_checkout.txt"
$ramaOrigenRestauracion = "master";

# Lista de archivos a excluir
$excludedFiles = @(
    "config/tests-to-run.list",
    "config/core-tests-to-run.list"
)

# Crear o limpiar el archivo de salida
Set-Content -Path $outputFile -Value ""

# Procesar cada PR
foreach ($prNumber in $prNumbers) {

    # Obtener el commit de merge del PR
    $mergeCommit = git log --all --grep="#$prNumber" -n 1 --format="%H"

    if ($mergeCommit) {
        # Obtener los archivos modificados en ese commit
        $files = git diff-tree --no-commit-id --name-only -r $mergeCommit

        if ($files) {
            $files | ForEach-Object {
                if ($excludedFiles -notcontains $_) {
                    Add-Content -Path $outputFile -Value $_
                } else {
                }
            }
        } else {
        }
    } else {
    }
}

# Confirmación antes de hacer el checkout
Write-Host "`nRevisa el archivo y edítalo si es necesario. Presiona Enter para continuar..."
Read-Host

# Realizar git checkout de los archivos listados
Get-Content -Path $outputFile | ForEach-Object {
    if ($_ -ne "") {
        git checkout $ramaOrigenRestauracion $_
    }
}

Write-Host "`nProceso completado."
