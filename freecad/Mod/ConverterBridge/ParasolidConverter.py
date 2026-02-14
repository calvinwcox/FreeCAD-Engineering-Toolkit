"""
Parasolid X_T to STEP Converter
Attempts to convert Parasolid text files using available methods

The Parasolid text format (.x_t) is documented in ISO 14306.
This module provides multiple conversion strategies.
"""

import os
import re
import json
import tempfile
import urllib.request
import urllib.parse
import subprocess
from pathlib import Path

import FreeCAD


class ParasolidConverter:
    """Convert Parasolid .x_t files to formats FreeCAD can read"""

    def __init__(self, input_file):
        self.input_file = input_file
        self.header = {}
        self.parse_header()

    def parse_header(self):
        """Parse the Parasolid file header"""
        try:
            with open(self.input_file, 'r', errors='ignore') as f:
                in_header = False
                for line in f:
                    if '**PART1;' in line:
                        in_header = True
                        continue
                    if '**END_OF_HEADER' in line:
                        break
                    if in_header and '=' in line:
                        key, _, value = line.partition('=')
                        self.header[key.strip()] = value.strip().rstrip(';')

            FreeCAD.Console.PrintMessage(f"Parasolid file info:\n")
            FreeCAD.Console.PrintMessage(f"  Application: {self.header.get('APPL', 'Unknown')}\n")
            FreeCAD.Console.PrintMessage(f"  Created: {self.header.get('DATE', 'Unknown')}\n")
            FreeCAD.Console.PrintMessage(f"  Format: {self.header.get('FORMAT', 'Unknown')}\n")
        except Exception as e:
            FreeCAD.Console.PrintError(f"Error parsing header: {e}\n")

    def get_source_application(self):
        """Get the application that created this file"""
        return self.header.get('APPL', 'Unknown')

    def convert_via_onshape(self, access_key, secret_key):
        """
        Convert via Onshape API
        Upload the file to Onshape, then download as STEP
        """
        import base64

        FreeCAD.Console.PrintMessage("Converting via Onshape API...\n")

        # This would require implementing the full Onshape upload/export flow
        # For now, provide instructions
        FreeCAD.Console.PrintMessage("Onshape API conversion not yet implemented.\n")
        FreeCAD.Console.PrintMessage("Please upload manually to Onshape and export as STEP.\n")
        return None

    def convert_via_freecad_occ(self):
        """
        Attempt conversion using FreeCAD's Open CASCADE
        Note: Standard OCCT doesn't support Parasolid without commercial addon
        """
        FreeCAD.Console.PrintMessage("Checking FreeCAD/OpenCASCADE Parasolid support...\n")

        try:
            import Part
            # Try direct import (will fail without Parasolid translator)
            shape = Part.read(self.input_file)
            return shape
        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Direct import failed: {e}\n")
            FreeCAD.Console.PrintMessage("OpenCASCADE Parasolid translator not available.\n")
            return None

    def convert_via_external_tool(self, tool_path=None):
        """
        Convert using external command-line tools
        Supports: CAD Exchanger CLI, OpenCASCADE draw, etc.
        """
        # Check for CAD Exchanger
        cad_exchanger_paths = [
            r"C:\Program Files\CAD Exchanger\ExchangerConv.exe",
            r"C:\Program Files (x86)\CAD Exchanger\ExchangerConv.exe",
        ]

        for path in cad_exchanger_paths:
            if os.path.exists(path):
                FreeCAD.Console.PrintMessage(f"Found CAD Exchanger at {path}\n")
                output_file = self.input_file.replace('.x_t', '.step')
                try:
                    result = subprocess.run(
                        [path, self.input_file, output_file],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    if os.path.exists(output_file):
                        FreeCAD.Console.PrintMessage(f"Converted to {output_file}\n")
                        return output_file
                except Exception as e:
                    FreeCAD.Console.PrintError(f"CAD Exchanger failed: {e}\n")

        return None

    def convert_via_online_service(self, service='cloudconvert'):
        """
        Convert using online conversion services
        Note: Requires API key for most services
        """
        FreeCAD.Console.PrintMessage(f"Online conversion via {service}...\n")

        # Would need to implement API calls to conversion services
        # Most require API keys and have usage limits

        services = {
            'cloudconvert': 'https://cloudconvert.com/x_t-to-step',
            'zamzar': 'https://www.zamzar.com/',
            'cadexchanger': 'https://cadexchanger.com/online/',
        }

        FreeCAD.Console.PrintMessage("Online converters available:\n")
        for name, url in services.items():
            FreeCAD.Console.PrintMessage(f"  {name}: {url}\n")

        return None

    def get_conversion_instructions(self):
        """
        Provide manual conversion instructions based on source application
        """
        source = self.get_source_application()

        instructions = f"""
========================================
PARASOLID CONVERSION INSTRUCTIONS
========================================

Source Application: {source}
File: {self.input_file}

"""
        if source == 'Onshape':
            instructions += """
RECOMMENDED: Re-export from Onshape as STEP

1. Open your Onshape document in a browser
2. Right-click on the Part Studio tab
3. Select "Export..."
4. Choose format: STEP
5. Click "Export"
6. Download the .step file
7. Import into FreeCAD: File -> Import

This preserves the best geometry quality.
"""
        elif 'SolidWorks' in source or 'SOLIDWORKS' in source:
            instructions += """
RECOMMENDED: Re-export from SolidWorks as STEP

1. Open the part in SolidWorks
2. File -> Save As
3. Change "Save as type" to STEP (*.step)
4. Click Save
5. Import into FreeCAD: File -> Import
"""
        else:
            instructions += """
CONVERSION OPTIONS:

1. ONLINE CONVERTER (Free):
   - Go to https://cadexchanger.com/online/
   - Upload your .x_t file
   - Download as STEP
   - Import into FreeCAD

2. CAD EXCHANGER (30-day trial):
   - Download from https://cadexchanger.com/
   - Convert locally with full quality

3. ORIGINAL APPLICATION:
   - If you have access to the CAD software that
     created this file, re-export as STEP
"""
        return instructions


def convert_parasolid_file(input_file, output_format='step'):
    """
    Main function to convert a Parasolid file

    Args:
        input_file: Path to .x_t file
        output_format: Desired output format (step, iges, brep)

    Returns:
        Path to converted file, or None if conversion failed
    """
    converter = ParasolidConverter(input_file)

    # Try different conversion methods in order of preference
    FreeCAD.Console.PrintMessage("\n" + "="*50 + "\n")
    FreeCAD.Console.PrintMessage("PARASOLID CONVERSION\n")
    FreeCAD.Console.PrintMessage("="*50 + "\n\n")

    # Method 1: External tools
    result = converter.convert_via_external_tool()
    if result:
        return result

    # Method 2: Direct FreeCAD/OCC (usually fails)
    result = converter.convert_via_freecad_occ()
    if result:
        return result

    # If all automated methods fail, provide instructions
    instructions = converter.get_conversion_instructions()
    FreeCAD.Console.PrintMessage(instructions)

    return None


# FreeCAD command for Parasolid conversion
class ParasolidConvertCommand:
    """FreeCAD command to convert Parasolid files"""

    def GetResources(self):
        return {
            'MenuText': 'Convert Parasolid (.x_t)...',
            'ToolTip': 'Convert Parasolid files to FreeCAD-compatible formats'
        }

    def Activated(self):
        from PySide2 import QtWidgets

        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Select Parasolid File",
            "",
            "Parasolid Files (*.x_t *.x_b *.xmt_txt *.xmt_bin);;All Files (*.*)"
        )

        if not filename:
            return

        result = convert_parasolid_file(filename)

        if result and os.path.exists(result):
            # Import the converted file
            import Part
            doc = FreeCAD.ActiveDocument
            if not doc:
                doc = FreeCAD.newDocument("Imported")
            Part.insert(result, doc.Name)
            FreeCAD.Console.PrintMessage(f"Imported {result}\n")
        else:
            QtWidgets.QMessageBox.information(
                None,
                "Conversion Instructions",
                "Automatic conversion not available.\n\n"
                "Please check the FreeCAD console for\n"
                "manual conversion instructions."
            )

    def IsActive(self):
        return True


# Register command
try:
    import FreeCADGui
    FreeCADGui.addCommand('Converter_Parasolid', ParasolidConvertCommand())
except:
    pass  # Running in console mode
