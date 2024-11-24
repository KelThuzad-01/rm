$prNumbers = @("8504", "8418", "8231", "8221", "8211", "7889", "7713", "8317", "8380", "8873", "8411", "8485", "8510", "8521", "8879" )  # Sustituir por tus números de PR
$ramaOrigenRestauracion = "master";

$outputFile = "files_to_checkout.txt"
$excludedFiles = @(
    "config/tests-to-run.list",
    "config/core-tests-to-run.list"
)

$excludedPaths = @(
    "force-app/main/default/profiles/",
    "force-app/main/default/permissionsets/"
)

Set-Content -Path $outputFile -Value ""
foreach ($prNumber in $prNumbers) {
    $mergeCommit = git log --all --grep="#$prNumber" -n 1 --format="%H"
    if ($mergeCommit) {
        $files = git diff-tree --no-commit-id --name-only -r $mergeCommit
        if ($files) {
            $files | ForEach-Object {
                if ($excludedFiles -notcontains $_ && $excludedPaths -notcontains $_) {
                    Add-Content -Path $outputFile -Value $_
                }
            }
        } 
    }
}
Write-Host "`nRevisa el archivo y edítalo si es necesario. Presiona Enter para continuar..."
Read-Host

Get-Content -Path $outputFile | ForEach-Object {
    if ($_ -ne "") {
        git checkout $ramaOrigenRestauracion $_
    }
}
Write-Host "`nProceso completado."