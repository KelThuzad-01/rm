$prNumbersList = @("8317") # Agrega aquí los números de PR que quieres procesar

function Get-MergeCommitHash {
    param (
        [int]$PRNumber
    )
    try {
        # Buscar el commit hash del PR usando git log
        Write-Host "Obteniendo commit hash para PR #$PRNumber..." -ForegroundColor Green
        $CommitHash = git log --all --grep="#$PRNumber" --format="%H" | Select-Object -Last 1
        
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
        git apply --3way --ignore-space-change --ignore-whitespace $PatchFilePath

        # Eliminar el parche después de aplicarlo
        #Remove-Item -Path $PatchFilePath -Force
    }
    catch {
        # Concatenamos manualmente el mensaje para evitar problemas con ":"
        Write-Error ("Error al aplicar el parche para el commit " + $MergeCommit + ": " + $_)
    }
}

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
