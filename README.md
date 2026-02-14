# FreeCAD Engineering Toolkit

A customized FreeCAD environment designed for comprehensive engineering analysis, inspired by SolidWorks/Onshape workflows.

## Features

### Integrated Analysis Workbenches
- **Structural FEA** - Using FreeCAD's FEM workbench with CalculiX/Elmer
- **CFD** - Fluid dynamics via CfdOF (OpenFOAM)
- **Thermal Analysis** - Heat transfer simulations
- **FEMM Bridge** - Electromagnetic/magnetic analysis integration
- **EasyEDA Bridge** - PCB design import/export

### Developer Tools
- **Claude Console** - Integrated terminal for running Claude Code directly in FreeCAD
- **GitHub Integration** - Version control for all projects and customizations

## Installation

### Prerequisites
- Windows 10/11
- [FreeCAD 0.21+](https://www.freecad.org/downloads.php) (Weekly build recommended)
- [FEMM](https://www.femm.info/wiki/Download) (for electromagnetic analysis)
- [GitHub CLI](https://cli.github.com/) (for version control)
- [Claude Code](https://claude.ai/claude-code) (for AI assistance)

### Quick Setup
```powershell
# Run the setup script
.\scripts\setup.ps1
```

## Project Structure
```
FreeCAD-Engineering-Toolkit/
├── freecad/
│   ├── Mod/                  # Custom workbenches
│   │   ├── ClaudeConsole/    # Integrated terminal
│   │   ├── FEMMBridge/       # FEMM integration
│   │   └── EasyEDABridge/    # EasyEDA import/export
│   ├── Macro/                # Custom macros
│   └── user.cfg              # UI customizations
├── templates/                # Project templates
├── scripts/                  # Setup and automation
└── .github/workflows/        # CI/CD
```

## Usage

### Claude Console
Press `Ctrl+Shift+C` in FreeCAD to open the Claude Console panel, then run:
```
claude
```

### FEMM Analysis
1. Create your geometry in FreeCAD
2. Switch to FEMM Bridge workbench
3. Define materials and boundary conditions
4. Run electromagnetic analysis

## License
MIT
