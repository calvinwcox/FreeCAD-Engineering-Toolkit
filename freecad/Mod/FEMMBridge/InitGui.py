"""
FEMM Bridge Workbench for FreeCAD
Integrates FEMM electromagnetic analysis with FreeCAD
"""

import FreeCAD
import FreeCADGui


class FEMMBridgeWorkbench(FreeCADGui.Workbench):
    """Workbench for FEMM electromagnetic analysis integration"""

    MenuText = "FEMM Bridge"
    ToolTip = "Electromagnetic and magnetic analysis using FEMM"
    Icon = """
        /* XPM */
        static char * femm_xpm[] = {
        "16 16 3 1",
        " 	c None",
        ".	c #2563EB",
        "+	c #60A5FA",
        "                ",
        "      ....      ",
        "    ........    ",
        "   ..++++++..   ",
        "  ..++    ++..  ",
        "  .++      ++.  ",
        " ..+   ..   +.. ",
        " .++  ....  ++. ",
        " .++  ....  ++. ",
        " ..+   ..   +.. ",
        "  .++      ++.  ",
        "  ..++    ++..  ",
        "   ..++++++..   ",
        "    ........    ",
        "      ....      ",
        "                "};
        """

    def Initialize(self):
        """Initialize the workbench"""
        from . import FEMMCommands

        self.appendToolbar("FEMM Analysis", [
            "FEMM_NewMagnetic",
            "FEMM_NewElectrostatic",
            "FEMM_ExportGeometry",
            "FEMM_RunAnalysis",
            "FEMM_ImportResults"
        ])

        self.appendMenu("FEMM", [
            "FEMM_NewMagnetic",
            "FEMM_NewElectrostatic",
            "Separator",
            "FEMM_ExportGeometry",
            "FEMM_RunAnalysis",
            "FEMM_ImportResults",
            "Separator",
            "FEMM_Settings"
        ])

        FreeCAD.Console.PrintMessage("FEMM Bridge workbench initialized\n")

    def Activated(self):
        """Called when workbench is activated"""
        FreeCAD.Console.PrintMessage("FEMM Bridge activated\n")

    def Deactivated(self):
        """Called when workbench is deactivated"""
        pass

    def GetClassName(self):
        return "Gui::PythonWorkbench"


FreeCADGui.addWorkbench(FEMMBridgeWorkbench())
