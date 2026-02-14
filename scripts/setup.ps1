# FreeCAD Engineering Toolkit Setup Script
# Run this script to set up your FreeCAD environment

param(
    [switch]$SkipFreeCADInstall,
    [switch]$SkipAddons
)

$ErrorActionPreference = "Stop"

Write-Host "================================" -ForegroundColor Cyan
Write-Host "FreeCAD Engineering Toolkit Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory and repo root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

# FreeCAD user data directory
$FreeCADUserDir = "$env:APPDATA\FreeCAD"
$FreeCADModDir = "$FreeCADUserDir\Mod"
$FreeCADMacroDir = "$FreeCADUserDir\Macro"

# Check for FreeCAD installation
function Test-FreeCADInstalled {
    $paths = @(
        "$env:LOCALAPPDATA\Programs\FreeCAD*\bin\FreeCAD.exe",
        "C:\Program Files\FreeCAD*\bin\FreeCAD.exe",
        "$env:USERPROFILE\AppData\Local\FreeCAD*\bin\FreeCAD.exe"
    )

    foreach ($pattern in $paths) {
        $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) {
            return $found.FullName
        }
    }
    return $null
}

# Download and install FreeCAD
function Install-FreeCAD {
    Write-Host "FreeCAD not found. Downloading..." -ForegroundColor Yellow

    # Get latest weekly build URL
    $downloadUrl = "https://github.com/FreeCAD/FreeCAD/releases/download/1.0.0/FreeCAD_1.0.0-conda-Windows-x86_64-installer-1.exe"
    $installerPath = "$env:TEMP\FreeCAD-installer.exe"

    Write-Host "Downloading FreeCAD 1.0 (stable release)..."
    Write-Host "URL: $downloadUrl"

    try {
        Invoke-WebRequest -Uri $downloadUrl -OutFile $installerPath -UseBasicParsing
        Write-Host "Download complete. Running installer..." -ForegroundColor Green

        # Run installer
        Start-Process -FilePath $installerPath -Wait

        Write-Host "Installation complete!" -ForegroundColor Green
    }
    catch {
        Write-Host "Download failed. Please install FreeCAD manually:" -ForegroundColor Red
        Write-Host "  https://www.freecad.org/downloads.php" -ForegroundColor White
        Write-Host "  Or for weekly builds: https://github.com/FreeCAD/FreeCAD-Bundle/releases/tag/weekly-builds" -ForegroundColor White
        return $false
    }

    return $true
}

# Create symbolic links for workbenches
function Install-Workbenches {
    Write-Host ""
    Write-Host "Installing custom workbenches..." -ForegroundColor Cyan

    # Create FreeCAD directories if they don't exist
    if (!(Test-Path $FreeCADModDir)) {
        New-Item -ItemType Directory -Path $FreeCADModDir -Force | Out-Null
        Write-Host "  Created: $FreeCADModDir"
    }

    if (!(Test-Path $FreeCADMacroDir)) {
        New-Item -ItemType Directory -Path $FreeCADMacroDir -Force | Out-Null
        Write-Host "  Created: $FreeCADMacroDir"
    }

    # Link each workbench
    $workbenches = @("ClaudeConsole", "FEMMBridge", "EasyEDABridge")

    foreach ($wb in $workbenches) {
        $source = "$RepoRoot\freecad\Mod\$wb"
        $target = "$FreeCADModDir\$wb"

        if (Test-Path $target) {
            # Remove existing link/folder
            if ((Get-Item $target).Attributes -band [IO.FileAttributes]::ReparsePoint) {
                cmd /c rmdir "$target" 2>$null
            } else {
                Remove-Item -Path $target -Recurse -Force
            }
        }

        # Create symbolic link (requires admin) or copy
        try {
            New-Item -ItemType SymbolicLink -Path $target -Target $source -ErrorAction Stop | Out-Null
            Write-Host "  Linked: $wb -> $target" -ForegroundColor Green
        }
        catch {
            # Fallback: create junction or copy
            try {
                cmd /c mklink /J "$target" "$source" 2>$null
                Write-Host "  Linked (junction): $wb -> $target" -ForegroundColor Green
            }
            catch {
                Copy-Item -Path $source -Destination $target -Recurse -Force
                Write-Host "  Copied: $wb -> $target" -ForegroundColor Yellow
                Write-Host "    (Run as admin for symbolic links)" -ForegroundColor Gray
            }
        }
    }
}

# Install recommended FreeCAD addons
function Install-Addons {
    Write-Host ""
    Write-Host "Recommended FreeCAD addons (install via Tools > Addon Manager):" -ForegroundColor Cyan
    Write-Host "  - A2plus (Assembly workbench)" -ForegroundColor White
    Write-Host "  - Assembly4 (Alternative assembly)" -ForegroundColor White
    Write-Host "  - CfdOF (CFD/OpenFOAM integration)" -ForegroundColor White
    Write-Host "  - Fasteners (Standard fasteners library)" -ForegroundColor White
    Write-Host "  - Render (Rendering workbench)" -ForegroundColor White
    Write-Host ""
}

# Main setup
Write-Host "Checking for FreeCAD..." -ForegroundColor Cyan
$freecadPath = Test-FreeCADInstalled

if ($freecadPath) {
    Write-Host "  Found: $freecadPath" -ForegroundColor Green
}
elseif (!$SkipFreeCADInstall) {
    $install = Read-Host "FreeCAD not found. Install now? (Y/n)"
    if ($install -ne 'n' -and $install -ne 'N') {
        Install-FreeCAD
    }
}

# Install workbenches
Install-Workbenches

# Show addon recommendations
if (!$SkipAddons) {
    Install-Addons
}

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Open FreeCAD" -ForegroundColor White
Write-Host "  2. Go to View > Workbenches > Claude Console" -ForegroundColor White
Write-Host "  3. Use Ctrl+Shift+C to toggle the console" -ForegroundColor White
Write-Host ""
Write-Host "For FEMM integration, ensure FEMM is installed at:" -ForegroundColor Cyan
Write-Host "  C:\femm42\bin\femm.exe" -ForegroundColor White
Write-Host ""
