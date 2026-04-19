$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$codeDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $codeDir
$appScript = Join-Path $codeDir "main.py"

function Pause-And-Exit([int]$code) {
    Write-Host ""
    Read-Host "Press Enter to close this window"
    exit $code
}

function Get-PythonCandidates {
    $candidates = [System.Collections.Generic.List[string]]::new()

    $venvPython = Join-Path $projectDir ".venv\Scripts\python.exe"
    if (Test-Path $venvPython) {
        $candidates.Add($venvPython)
    }

    foreach ($commandName in @("python.exe", "python", "py.exe", "py")) {
        try {
            $command = Get-Command $commandName -ErrorAction Stop
            if ($command.Source) {
                $candidates.Add($command.Source)
            }
        } catch {
        }
    }

    $commonRoots = @(
        (Join-Path $env:LOCALAPPDATA "Programs\Python"),
        (Join-Path $env:ProgramFiles "Python"),
        (Join-Path ${env:ProgramFiles(x86)} "Python")
    ) | Where-Object { $_ }

    foreach ($root in $commonRoots) {
        if (-not (Test-Path $root)) {
            continue
        }

        Get-ChildItem -Path $root -Recurse -Filter "python.exe" -ErrorAction SilentlyContinue |
            ForEach-Object { $candidates.Add($_.FullName) }
    }

    $registryKeys = @(
        "HKCU:\Software\Python\PythonCore",
        "HKLM:\Software\Python\PythonCore",
        "HKLM:\Software\WOW6432Node\Python\PythonCore"
    )

    foreach ($key in $registryKeys) {
        if (-not (Test-Path $key)) {
            continue
        }

        Get-ChildItem -Path $key -ErrorAction SilentlyContinue | ForEach-Object {
            $installPathKey = Join-Path $_.PSPath "InstallPath"
            if (-not (Test-Path $installPathKey)) {
                return
            }

            try {
                $installPath = (Get-ItemProperty -Path $installPathKey -ErrorAction Stop).'(default)'
                if (-not $installPath) {
                    $installPath = (Get-ItemProperty -Path $installPathKey -ErrorAction Stop).ExecutablePath
                }
                if ($installPath) {
                    $candidate = $installPath
                    if ((Split-Path $candidate -Leaf) -ne "python.exe") {
                        $candidate = Join-Path $installPath "python.exe"
                    }
                    $candidates.Add($candidate)
                }
            } catch {
            }
        }
    }

    return $candidates |
        Where-Object { $_ -and (Test-Path $_) } |
        Select-Object -Unique
}

function Test-PythonExe([string]$pythonExe) {
    try {
        $null = & $pythonExe -c "import sys; print(sys.version)" 2>$null
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

function Get-PythonCommand {
    $candidates = Get-PythonCandidates

    foreach ($candidate in $candidates) {
        if (Test-PythonExe $candidate) {
            return $candidate
        }
    }

    throw "Python 3 was not found. Install Python 3 and enable Add Python to PATH."
}

function Test-PythonImport([string]$pythonExe, [string]$moduleName) {
    try {
        $null = & $pythonExe -c "import $moduleName" 2>$null
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

function Ensure-QtBinding([string]$pythonExe) {
    if (Test-PythonImport -pythonExe $pythonExe -moduleName "PyQt6") {
        Write-Host "Found PyQt6."
        return
    }

    if (Test-PythonImport -pythonExe $pythonExe -moduleName "PySide6") {
        Write-Host "Found PySide6."
        return
    }

    Write-Host "PyQt6 and PySide6 are missing. Installing PyQt6..."
    $install = Start-Process -FilePath $pythonExe `
        -ArgumentList "-m", "pip", "install", "PyQt6" `
        -NoNewWindow -Wait -PassThru

    if ($install.ExitCode -ne 0) {
        throw "PyQt6 installation failed. Install PyQt6 or PySide6 manually and try again."
    }
}

try {
    Write-Host "====================================="
    Write-Host "Desktop Widget Launcher"
    Write-Host "====================================="
    Write-Host "Project folder: $projectDir"
    Write-Host "Code folder: $codeDir"
    Write-Host "Script: $appScript"
    Write-Host ""

    if (-not (Test-Path $appScript)) {
        throw "main.py was not found."
    }

    $pythonExe = Get-PythonCommand
    Write-Host "Using Python: $pythonExe"
    Write-Host ""

    Ensure-QtBinding -pythonExe $pythonExe

    Write-Host ""
    Write-Host "Starting widget..."
    $run = Start-Process -FilePath $pythonExe `
        -ArgumentList "`"$appScript`"" `
        -WorkingDirectory $codeDir `
        -NoNewWindow -Wait -PassThru

    if ($run.ExitCode -ne 0) {
        throw "The widget exited with error code $($run.ExitCode)."
    }

    Write-Host ""
    Write-Host "The widget finished without errors."
    Pause-And-Exit 0
} catch {
    Write-Host ""
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Pause-And-Exit 1
}
