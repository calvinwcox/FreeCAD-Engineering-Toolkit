"""
Converter Bridge Workbench for FreeCAD
Universal CAD file converter with multiple backends:
- FreeCAD native (STEP, IGES, BREP)
- Blender (FBX, glTF, DAE, 3DS, USD, Alembic)
- ODA File Converter (DWG, DXF)
- Online APIs (Parasolid, CATIA, SolidWorks, Inventor, etc.)
"""

import FreeCAD
import FreeCADGui


class ConverterBridgeWorkbench(FreeCADGui.Workbench):
    """Universal CAD Converter Workbench"""

    MenuText = "Converter"
    ToolTip = "Universal CAD file converter - import any format"
    Icon = """
        /* XPM */
        static char * converter_xpm[] = {
        "16 16 5 1",
        " 	c None",
        ".	c #10B981",
        "+	c #3B82F6",
        "@	c #F59E0B",
        "#	c #8B5CF6",
        "                ",
        "  @@@@@  .....  ",
        "  @   @  .   .  ",
        "  @   @  .   .  ",
        "  @@@@@  .....  ",
        "      #         ",
        "     ###        ",
        "    #####       ",
        "     ###        ",
        "      #         ",
        "  +++++  .....  ",
        "  +   +  .   .  ",
        "  +   +  .   .  ",
        "  +++++  .....  ",
        "                ",
        "                "};
        """

    def Initialize(self):
        """Initialize the workbench"""
        import ConverterCommands
        import UniversalConverter

        # Main toolbar - Universal Import is the star
        self.appendToolbar("Universal Converter", [
            "Converter_UniversalImport",
            "Converter_BatchUniversalImport",
            "Separator",
            "Converter_STLToSolid",
            "Converter_ShowFormats"
        ])

        # Secondary toolbar for specific converters
        self.appendToolbar("Specific Converters", [
            "Converter_STLToSolidAdvanced",
            "Converter_OnshapeImport",
            "Converter_SolidWorksImport"
        ])

        # Menu
        self.appendMenu("Converter", [
            "Converter_UniversalImport",
            "Converter_BatchUniversalImport",
            "Separator",
            "Converter_STLToSolid",
            "Converter_STLToSolidAdvanced",
            "Converter_BatchConvert",
            "Separator",
            "Converter_OnshapeImport",
            "Converter_SolidWorksImport",
            "Separator",
            "Converter_ShowFormats"
        ])

        FreeCAD.Console.PrintMessage("Converter Bridge workbench initialized\n")

    def Activated(self):
        """Called when workbench is activated"""
        FreeCAD.Console.PrintMessage("\n")
        FreeCAD.Console.PrintMessage("╔══════════════════════════════════════════════════════════════╗\n")
        FreeCAD.Console.PrintMessage("║            UNIVERSAL CAD CONVERTER                           ║\n")
        FreeCAD.Console.PrintMessage("╠══════════════════════════════════════════════════════════════╣\n")
        FreeCAD.Console.PrintMessage("║  Native:    STEP, IGES, BREP, STL, OBJ                       ║\n")
        FreeCAD.Console.PrintMessage("║  Blender:   FBX, glTF, DAE, 3DS, USD, Alembic, PLY          ║\n")
        FreeCAD.Console.PrintMessage("║  ODA:       DWG, DXF (all versions)                          ║\n")
        FreeCAD.Console.PrintMessage("║  Online:    Parasolid, CATIA, SolidWorks, Inventor, NX      ║\n")
        FreeCAD.Console.PrintMessage("╚══════════════════════════════════════════════════════════════╝\n")
        FreeCAD.Console.PrintMessage("\n")
        FreeCAD.Console.PrintMessage("Use 'Universal Import' to import any CAD file format.\n\n")

    def Deactivated(self):
        """Called when workbench is deactivated"""
        pass

    def GetClassName(self):
        return "Gui::PythonWorkbench"


FreeCADGui.addWorkbench(ConverterBridgeWorkbench())
