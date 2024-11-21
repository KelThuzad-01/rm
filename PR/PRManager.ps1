[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$prNumbersList = @()  # Reemplaza con los números reales de las PRs ej: "0001", "0004", "4462"
$currentBranch = git rev-parse --abbrev-ref HEAD 2>&1

function PreCherryPickActions{
    git fetch --all
    git pull
    Start-Process "https://bitbucket.org/iberdrola-clientes/iberdrola-sfdx/pull-requests/$prNumber/diff"
}

function ShowDiff {
    Write-Host "Lines Added    Lines Deleted    File" -ForegroundColor White
    Write-Host "+ Añadidas     - Eliminadas" -ForegroundColor Green
    git diff --cached --numstat | ForEach-Object {
        $line = $_ -split "\s+"
        $added = $line[0]
        $deleted = $line[1]
        $file = $line[2]
        Write-Host "$added" -ForegroundColor Green -NoNewline
        Write-Host "`t`t$deleted" -ForegroundColor Red -NoNewline
        Write-Host "`t`t$($file | Out-String)"
    }
}
#Tareas a ejecutar específicas al proyecto tras realizar commit local
function PostCommitActions {
    Write-Host "Recuerda copiar de las RN la tabla verde + sus pasos manuales. Revisa también la hoja de ProcessBuilder_Flow." -ForegroundColor Red 
    Write-Host "Cambia el estado de la solicitud en el teams IBD si no quedan más PR." -ForegroundColor Red
}

function PreCommitActions{
    $filePath = "C:\Users\aberdun\Downloads\iberdrola-sfdx\config\tests-to-run.list"
    Get-Content $filePath | Sort-Object -Unique | Set-Content $filePath
    git add $filePath
    Write-Host "Removed duplicated lines from $filePath"
}

function AskPushBranch{
    $commitConfirmation2 = Read-Host -Prompt "PRs finalizadas! Presiona 'y' para hacer push al repositorio remoto."
    if ($commitConfirmation2 -match '^[Yy]$') {
        $currentBranch = git rev-parse --abbrev-ref HEAD
        git push --set-upstream origin $currentBranch
        Start-Process "https://bitbucket.org/iberdrola-clientes/iberdrola-sfdx/pull-requests/new?source=$currentBranch&t=1"
    }
    Write-Host "Comparte la PR con los equipos para su revisión" -ForegroundColor Red
    Exit
}

function ShowMenu{
    Write-Host "Rama actual: $currentBranch"
    Write-Host "PR en curso: #$prNumber"
    ShowDiff
    Write-Host "-------------------------"
    Write-Host "[y/Y] Hacer commit de los cambios obtenidos por esta PR"
    Write-Host "-------------------------"
    $commitConfirmation = Read-Host -Prompt "Esperando opción..."
    if($commitConfirmation -match '^[Yy]$') {
        PreCommitActions
        git commit --no-verify
        PostCommitActions
    }else {
        Exit
    }
}

foreach ($prNumber in $prNumbersList) {
    PreCherryPickActions
    git log --all --grep="#$prNumber" -n 1 --format="%H" | ForEach-Object { 
        git cherry-pick -x -n -m 1 $_
        if ($?) { code -r . }
    }
    ShowMenu
}
AskPushBranch