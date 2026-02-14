"""
FEMM Bridge Commands
Provides FreeCAD commands for FEMM integration
"""

import os
import subprocess
import FreeCAD
import FreeCADGui

# Path to FEMM installation (default Windows location)
FEMM_PATH = r"C:\femm42\bin\femm.exe"


def find_femm():
    """Locate FEMM installation"""
    possible_paths = [
        r"C:\femm42\bin\femm.exe",
        r"C:\Program Files\femm42\bin\femm.exe",
        r"C:\Program Files (x86)\femm42\bin\femm.exe",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


def get_femm_path():
    """Get FEMM executable path from settings or auto-detect"""
    # Try to get from FreeCAD parameters
    params = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/FEMMBridge")
    path = params.GetString("FEMMPath", "")

    if path and os.path.exists(path):
        return path

    # Auto-detect
    detected = find_femm()
    if detected:
        params.SetString("FEMMPath", detected)
        return detected

    return None


class FEMMNewMagneticCommand:
    """Create a new magnetic analysis"""

    def GetResources(self):
        return {
            'MenuText': 'New Magnetic Problem',
            'ToolTip': 'Create a new 2D magnetic analysis problem'
        }

    def Activated(self):
        femm_path = get_femm_path()
        if not femm_path:
            FreeCAD.Console.PrintError("FEMM not found. Please set the path in preferences.\n")
            return

        # Create a new FEMM analysis object in the document
        doc = FreeCAD.ActiveDocument
        if not doc:
            doc = FreeCAD.newDocument("FEMM_Analysis")

        obj = doc.addObject("App::FeaturePython", "MagneticAnalysis")
        obj.addProperty("App::PropertyString", "AnalysisType", "FEMM", "Type of analysis")
        obj.AnalysisType = "Magnetic"
        obj.addProperty("App::PropertyFloat", "Frequency", "FEMM", "Frequency in Hz (0 for DC)")
        obj.Frequency = 0.0
        obj.addProperty("App::PropertyString", "Units", "FEMM", "Length units")
        obj.Units = "millimeters"

        doc.recompute()
        FreeCAD.Console.PrintMessage("Created new magnetic analysis\n")

    def IsActive(self):
        return True


class FEMMNewElectrostaticCommand:
    """Create a new electrostatic analysis"""

    def GetResources(self):
        return {
            'MenuText': 'New Electrostatic Problem',
            'ToolTip': 'Create a new 2D electrostatic analysis problem'
        }

    def Activated(self):
        doc = FreeCAD.ActiveDocument
        if not doc:
            doc = FreeCAD.newDocument("FEMM_Analysis")

        obj = doc.addObject("App::FeaturePython", "ElectrostaticAnalysis")
        obj.addProperty("App::PropertyString", "AnalysisType", "FEMM", "Type of analysis")
        obj.AnalysisType = "Electrostatic"
        obj.addProperty("App::PropertyString", "Units", "FEMM", "Length units")
        obj.Units = "millimeters"

        doc.recompute()
        FreeCAD.Console.PrintMessage("Created new electrostatic analysis\n")

    def IsActive(self):
        return True


class FEMMExportGeometryCommand:
    """Export FreeCAD geometry to FEMM"""

    def GetResources(self):
        return {
            'MenuText': 'Export to FEMM',
            'ToolTip': 'Export selected geometry to FEMM format'
        }

    def Activated(self):
        selection = FreeCADGui.Selection.getSelection()
        if not selection:
            FreeCAD.Console.PrintWarning("No objects selected for export\n")
            return

        # TODO: Implement geometry export
        # This will convert FreeCAD shapes to FEMM Lua script or DXF
        FreeCAD.Console.PrintMessage("Geometry export - implementation in progress\n")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None


class FEMMRunAnalysisCommand:
    """Run FEMM analysis"""

    def GetResources(self):
        return {
            'MenuText': 'Run Analysis',
            'ToolTip': 'Run the FEMM analysis'
        }

    def Activated(self):
        femm_path = get_femm_path()
        if not femm_path:
            FreeCAD.Console.PrintError("FEMM not found\n")
            return

        # TODO: Implement analysis execution via FEMM's Lua scripting
        FreeCAD.Console.PrintMessage("Analysis execution - implementation in progress\n")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None


class FEMMImportResultsCommand:
    """Import FEMM analysis results"""

    def GetResources(self):
        return {
            'MenuText': 'Import Results',
            'ToolTip': 'Import results from FEMM analysis'
        }

    def Activated(self):
        # TODO: Implement results import
        FreeCAD.Console.PrintMessage("Results import - implementation in progress\n")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None


class FEMMSettingsCommand:
    """Open FEMM Bridge settings"""

    def GetResources(self):
        return {
            'MenuText': 'Settings...',
            'ToolTip': 'Configure FEMM Bridge settings'
        }

    def Activated(self):
        # TODO: Create settings dialog
        femm_path = get_femm_path()
        if femm_path:
            FreeCAD.Console.PrintMessage(f"FEMM path: {femm_path}\n")
        else:
            FreeCAD.Console.PrintWarning("FEMM not configured\n")

    def IsActive(self):
        return True


# Register commands
FreeCADGui.addCommand('FEMM_NewMagnetic', FEMMNewMagneticCommand())
FreeCADGui.addCommand('FEMM_NewElectrostatic', FEMMNewElectrostaticCommand())
FreeCADGui.addCommand('FEMM_ExportGeometry', FEMMExportGeometryCommand())
FreeCADGui.addCommand('FEMM_RunAnalysis', FEMMRunAnalysisCommand())
FreeCADGui.addCommand('FEMM_ImportResults', FEMMImportResultsCommand())
FreeCADGui.addCommand('FEMM_Settings', FEMMSettingsCommand())
