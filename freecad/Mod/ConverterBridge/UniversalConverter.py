"""
Universal CAD Converter for FreeCAD
Integrates multiple conversion backends:
- FreeCAD native (STEP, IGES, BREP)
- Blender (FBX, glTF, DAE, 3DS, OBJ, PLY, USD, ABC)
- ODA File Converter (DWG, DXF)
- Online APIs (Parasolid, CATIA, ProE, NX, Inventor)
"""

import os
import sys
import subprocess
import tempfile
import shutil
import json
from pathlib import Path

import FreeCAD
import FreeCADGui
import Part
import Mesh

from PySide2 import QtWidgets, QtCore, QtGui


# ============================================================================
# CONFIGURATION
# ============================================================================

# Blender path (auto-detected or configured)
BLENDER_PATH = r"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe"

# ODA File Converter path
ODA_CONVERTER_PATH = r"C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe"

# Supported formats by converter
FORMAT_HANDLERS = {
    # FreeCAD native
    '.step': 'freecad', '.stp': 'freecad',
    '.iges': 'freecad', '.igs': 'freecad',
    '.brep': 'freecad', '.brp': 'freecad',
    '.stl': 'freecad',
    '.obj': 'freecad',  # FreeCAD can do OBJ too

    # Blender formats
    '.fbx': 'blender',
    '.gltf': 'blender', '.glb': 'blender',
    '.dae': 'blender',  # Collada
    '.3ds': 'blender',
    '.ply': 'blender',
    '.usd': 'blender', '.usda': 'blender', '.usdc': 'blender',
    '.abc': 'blender',  # Alembic
    '.svg': 'blender',
    '.x3d': 'blender',
    '.wrl': 'blender',  # VRML
    '.blend': 'blender',

    # ODA formats
    '.dwg': 'oda',
    '.dxf': 'oda',  # Can also use Blender for DXF

    # Online conversion needed
    '.x_t': 'online', '.x_b': 'online',  # Parasolid
    '.xmt_txt': 'online', '.xmt_bin': 'online',
    '.catpart': 'online', '.catproduct': 'online',  # CATIA
    '.prt': 'online',  # Pro/E, Creo, NX
    '.asm': 'online',  # Pro/E assembly
    '.sldprt': 'online', '.sldasm': 'online',  # SolidWorks
    '.ipt': 'online', '.iam': 'online',  # Inventor
    '.jt': 'online',  # JT format
    '.sat': 'online', '.sab': 'online',  # ACIS
}


# ============================================================================
# BLENDER CONVERTER
# ============================================================================

BLENDER_CONVERT_SCRIPT = '''
# Blender conversion script - run headless
import bpy
import sys
import os

# Get arguments after "--"
argv = sys.argv
argv = argv[argv.index("--") + 1:]
input_file = argv[0]
output_file = argv[1]
output_format = argv[2] if len(argv) > 2 else 'STL'

# Clear default scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Get file extension
ext = os.path.splitext(input_file)[1].lower()

# Import based on format
try:
    if ext == '.fbx':
        bpy.ops.import_scene.fbx(filepath=input_file)
    elif ext in ['.gltf', '.glb']:
        bpy.ops.import_scene.gltf(filepath=input_file)
    elif ext == '.dae':
        bpy.ops.wm.collada_import(filepath=input_file)
    elif ext == '.3ds':
        bpy.ops.import_scene.autodesk_3ds(filepath=input_file)
    elif ext == '.obj':
        bpy.ops.wm.obj_import(filepath=input_file)
    elif ext == '.ply':
        bpy.ops.wm.ply_import(filepath=input_file)
    elif ext == '.stl':
        bpy.ops.wm.stl_import(filepath=input_file)
    elif ext in ['.usd', '.usda', '.usdc']:
        bpy.ops.wm.usd_import(filepath=input_file)
    elif ext == '.abc':
        bpy.ops.wm.alembic_import(filepath=input_file)
    elif ext == '.svg':
        bpy.ops.import_curve.svg(filepath=input_file)
    elif ext == '.x3d':
        bpy.ops.import_scene.x3d(filepath=input_file)
    elif ext == '.wrl':
        bpy.ops.import_scene.x3d(filepath=input_file)
    elif ext == '.blend':
        bpy.ops.wm.open_mainfile(filepath=input_file)
    elif ext == '.dxf':
        # DXF import via io_import_dxf addon
        try:
            bpy.ops.import_scene.dxf(filepath=input_file)
        except:
            print(f"DXF import addon not available")
            sys.exit(1)
    else:
        print(f"Unsupported input format: {ext}")
        sys.exit(1)

    print(f"Imported: {input_file}")

except Exception as e:
    print(f"Import error: {e}")
    sys.exit(1)

# Export based on requested format
out_ext = os.path.splitext(output_file)[1].lower()

try:
    # Select all mesh objects
    bpy.ops.object.select_all(action='SELECT')

    if out_ext == '.stl':
        bpy.ops.wm.stl_export(filepath=output_file, export_selected_objects=False)
    elif out_ext == '.obj':
        bpy.ops.wm.obj_export(filepath=output_file)
    elif out_ext == '.ply':
        bpy.ops.wm.ply_export(filepath=output_file)
    elif out_ext in ['.gltf', '.glb']:
        bpy.ops.export_scene.gltf(filepath=output_file)
    elif out_ext == '.fbx':
        bpy.ops.export_scene.fbx(filepath=output_file)
    elif out_ext == '.dae':
        bpy.ops.wm.collada_export(filepath=output_file)
    elif out_ext in ['.usd', '.usda', '.usdc']:
        bpy.ops.wm.usd_export(filepath=output_file)
    else:
        # Default to STL
        output_file = output_file.rsplit('.', 1)[0] + '.stl'
        bpy.ops.wm.stl_export(filepath=output_file)

    print(f"Exported: {output_file}")

except Exception as e:
    print(f"Export error: {e}")
    sys.exit(1)

print("Conversion complete!")
'''


class BlenderConverter:
    """Convert files using Blender as backend"""

    def __init__(self, blender_path=BLENDER_PATH):
        self.blender_path = blender_path
        self.script_path = None
        self._create_script()

    def _create_script(self):
        """Create temporary conversion script"""
        self.script_path = os.path.join(tempfile.gettempdir(), 'blender_convert.py')
        with open(self.script_path, 'w') as f:
            f.write(BLENDER_CONVERT_SCRIPT)

    def is_available(self):
        """Check if Blender is available"""
        return os.path.exists(self.blender_path)

    def convert(self, input_file, output_format='stl'):
        """
        Convert file using Blender

        Args:
            input_file: Path to input file
            output_format: Desired output format (stl, obj, ply, etc.)

        Returns:
            Path to converted file, or None if failed
        """
        if not self.is_available():
            FreeCAD.Console.PrintError("Blender not found\n")
            return None

        # Determine output path
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = os.path.join(tempfile.gettempdir(), f"{base_name}_converted.{output_format}")

        FreeCAD.Console.PrintMessage(f"Converting via Blender: {os.path.basename(input_file)}\n")

        # Run Blender in background
        cmd = [
            self.blender_path,
            '--background',
            '--python', self.script_path,
            '--',
            input_file,
            output_file,
            output_format.upper()
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0 and os.path.exists(output_file):
                FreeCAD.Console.PrintMessage(f"Blender conversion successful\n")
                return output_file
            else:
                FreeCAD.Console.PrintError(f"Blender error: {result.stderr}\n")
                return None

        except subprocess.TimeoutExpired:
            FreeCAD.Console.PrintError("Blender conversion timed out\n")
            return None
        except Exception as e:
            FreeCAD.Console.PrintError(f"Blender conversion failed: {e}\n")
            return None


# ============================================================================
# ODA FILE CONVERTER
# ============================================================================

class ODAConverter:
    """Convert DWG/DXF files using ODA File Converter"""

    def __init__(self, oda_path=ODA_CONVERTER_PATH):
        self.oda_path = oda_path

    def is_available(self):
        """Check if ODA File Converter is available"""
        if os.path.exists(self.oda_path):
            return True
        # Try to find it
        possible_paths = [
            r"C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe",
            r"C:\Program Files (x86)\ODA\ODAFileConverter\ODAFileConverter.exe",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                self.oda_path = path
                return True
        return False

    def convert(self, input_file, output_format='dxf'):
        """
        Convert DWG/DXF using ODA File Converter

        Args:
            input_file: Path to DWG or DXF file
            output_format: 'dxf' or 'dwg'

        Returns:
            Path to converted file, or None if failed
        """
        if not self.is_available():
            FreeCAD.Console.PrintWarning("ODA File Converter not found\n")
            FreeCAD.Console.PrintMessage("Download free from: https://www.opendesign.com/guestfiles/oda_file_converter\n")
            return None

        # ODA uses directory-based conversion
        input_dir = os.path.dirname(input_file)
        output_dir = tempfile.mkdtemp(prefix='oda_convert_')

        # Determine output version
        # Format: ACAD2018, ACAD2013, ACAD2010, ACAD2007, ACAD2004, ACAD2000, ACAD14, ACAD13, ACAD12
        out_version = 'ACAD2018'
        out_type = 'DXF' if output_format.lower() == 'dxf' else 'DWG'

        FreeCAD.Console.PrintMessage(f"Converting via ODA: {os.path.basename(input_file)}\n")

        try:
            # ODA command line: ODAFileConverter "input_dir" "output_dir" version type recurse audit [filter]
            cmd = [
                self.oda_path,
                input_dir,
                output_dir,
                out_version,
                out_type,
                '0',  # Don't recurse
                '1',  # Audit
                os.path.basename(input_file)  # Filter to specific file
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            # Find output file
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = os.path.join(output_dir, f"{base_name}.{output_format.lower()}")

            if os.path.exists(output_file):
                FreeCAD.Console.PrintMessage(f"ODA conversion successful\n")
                return output_file
            else:
                FreeCAD.Console.PrintError("ODA conversion produced no output\n")
                return None

        except Exception as e:
            FreeCAD.Console.PrintError(f"ODA conversion failed: {e}\n")
            return None


# ============================================================================
# ONLINE CONVERTER (for proprietary formats)
# ============================================================================

class OnlineConverter:
    """Convert proprietary formats using online services"""

    def __init__(self):
        self.api_keys = self._load_api_keys()

    def _load_api_keys(self):
        """Load API keys from config file"""
        config_file = os.path.join(os.path.expanduser("~"), ".freecad_converter_keys.json")
        if os.path.exists(config_file):
            try:
                with open(config_file) as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _save_api_keys(self):
        """Save API keys to config file"""
        config_file = os.path.join(os.path.expanduser("~"), ".freecad_converter_keys.json")
        with open(config_file, 'w') as f:
            json.dump(self.api_keys, f)

    def get_conversion_options(self, input_ext):
        """Get available online conversion options for a format"""
        options = []

        # CloudConvert (has free tier)
        options.append({
            'name': 'CloudConvert',
            'url': 'https://cloudconvert.com/',
            'api_url': 'https://api.cloudconvert.com/v2',
            'free_tier': True,
            'formats': ['x_t', 'x_b', 'sat', 'sab', 'dwg', 'dxf', 'pdf']
        })

        # CAD Exchanger (30-day trial)
        options.append({
            'name': 'CAD Exchanger Online',
            'url': 'https://cadexchanger.com/online/',
            'manual': True,  # No API, manual upload
            'formats': ['x_t', 'x_b', 'catpart', 'prt', 'sldprt', 'ipt', 'jt', 'sat']
        })

        # Onshape (free account)
        options.append({
            'name': 'Onshape',
            'url': 'https://cad.onshape.com/',
            'api_url': 'https://cad.onshape.com/api/v5',
            'free_tier': True,
            'formats': ['x_t', 'sat', 'step', 'iges', 'sldprt', 'catpart', 'prt', 'ipt']
        })

        return options

    def show_manual_instructions(self, input_file):
        """Show instructions for manual online conversion"""
        ext = os.path.splitext(input_file)[1].lower()

        instructions = f"""
╔══════════════════════════════════════════════════════════════╗
║           ONLINE CONVERSION REQUIRED                          ║
╠══════════════════════════════════════════════════════════════╣
║                                                               ║
║  File: {os.path.basename(input_file)[:45]:<45} ║
║  Format: {ext:<52} ║
║                                                               ║
║  FREE ONLINE CONVERTERS:                                      ║
║                                                               ║
║  1. CAD Exchanger Online (Recommended)                        ║
║     https://cadexchanger.com/online/                          ║
║     - Upload your file                                        ║
║     - Download as STEP                                        ║
║                                                               ║
║  2. Onshape (Free account)                                    ║
║     https://cad.onshape.com/                                  ║
║     - Import your file                                        ║
║     - Export as STEP                                          ║
║                                                               ║
║  3. CloudConvert                                              ║
║     https://cloudconvert.com/                                 ║
║     - Supports many CAD formats                               ║
║                                                               ║
║  After conversion, use File -> Import in FreeCAD              ║
║                                                               ║
╚══════════════════════════════════════════════════════════════╝
"""
        return instructions


# ============================================================================
# UNIVERSAL CONVERTER - MAIN CLASS
# ============================================================================

class UniversalConverter:
    """
    Universal CAD file converter
    Automatically routes files to the appropriate conversion backend
    """

    def __init__(self):
        self.blender = BlenderConverter()
        self.oda = ODAConverter()
        self.online = OnlineConverter()

        # Check available backends
        self._check_backends()

    def _check_backends(self):
        """Check which conversion backends are available"""
        FreeCAD.Console.PrintMessage("\n=== Universal Converter Backends ===\n")

        FreeCAD.Console.PrintMessage(f"  FreeCAD: ✓ Always available\n")

        if self.blender.is_available():
            FreeCAD.Console.PrintMessage(f"  Blender: ✓ Found at {self.blender.blender_path}\n")
        else:
            FreeCAD.Console.PrintMessage(f"  Blender: ✗ Not found\n")

        if self.oda.is_available():
            FreeCAD.Console.PrintMessage(f"  ODA Converter: ✓ Found\n")
        else:
            FreeCAD.Console.PrintMessage(f"  ODA Converter: ✗ Not found (DWG support limited)\n")

        FreeCAD.Console.PrintMessage(f"  Online APIs: ✓ Available for proprietary formats\n\n")

    def get_supported_formats(self):
        """Get list of all supported formats"""
        formats = {
            'native': ['.step', '.stp', '.iges', '.igs', '.brep', '.brp', '.stl', '.obj'],
            'blender': ['.fbx', '.gltf', '.glb', '.dae', '.3ds', '.ply', '.usd', '.abc', '.x3d', '.wrl', '.blend'],
            'oda': ['.dwg', '.dxf'],
            'online': ['.x_t', '.x_b', '.catpart', '.catproduct', '.prt', '.sldprt', '.sldasm', '.ipt', '.iam', '.jt', '.sat']
        }
        return formats

    def get_handler(self, file_path):
        """Determine which handler to use for a file"""
        ext = os.path.splitext(file_path)[1].lower()
        return FORMAT_HANDLERS.get(ext, 'unknown')

    def convert(self, input_file, target_format='step'):
        """
        Convert a file to FreeCAD-compatible format

        Args:
            input_file: Path to input file
            target_format: Desired output format (step, stl, obj, etc.)

        Returns:
            Path to converted file, or original file if no conversion needed
        """
        if not os.path.exists(input_file):
            FreeCAD.Console.PrintError(f"File not found: {input_file}\n")
            return None

        ext = os.path.splitext(input_file)[1].lower()
        handler = self.get_handler(input_file)

        FreeCAD.Console.PrintMessage(f"\n{'='*60}\n")
        FreeCAD.Console.PrintMessage(f"UNIVERSAL CONVERTER\n")
        FreeCAD.Console.PrintMessage(f"{'='*60}\n")
        FreeCAD.Console.PrintMessage(f"Input: {os.path.basename(input_file)}\n")
        FreeCAD.Console.PrintMessage(f"Format: {ext}\n")
        FreeCAD.Console.PrintMessage(f"Handler: {handler}\n\n")

        # Route to appropriate handler
        if handler == 'freecad':
            # No conversion needed, FreeCAD can import directly
            FreeCAD.Console.PrintMessage("Direct FreeCAD import (no conversion needed)\n")
            return input_file

        elif handler == 'blender':
            if self.blender.is_available():
                # Convert via Blender to STL/OBJ, then we can convert to solid if needed
                converted = self.blender.convert(input_file, 'stl')
                if converted:
                    return converted
            FreeCAD.Console.PrintWarning("Blender conversion failed or unavailable\n")
            return None

        elif handler == 'oda':
            if self.oda.is_available():
                # Convert DWG to DXF, then FreeCAD can import
                converted = self.oda.convert(input_file, 'dxf')
                if converted:
                    return converted
            # Fallback to Blender for DXF
            if ext == '.dxf' and self.blender.is_available():
                return self.blender.convert(input_file, 'stl')
            FreeCAD.Console.PrintWarning("ODA/Blender conversion failed or unavailable\n")
            return None

        elif handler == 'online':
            # Show online conversion instructions
            instructions = self.online.show_manual_instructions(input_file)
            FreeCAD.Console.PrintMessage(instructions)
            return None

        else:
            FreeCAD.Console.PrintError(f"Unknown format: {ext}\n")
            return None

    def import_file(self, input_file, convert_to_solid=True):
        """
        Import a file into FreeCAD, converting if necessary

        Args:
            input_file: Path to input file
            convert_to_solid: If True, convert mesh to solid

        Returns:
            FreeCAD document object, or None if failed
        """
        # Convert if needed
        converted_file = self.convert(input_file)

        if not converted_file:
            return None

        # Get or create document
        doc = FreeCAD.ActiveDocument
        if not doc:
            name = os.path.splitext(os.path.basename(input_file))[0]
            name = name.replace('-', '_').replace(' ', '_')
            doc = FreeCAD.newDocument(name)

        ext = os.path.splitext(converted_file)[1].lower()

        try:
            if ext in ['.step', '.stp', '.iges', '.igs', '.brep', '.brp']:
                # Import as solid
                Part.insert(converted_file, doc.Name)
                FreeCAD.Console.PrintMessage(f"Imported as solid geometry\n")

            elif ext in ['.stl', '.obj', '.ply']:
                # Import as mesh
                Mesh.insert(converted_file, doc.Name)
                FreeCAD.Console.PrintMessage(f"Imported as mesh\n")

                # Optionally convert to solid
                if convert_to_solid:
                    FreeCAD.Console.PrintMessage("Converting mesh to solid...\n")
                    self._convert_mesh_to_solid(doc)

            elif ext == '.dxf':
                # Import DXF
                import importDXF
                importDXF.insert(converted_file, doc.Name)
                FreeCAD.Console.PrintMessage(f"Imported DXF\n")

            else:
                FreeCAD.Console.PrintWarning(f"Direct import not implemented for {ext}\n")
                return None

            doc.recompute()
            FreeCADGui.ActiveDocument.ActiveView.fitAll()

            return doc

        except Exception as e:
            FreeCAD.Console.PrintError(f"Import failed: {e}\n")
            return None

    def _convert_mesh_to_solid(self, doc):
        """Convert mesh objects in document to solids"""
        for obj in doc.Objects:
            if obj.isDerivedFrom("Mesh::Feature"):
                try:
                    # Convert mesh to shape
                    shape = Part.Shape()
                    shape.makeShapeFromMesh(obj.Mesh.Topology, 0.1)
                    shape = shape.copy()
                    shape.sewShape()

                    try:
                        solid = Part.makeSolid(shape)
                    except:
                        solid = shape

                    # Create solid object
                    solid_obj = doc.addObject("Part::Feature", obj.Name + "_Solid")
                    solid_obj.Shape = solid

                    FreeCAD.Console.PrintMessage(f"Converted {obj.Name} to solid\n")

                except Exception as e:
                    FreeCAD.Console.PrintWarning(f"Could not convert {obj.Name}: {e}\n")


# ============================================================================
# FREECAD COMMANDS
# ============================================================================

class UniversalImportCommand:
    """FreeCAD command for universal file import"""

    def GetResources(self):
        return {
            'MenuText': 'Universal Import...',
            'ToolTip': 'Import any CAD file format (auto-converts as needed)'
        }

    def Activated(self):
        # Build file filter from supported formats
        converter = UniversalConverter()
        formats = converter.get_supported_formats()

        all_formats = []
        for fmt_list in formats.values():
            all_formats.extend(fmt_list)

        filter_str = "All CAD Files ({});;".format(' '.join(['*' + f for f in all_formats]))
        filter_str += "STEP Files (*.step *.stp);;"
        filter_str += "IGES Files (*.iges *.igs);;"
        filter_str += "Mesh Files (*.stl *.obj *.ply);;"
        filter_str += "Blender/Game (*.fbx *.gltf *.glb *.dae *.3ds);;"
        filter_str += "DWG/DXF (*.dwg *.dxf);;"
        filter_str += "Proprietary CAD (*.x_t *.sldprt *.catpart *.prt *.ipt);;"
        filter_str += "All Files (*.*)"

        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Universal CAD Import",
            "",
            filter_str
        )

        if filename:
            converter.import_file(filename, convert_to_solid=True)

    def IsActive(self):
        return True


class BatchUniversalImportCommand:
    """Batch import multiple files"""

    def GetResources(self):
        return {
            'MenuText': 'Batch Universal Import...',
            'ToolTip': 'Import multiple CAD files at once'
        }

    def Activated(self):
        filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(
            None,
            "Select Files to Import",
            "",
            "All CAD Files (*.step *.stp *.iges *.igs *.stl *.obj *.fbx *.gltf *.dae *.3ds *.dwg *.dxf);;All Files (*.*)"
        )

        if filenames:
            converter = UniversalConverter()
            success = 0
            failed = 0

            for filename in filenames:
                FreeCAD.Console.PrintMessage(f"\n--- Importing: {os.path.basename(filename)} ---\n")
                result = converter.import_file(filename)
                if result:
                    success += 1
                else:
                    failed += 1

            FreeCAD.Console.PrintMessage(f"\n=== Batch Import Complete: {success} success, {failed} failed ===\n")

    def IsActive(self):
        return True


class ShowSupportedFormatsCommand:
    """Show all supported formats"""

    def GetResources(self):
        return {
            'MenuText': 'Supported Formats...',
            'ToolTip': 'Show all supported CAD file formats'
        }

    def Activated(self):
        converter = UniversalConverter()
        formats = converter.get_supported_formats()

        msg = "═══════════════════════════════════════════\n"
        msg += "      SUPPORTED CAD FORMATS\n"
        msg += "═══════════════════════════════════════════\n\n"

        msg += "NATIVE (FreeCAD):\n"
        msg += "  " + ", ".join(formats['native']) + "\n\n"

        msg += "VIA BLENDER:\n"
        msg += "  " + ", ".join(formats['blender']) + "\n\n"

        msg += "VIA ODA CONVERTER:\n"
        msg += "  " + ", ".join(formats['oda']) + "\n\n"

        msg += "ONLINE CONVERSION:\n"
        msg += "  " + ", ".join(formats['online']) + "\n\n"

        msg += "═══════════════════════════════════════════\n"

        QtWidgets.QMessageBox.information(None, "Supported Formats", msg)

    def IsActive(self):
        return True


# Register commands
FreeCADGui.addCommand('Converter_UniversalImport', UniversalImportCommand())
FreeCADGui.addCommand('Converter_BatchUniversalImport', BatchUniversalImportCommand())
FreeCADGui.addCommand('Converter_ShowFormats', ShowSupportedFormatsCommand())
