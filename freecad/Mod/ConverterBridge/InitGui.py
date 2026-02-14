"""
Converter Bridge Workbench for FreeCAD
Convert STL, Onshape, and other formats to FreeCAD solids
"""

import FreeCAD
import FreeCADGui


class ConverterBridgeWorkbench(FreeCADGui.Workbench):
    """Workbench for file format conversion"""

    MenuText = "Converter"
    ToolTip = "Convert meshes and external formats to FreeCAD solids"
    Icon = """
        /* XPM */
        static char * converter_xpm[] = {
        "16 16 4 1",
        " 	c None",
        ".	c #10B981",
        "+	c #3B82F6",
        "@	c #F59E0B",
        "                ",
        "   @@@@@@@@     ",
        "   @      @     ",
        "   @  @@  @     ",
        "   @      @     ",
        "   @@@@@@@@     ",
        "        .       ",
        "       ...      ",
        "      .....     ",
        "        .       ",
        "   ++++++++     ",
        "   +      +     ",
        "   +  ++  +     ",
        "   +      +     ",
        "   ++++++++     ",
        "                "};
        """

    def Initialize(self):
        """Initialize the workbench"""
        import ConverterCommands

        self.appendToolbar("Converter", [
            "Converter_STLToSolid",
            "Converter_STLToSolidAdvanced",
            "Converter_BatchConvert",
            "Converter_OnshapeImport",
            "Converter_SolidWorksImport"
        ])

        self.appendMenu("Converter", [
            "Converter_STLToSolid",
            "Converter_STLToSolidAdvanced",
            "Converter_BatchConvert",
            "Separator",
            "Converter_OnshapeImport",
            "Converter_SolidWorksImport"
        ])

        FreeCAD.Console.PrintMessage("Converter Bridge workbench initialized\n")

    def Activated(self):
        """Called when workbench is activated"""
        FreeCAD.Console.PrintMessage("Converter Bridge activated\n")
        FreeCAD.Console.PrintMessage("  STL to Solid - Convert mesh files to editable solids\n")
        FreeCAD.Console.PrintMessage("  Onshape Import - Download parts via Onshape API\n")
        FreeCAD.Console.PrintMessage("  SolidWorks Import - Help importing SW files\n")

    def Deactivated(self):
        """Called when workbench is deactivated"""
        pass

    def GetClassName(self):
        return "Gui::PythonWorkbench"


FreeCADGui.addWorkbench(ConverterBridgeWorkbench())
