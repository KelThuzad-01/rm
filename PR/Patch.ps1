# Lista de PRs en un array
$prNumbersList = @("8852") # Agrega aquí los números de PR que quieres procesar

function Get-CurrentBranch {
    try {
        # Obtener la rama actual usando git rev-parse
        $CurrentBranch = git rev-parse --abbrev-ref HEAD
        if (-not $CurrentBranch) {
            throw "No se pudo obtener la rama actual. ¿Estás en un repositorio Git válido?"
        }
        Write-Host "Actualmente en la rama: $CurrentBranch" -ForegroundColor Cyan
        return $CurrentBranch.Trim()
    }
    catch {
        Write-Error "Error al obtener la rama actual: $_"
        exit 1
    }
}

function Get-MergeCommitHash {
    param (
        [int]$PRNumber
    )
    try {
        # Buscar el commit hash del PR usando git log
        Write-Host "Obteniendo commit hash para PR #$PRNumber..." -ForegroundColor Green
        $CommitHash = git log --all --grep="#$PRNumber" -n 1 --format="%H"
        
        if (-not $CommitHash) {
            Write-Warning "No se encontró un commit de merge para PR #$PRNumber."
        }

        return $CommitHash.Trim()
    }
    catch {
        # Corregimos la cadena para evitar problemas con ":"
        Write-Error ("Error al obtener el commit hash para PR #" + $PRNumber + ": " + $_)
        return $null
    }
}

function Apply-Patch {
    param (
        [string]$MergeCommit
    )
    try {
        # Crear un archivo de parche basado en el commit de merge
        Write-Host "Creando parche desde el commit $MergeCommit..." -ForegroundColor Green
        $PatchFilePath = git format-patch -1 $MergeCommit -o . | ForEach-Object { $_.Trim() }

        if (-not (Test-Path $PatchFilePath)) {
            throw "No se pudo encontrar el archivo de parche generado: $PatchFilePath"
        }

        # Aplicar el parche a la rama actual
        Write-Host "Aplicando el parche $PatchFilePath a la rama actual..." -ForegroundColor Green
        git apply $PatchFilePath

        Write-Host "El parche se aplicó correctamente a la rama actual." -ForegroundColor Cyan

        # Eliminar el parche después de aplicarlo
        Remove-Item -Path $PatchFilePath -Force
    }
    catch {
        # Concatenamos manualmente el mensaje para evitar problemas con ":"
        Write-Error ("Error al aplicar el parche para el commit " + $MergeCommit + ": " + $_)
    }
}

# Obtener la rama actual
$CurrentBranch = Get-CurrentBranch

# Procesar cada PR de la lista
foreach ($PRNumber in $prNumbersList) {
    $PRNumber = $PRNumber.Trim() # Asegurarse de que no haya espacios
    if (-not [int]::TryParse($PRNumber, [ref]0)) {
        Write-Warning "El valor '$PRNumber' no es un número válido. Se omitirá."
        continue
    }

    # Obtener el commit hash del PR
    $MergeCommitHash = Get-MergeCommitHash -PRNumber $PRNumber
    if ($MergeCommitHash) {
        # Aplicar el parche a la rama actual
        Apply-Patch -MergeCommit $MergeCommitHash
    }
}
