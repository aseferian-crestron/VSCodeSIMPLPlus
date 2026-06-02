<#
.SYNOPSIS
    Batch-compiles all SIMPL+ .usp files and reports results.

.PARAMETER Path
    Root folder to search for .usp files. Defaults to current directory.

.PARAMETER Target
    Crestron target series. Defaults to "series3". Use "series2 series3" for both.

.PARAMETER LogDir
    Directory to write per-file build logs. Defaults to a .build subfolder in Path.

.PARAMETER Exclude
    Glob patterns to exclude (e.g. "*.bak.usp", "test_*.usp").

.EXAMPLE
    .\test-compile.ps1 -Path "C:\MyProject" -Target "series3"
#>
param(
    [string]   $Path    = ".",
    [string]   $Target  = "series3",
    [string]   $LogDir  = "",
    [string[]] $Exclude = @()
)

$Compiler = "C:\Program Files (x86)\Crestron\Simpl\SPlusCC.exe"

if (-not (Test-Path $Compiler)) {
    Write-Host "ERROR: SPlusCC.exe not found at: $Compiler" -ForegroundColor Red
    exit 1
}

if ($LogDir -eq "") {
    $LogDir = Join-Path (Resolve-Path $Path) ".build"
}
New-Item -ItemType Directory -Force $LogDir | Out-Null

$files = Get-ChildItem -Recurse -Filter "*.usp" -Path $Path

# Apply exclusions
foreach ($pattern in $Exclude) {
    $files = $files | Where-Object { $_.Name -notlike $pattern }
}

if ($files.Count -eq 0) {
    Write-Host "No .usp files found in: $Path" -ForegroundColor Yellow
    exit 0
}

$targetArgs = $Target -split " "
$passCount  = 0
$failCount  = 0
$warnCount  = 0
$results    = @()

Write-Host ""
Write-Host "SIMPL+ Batch Compiler" -ForegroundColor Cyan
Write-Host "Target: $Target  |  Files: $($files.Count)" -ForegroundColor Cyan
Write-Host ("-" * 60)

foreach ($file in $files) {
    $logFile = Join-Path $LogDir ($file.BaseName + ".build.log")

    # Call per-file to avoid Windows command-line length limits with 200+ files
    $buildArgs = @("\build", $file.FullName, "\target") + $targetArgs + @("\out", $logFile, "\silent")
    & $Compiler @buildArgs | Out-Null
    $exitCode = $LASTEXITCODE

    # Remove compiler intermediate output immediately to avoid filling the disk
    $sWork = Join-Path $file.DirectoryName "SPlsWork"
    if (Test-Path $sWork) { Remove-Item -Recurse -Force $sWork -ErrorAction SilentlyContinue }
    Get-ChildItem $file.DirectoryName -Filter "*.ush" -ErrorAction SilentlyContinue |
        Where-Object { $_.BaseName -eq $file.BaseName } |
        Remove-Item -Force -ErrorAction SilentlyContinue

    $logContent = if (Test-Path $logFile) { Get-Content $logFile } else { @() }
    $errors     = $logContent | Where-Object { $_ -match "^\[.+\]\s+Error" }
    $warnings   = $logContent | Where-Object { $_ -match "^\[.+\]\s+Warning" }

    if ($exitCode -ne 0 -or $errors.Count -gt 0) {
        Write-Host "FAIL  $($file.Name)" -ForegroundColor Red
        foreach ($err in $errors)   { Write-Host "      $err" -ForegroundColor Red }
        foreach ($warn in $warnings) { Write-Host "      $warn" -ForegroundColor Yellow }
        $failCount++
    } elseif ($warnings.Count -gt 0) {
        Write-Host "WARN  $($file.Name)" -ForegroundColor Yellow
        foreach ($warn in $warnings) { Write-Host "      $warn" -ForegroundColor Yellow }
        $warnCount++
        $passCount++
    } else {
        Write-Host "OK    $($file.Name)" -ForegroundColor Green
        $passCount++
    }

    $results += [PSCustomObject]@{
        File     = $file.FullName
        Status   = if ($exitCode -ne 0) { "FAIL" } elseif ($warnings.Count -gt 0) { "WARN" } else { "OK" }
        Errors   = $errors.Count
        Warnings = $warnings.Count
        Log      = $logFile
    }
}

Write-Host ("-" * 60)
Write-Host "Results: $passCount passed, $failCount failed, $warnCount with warnings" -ForegroundColor $(if ($failCount -gt 0) { "Red" } elseif ($warnCount -gt 0) { "Yellow" } else { "Green" })
Write-Host "Logs written to: $LogDir"
Write-Host ""

# Export summary CSV alongside logs
$results | Export-Csv -NoTypeInformation -Path (Join-Path $LogDir "summary.csv")

exit $failCount
