"""
SolidWorks-Style Configuration for FreeCAD
Applies keyboard shortcuts, mouse behavior, and UI settings similar to SolidWorks
"""

import FreeCAD
import FreeCADGui
from PySide2 import QtWidgets, QtCore, QtGui


def apply_solidworks_shortcuts():
    """Apply SolidWorks-style keyboard shortcuts"""

    # Get the main window
    mw = FreeCADGui.getMainWindow()

    # Define SolidWorks-style shortcuts
    shortcuts = {
        # View controls
        'Std_ViewFront': 'Ctrl+1',
        'Std_ViewBack': 'Ctrl+2',
        'Std_ViewRight': 'Ctrl+3',
        'Std_ViewLeft': 'Ctrl+4',
        'Std_ViewTop': 'Ctrl+5',
        'Std_ViewBottom': 'Ctrl+6',
        'Std_ViewIsometric': 'Ctrl+7',
        'Std_ViewFitAll': 'F',
        'Std_ViewHome': 'Home',

        # Sketch commands (when in sketcher)
        'Sketcher_CreateLine': 'L',
        'Sketcher_CreateRectangle': 'R',
        'Sketcher_CreateCircle': 'C',
        'Sketcher_CreateArc': 'A',
        'Sketcher_CreatePoint': 'P',
        'Sketcher_ConstrainCoincident': 'Ctrl+Shift+C',
        'Sketcher_ConstrainHorizontal': 'H',
        'Sketcher_ConstrainVertical': 'V',
        'Sketcher_ConstrainEqual': 'E',
        'Sketcher_ConstrainSymmetric': 'Ctrl+Shift+S',
        'Sketcher_ConstrainLock': 'Ctrl+L',
        'Sketcher_ConstrainDistance': 'D',
        'Sketcher_Trimming': 'T',
        'Sketcher_External': 'X',
        'Sketcher_CreateFillet': 'Shift+F',

        # Part Design commands
        'PartDesign_Pad': 'Ctrl+Shift+P',
        'PartDesign_Pocket': 'Ctrl+Shift+K',
        'PartDesign_Revolution': 'Ctrl+Shift+R',
        'PartDesign_Fillet': 'Ctrl+Shift+F',
        'PartDesign_Chamfer': 'Ctrl+Shift+H',
        'PartDesign_NewSketch': 'S',
        'PartDesign_Hole': 'Ctrl+Shift+O',
        'PartDesign_LinearPattern': 'Ctrl+Shift+L',
        'PartDesign_PolarPattern': 'Ctrl+Shift+A',
        'PartDesign_Mirrored': 'Ctrl+M',

        # General
        'Std_Undo': 'Ctrl+Z',
        'Std_Redo': 'Ctrl+Y',
        'Std_Cut': 'Ctrl+X',
        'Std_Copy': 'Ctrl+C',
        'Std_Paste': 'Ctrl+V',
        'Std_Delete': 'Delete',
        'Std_SelectAll': 'Ctrl+A',
        'Std_New': 'Ctrl+N',
        'Std_Open': 'Ctrl+O',
        'Std_Save': 'Ctrl+S',
        'Std_SaveAs': 'Ctrl+Shift+S',
        'Std_Print': 'Ctrl+P',

        # Measurement
        'Part_Measure_Linear': 'Ctrl+Shift+M',

        # Selection
        'Std_BoxSelection': 'B',
    }

    # Apply shortcuts using FreeCAD's parameter system
    params = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Shortcut")

    for cmd, shortcut in shortcuts.items():
        try:
            params.SetString(cmd, shortcut)
        except:
            pass  # Command may not exist

    FreeCAD.Console.PrintMessage("SolidWorks-style shortcuts applied!\n")
    FreeCAD.Console.PrintMessage("Key shortcuts:\n")
    FreeCAD.Console.PrintMessage("  S = New Sketch\n")
    FreeCAD.Console.PrintMessage("  L = Line, R = Rectangle, C = Circle\n")
    FreeCAD.Console.PrintMessage("  F = Fit All, Ctrl+1-7 = Standard Views\n")
    FreeCAD.Console.PrintMessage("  D = Dimension, T = Trim\n")

    return shortcuts


def apply_solidworks_mouse():
    """Configure mouse behavior like SolidWorks"""

    # Mouse settings via parameters
    params = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View")

    # Middle mouse = rotate (like SolidWorks)
    # Shift+Middle = pan
    # Scroll = zoom
    params.SetInt("NavigationStyle", 1)  # CAD navigation style
    params.SetBool("ZoomAtCursor", True)  # Zoom at cursor position
    params.SetBool("InvertZoom", False)
    params.SetInt("ZoomStep", 20)  # Zoom sensitivity

    # Orbit style - turntable is more SolidWorks-like
    params.SetInt("OrbitStyle", 1)  # Turntable

    FreeCAD.Console.PrintMessage("Mouse controls configured:\n")
    FreeCAD.Console.PrintMessage("  Middle Mouse = Rotate\n")
    FreeCAD.Console.PrintMessage("  Shift + Middle = Pan\n")
    FreeCAD.Console.PrintMessage("  Scroll = Zoom (at cursor)\n")


def apply_solidworks_ui():
    """Configure UI elements like SolidWorks"""

    params = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/View")

    # Dark background like SolidWorks
    # params.SetUnsigned("BackgroundColor", 0x36454F)  # Dark gray-blue
    # params.SetUnsigned("BackgroundColor2", 0x36454F)
    # params.SetUnsigned("BackgroundColor3", 0x4A5568)
    # params.SetUnsigned("BackgroundColor4", 0x4A5568)

    # Grid settings
    params.SetBool("ShowGrid", True)

    # Selection highlighting
    params.SetUnsigned("HighlightColor", 0x00FF00)  # Green highlight
    params.SetUnsigned("SelectionColor", 0x00FF00)  # Green selection

    FreeCAD.Console.PrintMessage("UI settings applied\n")


def setup_feature_manager():
    """Tips for using the Model Tree like SolidWorks FeatureManager"""

    msg = """
=== Feature Manager Tips ===
FreeCAD's Model Tree works similarly to SolidWorks FeatureManager:

- Right-click features to Edit, Delete, or Suppress
- Drag features to reorder (some operations)
- Double-click sketches to edit them
- Use 'Space' to toggle visibility (like hide/show in SW)
- Dependencies shown in tree structure

To see it more like SolidWorks:
- View > Panels > Model (should already be visible)
- The tree shows: Document > Body > Features > Sketches
"""
    FreeCAD.Console.PrintMessage(msg)


def apply_all_solidworks_settings():
    """Apply all SolidWorks-style settings"""
    FreeCAD.Console.PrintMessage("\n" + "="*50 + "\n")
    FreeCAD.Console.PrintMessage("Applying SolidWorks-Style Configuration\n")
    FreeCAD.Console.PrintMessage("="*50 + "\n\n")

    apply_solidworks_shortcuts()
    apply_solidworks_mouse()
    apply_solidworks_ui()
    setup_feature_manager()

    FreeCAD.Console.PrintMessage("\n" + "="*50 + "\n")
    FreeCAD.Console.PrintMessage("Configuration complete! Restart FreeCAD for all changes.\n")
    FreeCAD.Console.PrintMessage("="*50 + "\n")


# Command to apply settings from FreeCAD
class ApplySolidWorksStyleCommand:
    """Command to apply SolidWorks-style settings"""

    def GetResources(self):
        return {
            'MenuText': 'Apply SolidWorks Style',
            'ToolTip': 'Configure FreeCAD with SolidWorks-like shortcuts and behavior'
        }

    def Activated(self):
        apply_all_solidworks_settings()

    def IsActive(self):
        return True


# Register command
FreeCADGui.addCommand('ClaudeConsole_SolidWorksStyle', ApplySolidWorksStyleCommand())


# Quick reference card
QUICK_REFERENCE = """
╔══════════════════════════════════════════════════════════════╗
║           SOLIDWORKS-STYLE KEYBOARD SHORTCUTS                 ║
╠══════════════════════════════════════════════════════════════╣
║  SKETCHING                    │  FEATURES                     ║
║  S = New Sketch               │  Ctrl+Shift+P = Extrude (Pad) ║
║  L = Line                     │  Ctrl+Shift+K = Cut (Pocket)  ║
║  R = Rectangle                │  Ctrl+Shift+R = Revolve       ║
║  C = Circle                   │  Ctrl+Shift+F = Fillet        ║
║  A = Arc                      │  Ctrl+Shift+H = Chamfer       ║
║  T = Trim                     │  Ctrl+M = Mirror              ║
║  D = Dimension                │  Ctrl+Shift+O = Hole          ║
║  X = External Reference       │                               ║
╠──────────────────────────────────────────────────────────────╣
║  VIEWS                        │  GENERAL                      ║
║  F = Fit All                  │  Ctrl+Z = Undo                ║
║  Ctrl+1 = Front               │  Ctrl+Y = Redo                ║
║  Ctrl+2 = Back                │  Ctrl+S = Save                ║
║  Ctrl+3 = Right               │  Delete = Delete              ║
║  Ctrl+5 = Top                 │  Space = Toggle Visibility    ║
║  Ctrl+7 = Isometric           │  B = Box Select               ║
╠──────────────────────────────────────────────────────────────╣
║  MOUSE                                                        ║
║  Middle Button = Rotate       │  Scroll = Zoom                ║
║  Shift + Middle = Pan         │  Right Click = Context Menu   ║
╚══════════════════════════════════════════════════════════════╝
"""

def print_quick_reference():
    """Print the quick reference card"""
    print(QUICK_REFERENCE)
