"""
Claude Console Workbench for FreeCAD
Embeds a terminal panel for running Claude Code directly in FreeCAD
"""

import FreeCAD
import FreeCADGui


class ClaudeConsoleWorkbench(FreeCADGui.Workbench):
    """Workbench with integrated Claude Code terminal"""

    MenuText = "Claude Console"
    ToolTip = "Integrated terminal for Claude Code AI assistance"
    Icon = """
        /* XPM */
        static char * claude_xpm[] = {
        "16 16 3 1",
        " 	c None",
        ".	c #D97706",
        "+	c #FFFFFF",
        "                ",
        "     ......     ",
        "   ..........   ",
        "  ............  ",
        " ....+....+.... ",
        " ....+....+.... ",
        " .............. ",
        " .............. ",
        " ..+........+.. ",
        " ...+......+... ",
        "  ....++++....  ",
        "   ..........   ",
        "     ......     ",
        "                ",
        "                ",
        "                "};
        """

    def Initialize(self):
        """Initialize the workbench"""
        from . import ClaudeConsolePanel

        self.appendToolbar("Claude Console", ["ClaudeConsole_Toggle"])
        self.appendMenu("Claude Console", ["ClaudeConsole_Toggle", "ClaudeConsole_Clear"])

        FreeCAD.Console.PrintMessage("Claude Console workbench initialized\n")

    def Activated(self):
        """Called when workbench is activated"""
        from . import ClaudeConsolePanel
        ClaudeConsolePanel.show_console()
        FreeCAD.Console.PrintMessage("Claude Console activated - press Ctrl+Shift+C to toggle\n")

    def Deactivated(self):
        """Called when workbench is deactivated"""
        pass

    def GetClassName(self):
        return "Gui::PythonWorkbench"


# Register the workbench
FreeCADGui.addWorkbench(ClaudeConsoleWorkbench())
