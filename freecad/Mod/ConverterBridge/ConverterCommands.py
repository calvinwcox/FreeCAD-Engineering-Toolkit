"""
Converter Bridge Commands
Convert various file formats to FreeCAD solids
"""

import os
import json
import tempfile
import urllib.request
import urllib.parse
import base64
import FreeCAD
import FreeCADGui
import Part
import Mesh
import MeshPart
from PySide2 import QtWidgets, QtCore, QtGui


# ============================================================================
# STL TO SOLID CONVERTER
# ============================================================================

class STLToSolidCommand:
    """Convert STL mesh files to solid bodies"""

    def GetResources(self):
        return {
            'MenuText': 'STL to Solid',
            'ToolTip': 'Convert an STL mesh file to a solid body'
        }

    def Activated(self):
        # Open file dialog
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            None,
            "Select STL File",
            "",
            "STL Files (*.stl);;OBJ Files (*.obj);;All Mesh Files (*.stl *.obj *.ply)"
        )

        if not filename:
            return

        self.convert_mesh_to_solid(filename)

    def convert_mesh_to_solid(self, filename, tolerance=0.1, sewing=True):
        """Convert a mesh file to a solid"""
        FreeCAD.Console.PrintMessage(f"Converting {filename} to solid...\n")

        doc = FreeCAD.ActiveDocument
        if not doc:
            name = os.path.splitext(os.path.basename(filename))[0]
            doc = FreeCAD.newDocument(name)

        try:
            # Import mesh
            Mesh.insert(filename, doc.Name)

            # Find the mesh object (last added)
            mesh_obj = None
            for obj in doc.Objects:
                if obj.isDerivedFrom("Mesh::Feature"):
                    mesh_obj = obj

            if not mesh_obj:
                FreeCAD.Console.PrintError("Failed to import mesh\n")
                return None

            mesh_name = mesh_obj.Name
            FreeCAD.Console.PrintMessage(f"Imported mesh: {mesh_name}\n")

            # Convert mesh to shape
            shape = Part.Shape()
            shape.makeShapeFromMesh(mesh_obj.Mesh.Topology, tolerance)

            if sewing:
                # Sew the shape to close gaps
                shape = shape.copy()
                shape.sewShape()

            # Try to make solid
            try:
                solid = Part.makeSolid(shape)
                FreeCAD.Console.PrintMessage("Successfully created solid\n")
            except:
                FreeCAD.Console.PrintWarning("Could not create solid, using shell instead\n")
                solid = shape

            # Create Part feature
            part_obj = doc.addObject("Part::Feature", mesh_name + "_Solid")
            part_obj.Shape = solid

            # Optionally remove original mesh
            # doc.removeObject(mesh_name)

            doc.recompute()

            # Report statistics
            if hasattr(solid, 'Volume'):
                FreeCAD.Console.PrintMessage(f"Volume: {solid.Volume:.2f} mm³\n")
            if hasattr(solid, 'Area'):
                FreeCAD.Console.PrintMessage(f"Surface Area: {solid.Area:.2f} mm²\n")

            FreeCAD.Console.PrintMessage("Conversion complete!\n")
            return part_obj

        except Exception as e:
            FreeCAD.Console.PrintError(f"Conversion failed: {e}\n")
            return None

    def IsActive(self):
        return True


class STLToSolidAdvancedCommand:
    """Advanced STL to solid with options dialog"""

    def GetResources(self):
        return {
            'MenuText': 'STL to Solid (Advanced)...',
            'ToolTip': 'Convert STL with advanced options for tolerance and repair'
        }

    def Activated(self):
        dialog = STLConversionDialog()
        dialog.exec_()

    def IsActive(self):
        return True


class STLConversionDialog(QtWidgets.QDialog):
    """Dialog for advanced STL conversion options"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("STL to Solid Conversion")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # File selection
        file_layout = QtWidgets.QHBoxLayout()
        self.file_edit = QtWidgets.QLineEdit()
        self.file_edit.setPlaceholderText("Select STL file...")
        browse_btn = QtWidgets.QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(browse_btn)
        layout.addLayout(file_layout)

        # Options group
        options_group = QtWidgets.QGroupBox("Conversion Options")
        options_layout = QtWidgets.QFormLayout(options_group)

        self.tolerance_spin = QtWidgets.QDoubleSpinBox()
        self.tolerance_spin.setRange(0.001, 10.0)
        self.tolerance_spin.setValue(0.1)
        self.tolerance_spin.setDecimals(3)
        options_layout.addRow("Tolerance (mm):", self.tolerance_spin)

        self.sewing_check = QtWidgets.QCheckBox("Sew shape (repair gaps)")
        self.sewing_check.setChecked(True)
        options_layout.addRow(self.sewing_check)

        self.refine_check = QtWidgets.QCheckBox("Refine shape (merge faces)")
        self.refine_check.setChecked(True)
        options_layout.addRow(self.refine_check)

        self.remove_mesh_check = QtWidgets.QCheckBox("Remove original mesh after conversion")
        self.remove_mesh_check.setChecked(False)
        options_layout.addRow(self.remove_mesh_check)

        layout.addWidget(options_group)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        convert_btn = QtWidgets.QPushButton("Convert")
        convert_btn.clicked.connect(self.do_convert)
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(convert_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

    def browse_file(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select STL File",
            "",
            "STL Files (*.stl);;OBJ Files (*.obj);;All Mesh Files (*.stl *.obj *.ply)"
        )
        if filename:
            self.file_edit.setText(filename)

    def do_convert(self):
        filename = self.file_edit.text()
        if not filename or not os.path.exists(filename):
            QtWidgets.QMessageBox.warning(self, "Error", "Please select a valid file")
            return

        tolerance = self.tolerance_spin.value()
        sewing = self.sewing_check.isChecked()

        # Do conversion
        converter = STLToSolidCommand()
        result = converter.convert_mesh_to_solid(filename, tolerance, sewing)

        if result and self.refine_check.isChecked():
            # Refine the shape
            try:
                doc = FreeCAD.ActiveDocument
                refined = doc.addObject("Part::Refine", result.Name + "_Refined")
                refined.Source = result
                doc.recompute()
            except Exception as e:
                FreeCAD.Console.PrintWarning(f"Refine failed: {e}\n")

        self.accept()


# ============================================================================
# ONSHAPE IMPORTER
# ============================================================================

class OnshapeImportCommand:
    """Import parts from Onshape via API"""

    def GetResources(self):
        return {
            'MenuText': 'Import from Onshape...',
            'ToolTip': 'Download and import parts from Onshape using their API'
        }

    def Activated(self):
        dialog = OnshapeImportDialog()
        dialog.exec_()

    def IsActive(self):
        return True


class OnshapeImportDialog(QtWidgets.QDialog):
    """Dialog for Onshape import"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import from Onshape")
        self.setMinimumWidth(500)
        self.setup_ui()
        self.load_credentials()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Instructions
        instructions = QtWidgets.QLabel(
            "To import from Onshape, you need API keys from:\n"
            "https://dev-portal.onshape.com/keys\n\n"
            "Paste your document URL or enter document/workspace/element IDs."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Credentials group
        cred_group = QtWidgets.QGroupBox("API Credentials")
        cred_layout = QtWidgets.QFormLayout(cred_group)

        self.access_key_edit = QtWidgets.QLineEdit()
        self.access_key_edit.setPlaceholderText("Access Key")
        cred_layout.addRow("Access Key:", self.access_key_edit)

        self.secret_key_edit = QtWidgets.QLineEdit()
        self.secret_key_edit.setPlaceholderText("Secret Key")
        self.secret_key_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        cred_layout.addRow("Secret Key:", self.secret_key_edit)

        self.save_creds_check = QtWidgets.QCheckBox("Save credentials locally")
        self.save_creds_check.setChecked(True)
        cred_layout.addRow(self.save_creds_check)

        layout.addWidget(cred_group)

        # Document group
        doc_group = QtWidgets.QGroupBox("Onshape Document")
        doc_layout = QtWidgets.QFormLayout(doc_group)

        self.url_edit = QtWidgets.QLineEdit()
        self.url_edit.setPlaceholderText("https://cad.onshape.com/documents/...")
        self.url_edit.textChanged.connect(self.parse_url)
        doc_layout.addRow("Document URL:", self.url_edit)

        self.doc_id_edit = QtWidgets.QLineEdit()
        self.doc_id_edit.setPlaceholderText("Document ID (auto-filled from URL)")
        doc_layout.addRow("Document ID:", self.doc_id_edit)

        self.workspace_edit = QtWidgets.QLineEdit()
        self.workspace_edit.setPlaceholderText("Workspace/Version ID")
        doc_layout.addRow("Workspace ID:", self.workspace_edit)

        self.element_edit = QtWidgets.QLineEdit()
        self.element_edit.setPlaceholderText("Element ID (Part Studio)")
        doc_layout.addRow("Element ID:", self.element_edit)

        layout.addWidget(doc_group)

        # Export options
        export_group = QtWidgets.QGroupBox("Export Options")
        export_layout = QtWidgets.QFormLayout(export_group)

        self.format_combo = QtWidgets.QComboBox()
        self.format_combo.addItems(["STEP", "STL", "Parasolid"])
        export_layout.addRow("Format:", self.format_combo)

        layout.addWidget(export_group)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        import_btn = QtWidgets.QPushButton("Import")
        import_btn.clicked.connect(self.do_import)
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(import_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

    def parse_url(self, url):
        """Parse Onshape URL to extract IDs"""
        # URL format: https://cad.onshape.com/documents/{did}/w/{wid}/e/{eid}
        try:
            if "/documents/" in url:
                parts = url.split("/documents/")[1].split("/")
                if len(parts) >= 1:
                    self.doc_id_edit.setText(parts[0])
                if len(parts) >= 3 and parts[1] in ['w', 'v']:
                    self.workspace_edit.setText(parts[2])
                if len(parts) >= 5 and parts[3] == 'e':
                    self.element_edit.setText(parts[4].split("?")[0])
        except:
            pass

    def load_credentials(self):
        """Load saved credentials"""
        cred_file = os.path.join(os.path.expanduser("~"), ".onshape_credentials.json")
        if os.path.exists(cred_file):
            try:
                with open(cred_file, 'r') as f:
                    creds = json.load(f)
                    self.access_key_edit.setText(creds.get("access_key", ""))
                    self.secret_key_edit.setText(creds.get("secret_key", ""))
            except:
                pass

    def save_credentials(self):
        """Save credentials to file"""
        cred_file = os.path.join(os.path.expanduser("~"), ".onshape_credentials.json")
        creds = {
            "access_key": self.access_key_edit.text(),
            "secret_key": self.secret_key_edit.text()
        }
        with open(cred_file, 'w') as f:
            json.dump(creds, f)

    def do_import(self):
        """Perform the import from Onshape"""
        access_key = self.access_key_edit.text().strip()
        secret_key = self.secret_key_edit.text().strip()
        doc_id = self.doc_id_edit.text().strip()
        workspace_id = self.workspace_edit.text().strip()
        element_id = self.element_edit.text().strip()

        if not all([access_key, secret_key, doc_id, workspace_id, element_id]):
            QtWidgets.QMessageBox.warning(self, "Error", "Please fill in all required fields")
            return

        if self.save_creds_check.isChecked():
            self.save_credentials()

        # Export format
        format_map = {"STEP": "STEP", "STL": "STL", "Parasolid": "PARASOLID"}
        export_format = format_map[self.format_combo.currentText()]

        try:
            FreeCAD.Console.PrintMessage("Requesting export from Onshape...\n")

            # Build API request
            # Onshape API endpoint for part studio export
            base_url = "https://cad.onshape.com/api/v5"
            endpoint = f"/partstudios/d/{doc_id}/w/{workspace_id}/e/{element_id}/stl"

            if export_format == "STEP":
                endpoint = f"/partstudios/d/{doc_id}/w/{workspace_id}/e/{element_id}/step"
            elif export_format == "PARASOLID":
                endpoint = f"/partstudios/d/{doc_id}/w/{workspace_id}/e/{element_id}/parasolid"

            url = base_url + endpoint

            # Create auth header (Basic auth with access:secret)
            credentials = f"{access_key}:{secret_key}"
            encoded_creds = base64.b64encode(credentials.encode()).decode()

            req = urllib.request.Request(url)
            req.add_header("Authorization", f"Basic {encoded_creds}")
            req.add_header("Accept", "application/octet-stream")

            # Download the file
            FreeCAD.Console.PrintMessage(f"Downloading from Onshape...\n")

            with urllib.request.urlopen(req, timeout=60) as response:
                data = response.read()

            # Save to temp file
            ext = ".step" if export_format == "STEP" else ".stl" if export_format == "STL" else ".x_t"
            temp_file = os.path.join(tempfile.gettempdir(), f"onshape_import{ext}")

            with open(temp_file, 'wb') as f:
                f.write(data)

            FreeCAD.Console.PrintMessage(f"Downloaded to {temp_file}\n")

            # Import into FreeCAD
            if export_format in ["STEP", "PARASOLID"]:
                Part.insert(temp_file, FreeCAD.ActiveDocument.Name if FreeCAD.ActiveDocument else "Onshape_Import")
            else:
                # STL - convert to solid
                converter = STLToSolidCommand()
                converter.convert_mesh_to_solid(temp_file)

            FreeCAD.Console.PrintMessage("Import complete!\n")
            self.accept()

        except urllib.error.HTTPError as e:
            FreeCAD.Console.PrintError(f"HTTP Error {e.code}: {e.reason}\n")
            QtWidgets.QMessageBox.critical(self, "Error", f"API Error: {e.code} {e.reason}\nCheck your credentials and document permissions.")
        except Exception as e:
            FreeCAD.Console.PrintError(f"Import failed: {e}\n")
            QtWidgets.QMessageBox.critical(self, "Error", f"Import failed: {e}")

    def IsActive(self):
        return True


# ============================================================================
# SOLIDWORKS HELPER (Limited - needs SW installed or manual conversion)
# ============================================================================

class SolidWorksImportCommand:
    """Helper for SolidWorks file import"""

    def GetResources(self):
        return {
            'MenuText': 'Import SolidWorks File...',
            'ToolTip': 'Convert and import SolidWorks files'
        }

    def Activated(self):
        dialog = SolidWorksImportDialog()
        dialog.exec_()

    def IsActive(self):
        return True


class SolidWorksImportDialog(QtWidgets.QDialog):
    """Dialog for SolidWorks import options"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import SolidWorks File")
        self.setMinimumWidth(500)
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Info label
        info = QtWidgets.QLabel(
            "<b>SolidWorks Native Format (.sldprt, .sldasm)</b><br><br>"
            "FreeCAD cannot directly read proprietary SolidWorks files.<br><br>"
            "<b>Options:</b><br>"
            "1. <b>If you have SolidWorks:</b> Export as STEP from SolidWorks, then import here<br>"
            "2. <b>eDrawings:</b> Free viewer can export to STEP (limited)<br>"
            "3. <b>Online converters:</b> CAD Exchanger, Onshape (import then export)<br><br>"
            "Select a STEP/IGES file that was exported from SolidWorks:"
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        # File selection
        file_group = QtWidgets.QGroupBox("Select Converted File")
        file_layout = QtWidgets.QHBoxLayout(file_group)

        self.file_edit = QtWidgets.QLineEdit()
        self.file_edit.setPlaceholderText("Select STEP or IGES file...")
        browse_btn = QtWidgets.QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(browse_btn)

        layout.addWidget(file_group)

        # Or drag native file
        native_group = QtWidgets.QGroupBox("Or: Check for SolidWorks Installation")
        native_layout = QtWidgets.QVBoxLayout(native_group)

        self.check_sw_btn = QtWidgets.QPushButton("Check for SolidWorks")
        self.check_sw_btn.clicked.connect(self.check_solidworks)
        native_layout.addWidget(self.check_sw_btn)

        self.sw_status = QtWidgets.QLabel("Click to check if SolidWorks is installed")
        native_layout.addWidget(self.sw_status)

        layout.addWidget(native_group)

        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        import_btn = QtWidgets.QPushButton("Import")
        import_btn.clicked.connect(self.do_import)
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(import_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

    def browse_file(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select File",
            "",
            "STEP Files (*.step *.stp);;IGES Files (*.iges *.igs);;All Files (*.*)"
        )
        if filename:
            self.file_edit.setText(filename)

    def check_solidworks(self):
        """Check if SolidWorks is installed and available for COM automation"""
        try:
            import win32com.client
            sw = win32com.client.Dispatch("SldWorks.Application")
            version = sw.RevisionNumber()
            self.sw_status.setText(f"✓ SolidWorks {version} found! You can use it to export STEP files.")
            self.sw_status.setStyleSheet("color: green;")
        except ImportError:
            self.sw_status.setText("✗ pywin32 not installed. Install with: pip install pywin32")
            self.sw_status.setStyleSheet("color: orange;")
        except Exception as e:
            self.sw_status.setText("✗ SolidWorks not found or not accessible")
            self.sw_status.setStyleSheet("color: red;")

    def do_import(self):
        filename = self.file_edit.text()
        if not filename or not os.path.exists(filename):
            QtWidgets.QMessageBox.warning(self, "Error", "Please select a valid STEP or IGES file")
            return

        try:
            doc = FreeCAD.ActiveDocument
            if not doc:
                name = os.path.splitext(os.path.basename(filename))[0]
                doc = FreeCAD.newDocument(name)

            Part.insert(filename, doc.Name)
            FreeCAD.Console.PrintMessage(f"Imported {filename}\n")
            self.accept()

        except Exception as e:
            FreeCAD.Console.PrintError(f"Import failed: {e}\n")
            QtWidgets.QMessageBox.critical(self, "Error", f"Import failed: {e}")


# ============================================================================
# BATCH CONVERTER
# ============================================================================

class BatchConvertCommand:
    """Batch convert multiple files"""

    def GetResources(self):
        return {
            'MenuText': 'Batch Convert...',
            'ToolTip': 'Convert multiple STL/OBJ files to solids at once'
        }

    def Activated(self):
        filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(
            None,
            "Select Files to Convert",
            "",
            "Mesh Files (*.stl *.obj *.ply);;All Files (*.*)"
        )

        if not filenames:
            return

        converter = STLToSolidCommand()
        success = 0
        failed = 0

        for filename in filenames:
            FreeCAD.Console.PrintMessage(f"\nConverting: {os.path.basename(filename)}\n")
            result = converter.convert_mesh_to_solid(filename)
            if result:
                success += 1
            else:
                failed += 1

        FreeCAD.Console.PrintMessage(f"\n=== Batch Complete: {success} success, {failed} failed ===\n")

    def IsActive(self):
        return True


# Register commands
FreeCADGui.addCommand('Converter_STLToSolid', STLToSolidCommand())
FreeCADGui.addCommand('Converter_STLToSolidAdvanced', STLToSolidAdvancedCommand())
FreeCADGui.addCommand('Converter_OnshapeImport', OnshapeImportCommand())
FreeCADGui.addCommand('Converter_SolidWorksImport', SolidWorksImportCommand())
FreeCADGui.addCommand('Converter_BatchConvert', BatchConvertCommand())
