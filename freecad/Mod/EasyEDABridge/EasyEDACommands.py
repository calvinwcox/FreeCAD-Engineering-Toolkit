"""
EasyEDA Bridge Commands
Import/export PCB designs between FreeCAD and EasyEDA
"""

import os
import json
import FreeCAD
import FreeCADGui
from PySide2 import QtWidgets

# EasyEDA exports JSON format which we can parse


class EasyEDAImportCommand:
    """Import EasyEDA project JSON file"""

    def GetResources(self):
        return {
            'MenuText': 'Import EasyEDA Project',
            'ToolTip': 'Import a PCB design from EasyEDA JSON export'
        }

    def Activated(self):
        # Open file dialog
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Import EasyEDA Project",
            "",
            "EasyEDA JSON (*.json);;All Files (*.*)"
        )

        if not filename:
            return

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.process_easyeda_data(data, filename)

        except Exception as e:
            FreeCAD.Console.PrintError(f"Error importing EasyEDA file: {e}\n")

    def process_easyeda_data(self, data, filename):
        """Process EasyEDA JSON data and create FreeCAD objects"""
        doc = FreeCAD.ActiveDocument
        if not doc:
            name = os.path.splitext(os.path.basename(filename))[0]
            doc = FreeCAD.newDocument(name)

        # Create a group for the PCB
        pcb_group = doc.addObject("App::DocumentObjectGroup", "PCB")

        # EasyEDA format varies, handle common structures
        if isinstance(data, dict):
            if 'head' in data:
                # Standard EasyEDA export format
                self.process_standard_format(data, pcb_group, doc)
            elif 'spiData' in data:
                # Project format
                self.process_project_format(data, pcb_group, doc)
            else:
                FreeCAD.Console.PrintWarning("Unknown EasyEDA format, attempting basic import\n")
                self.process_generic(data, pcb_group, doc)

        doc.recompute()
        FreeCAD.Console.PrintMessage(f"Imported PCB from {filename}\n")

    def process_standard_format(self, data, group, doc):
        """Process standard EasyEDA JSON export"""
        # Extract board outline
        if 'shape' in data:
            for shape in data.get('shape', []):
                if isinstance(shape, str) and shape.startswith('TRACK'):
                    # Parse track data
                    pass

        # Create placeholder info object
        info = doc.addObject("App::FeaturePython", "PCB_Info")
        info.addProperty("App::PropertyString", "Source", "EasyEDA", "Source file")
        info.Source = "EasyEDA"
        group.addObject(info)

    def process_project_format(self, data, group, doc):
        """Process EasyEDA project format"""
        info = doc.addObject("App::FeaturePython", "PCB_Info")
        info.addProperty("App::PropertyString", "Source", "EasyEDA", "Source file")
        info.Source = "EasyEDA Project"
        group.addObject(info)

    def process_generic(self, data, group, doc):
        """Generic processing for unknown formats"""
        info = doc.addObject("App::FeaturePython", "PCB_Info")
        info.addProperty("App::PropertyString", "Source", "EasyEDA", "Source file")
        info.Source = "EasyEDA (unknown format)"
        group.addObject(info)

    def IsActive(self):
        return True


class EasyEDAExport3DCommand:
    """Export 3D model for use in EasyEDA"""

    def GetResources(self):
        return {
            'MenuText': 'Export 3D Model',
            'ToolTip': 'Export selected object as 3D model for EasyEDA component'
        }

    def Activated(self):
        selection = FreeCADGui.Selection.getSelection()
        if not selection:
            FreeCAD.Console.PrintWarning("No objects selected for export\n")
            return

        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            None,
            "Export 3D Model",
            "",
            "STEP Files (*.step *.stp);;WRL Files (*.wrl)"
        )

        if not filename:
            return

        try:
            import Part
            shapes = []
            for obj in selection:
                if hasattr(obj, 'Shape'):
                    shapes.append(obj.Shape)

            if shapes:
                compound = Part.makeCompound(shapes)
                compound.exportStep(filename)
                FreeCAD.Console.PrintMessage(f"Exported to {filename}\n")
            else:
                FreeCAD.Console.PrintWarning("No valid shapes to export\n")

        except Exception as e:
            FreeCAD.Console.PrintError(f"Export error: {e}\n")

    def IsActive(self):
        return FreeCADGui.Selection.hasSelection()


class EasyEDARefreshCommand:
    """Refresh/reload EasyEDA data"""

    def GetResources(self):
        return {
            'MenuText': 'Refresh',
            'ToolTip': 'Reload EasyEDA project data'
        }

    def Activated(self):
        FreeCAD.Console.PrintMessage("Refresh - implementation in progress\n")

    def IsActive(self):
        return FreeCAD.ActiveDocument is not None


class EasyEDASettingsCommand:
    """EasyEDA Bridge settings"""

    def GetResources(self):
        return {
            'MenuText': 'Settings...',
            'ToolTip': 'Configure EasyEDA Bridge settings'
        }

    def Activated(self):
        FreeCAD.Console.PrintMessage("EasyEDA Bridge settings\n")
        # TODO: Create settings dialog for API integration, default paths, etc.

    def IsActive(self):
        return True


# Register commands
FreeCADGui.addCommand('EasyEDA_Import', EasyEDAImportCommand())
FreeCADGui.addCommand('EasyEDA_Export3D', EasyEDAExport3DCommand())
FreeCADGui.addCommand('EasyEDA_Refresh', EasyEDARefreshCommand())
FreeCADGui.addCommand('EasyEDA_Settings', EasyEDASettingsCommand())
