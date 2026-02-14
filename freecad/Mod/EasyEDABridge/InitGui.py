"""
EasyEDA Bridge Workbench for FreeCAD
Import/export PCB designs from EasyEDA
"""

import FreeCAD
import FreeCADGui


class EasyEDABridgeWorkbench(FreeCADGui.Workbench):
    """Workbench for EasyEDA PCB integration"""

    MenuText = "EasyEDA Bridge"
    ToolTip = "Import and visualize PCB designs from EasyEDA"
    Icon = """
        /* XPM */
        static char * easyeda_xpm[] = {
        "16 16 3 1",
        " 	c None",
        ".	c #10B981",
        "+	c #34D399",
        "                ",
        "  ............  ",
        "  .++++++++++.  ",
        "  .+        +.  ",
        "  .+ ..  .. +.  ",
        "  .+ ..  .. +.  ",
        "  .+        +.  ",
        "  .++++  ++++.  ",
        "  .+        +.  ",
        "  .+ ..  .. +.  ",
        "  .+ ..  .. +.  ",
        "  .+        +.  ",
        "  .++++++++++.  ",
        "  ............  ",
        "                ",
        "                "};
        """

    def Initialize(self):
        """Initialize the workbench"""
        import EasyEDACommands

        self.appendToolbar("EasyEDA", [
            "EasyEDA_Import",
            "EasyEDA_Export3D",
            "EasyEDA_Refresh"
        ])

        self.appendMenu("EasyEDA", [
            "EasyEDA_Import",
            "EasyEDA_Export3D",
            "Separator",
            "EasyEDA_Refresh",
            "EasyEDA_Settings"
        ])

        FreeCAD.Console.PrintMessage("EasyEDA Bridge workbench initialized\n")

    def Activated(self):
        """Called when workbench is activated"""
        FreeCAD.Console.PrintMessage("EasyEDA Bridge activated\n")

    def Deactivated(self):
        """Called when workbench is deactivated"""
        pass

    def GetClassName(self):
        return "Gui::PythonWorkbench"


FreeCADGui.addWorkbench(EasyEDABridgeWorkbench())
