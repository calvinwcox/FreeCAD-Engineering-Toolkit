"""
Claude Console Panel - Embedded terminal for FreeCAD
Allows running Claude Code directly within FreeCAD's interface
"""

import os
import sys
from PySide2 import QtCore, QtGui, QtWidgets

import FreeCAD
import FreeCADGui

# Global reference to the console panel
_console_panel = None


class TerminalWidget(QtWidgets.QWidget):
    """A terminal widget that runs PowerShell/cmd with Claude Code support"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.process = None
        self.history = []
        self.history_index = 0

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        # Toolbar
        toolbar = QtWidgets.QHBoxLayout()

        self.shell_combo = QtWidgets.QComboBox()
        self.shell_combo.addItems(["PowerShell", "CMD", "Claude Code"])
        self.shell_combo.setCurrentIndex(0)
        self.shell_combo.currentIndexChanged.connect(self.restart_shell)
        toolbar.addWidget(QtWidgets.QLabel("Shell:"))
        toolbar.addWidget(self.shell_combo)

        toolbar.addStretch()

        clear_btn = QtWidgets.QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_output)
        toolbar.addWidget(clear_btn)

        restart_btn = QtWidgets.QPushButton("Restart")
        restart_btn.clicked.connect(self.restart_shell)
        toolbar.addWidget(restart_btn)

        layout.addLayout(toolbar)

        # Output display
        self.output = QtWidgets.QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QtGui.QFont("Consolas", 10))
        self.output.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #333;
            }
        """)
        layout.addWidget(self.output, stretch=1)

        # Input line
        input_layout = QtWidgets.QHBoxLayout()

        self.prompt_label = QtWidgets.QLabel("PS>")
        self.prompt_label.setStyleSheet("color: #569cd6; font-family: Consolas;")
        input_layout.addWidget(self.prompt_label)

        self.input_line = QtWidgets.QLineEdit()
        self.input_line.setFont(QtGui.QFont("Consolas", 10))
        self.input_line.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #333;
                padding: 4px;
            }
        """)
        self.input_line.returnPressed.connect(self.execute_command)
        self.input_line.installEventFilter(self)
        input_layout.addWidget(self.input_line, stretch=1)

        layout.addLayout(input_layout)

        # Start the shell
        self.start_shell()

    def eventFilter(self, obj, event):
        """Handle up/down arrow keys for command history"""
        if obj == self.input_line and event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Up:
                if self.history and self.history_index > 0:
                    self.history_index -= 1
                    self.input_line.setText(self.history[self.history_index])
                return True
            elif event.key() == QtCore.Qt.Key_Down:
                if self.history_index < len(self.history) - 1:
                    self.history_index += 1
                    self.input_line.setText(self.history[self.history_index])
                elif self.history_index == len(self.history) - 1:
                    self.history_index = len(self.history)
                    self.input_line.clear()
                return True
        return super().eventFilter(obj, event)

    def start_shell(self):
        """Start the shell process"""
        if self.process:
            self.process.kill()
            self.process.waitForFinished()

        self.process = QtCore.QProcess(self)
        self.process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.finished.connect(self.on_process_finished)

        shell_type = self.shell_combo.currentText()

        if shell_type == "PowerShell":
            self.process.start("powershell.exe", ["-NoLogo", "-NoExit", "-Command", "-"])
            self.prompt_label.setText("PS>")
        elif shell_type == "CMD":
            self.process.start("cmd.exe", ["/K"])
            self.prompt_label.setText(">")
        elif shell_type == "Claude Code":
            # Start PowerShell, then we'll run claude in it
            self.process.start("powershell.exe", ["-NoLogo", "-NoExit", "-Command", "-"])
            self.prompt_label.setText("Claude>")
            # Auto-start claude after shell is ready
            QtCore.QTimer.singleShot(500, lambda: self.send_command("claude"))

        self.append_output(f"[Starting {shell_type}...]\n")

    def restart_shell(self):
        """Restart the shell with current selection"""
        self.start_shell()

    def send_command(self, cmd):
        """Send a command to the shell process"""
        if self.process and self.process.state() == QtCore.QProcess.Running:
            self.process.write((cmd + "\n").encode())

    def execute_command(self):
        """Execute the command from input line"""
        cmd = self.input_line.text().strip()
        if not cmd:
            return

        # Add to history
        self.history.append(cmd)
        self.history_index = len(self.history)

        # Echo command
        shell_type = self.shell_combo.currentText()
        prompt = "PS>" if shell_type == "PowerShell" else ">" if shell_type == "CMD" else "Claude>"
        self.append_output(f"{prompt} {cmd}\n")

        # Send to process
        self.send_command(cmd)
        self.input_line.clear()

    def read_output(self):
        """Read output from the shell process"""
        if self.process:
            data = self.process.readAllStandardOutput().data()
            try:
                text = data.decode('utf-8', errors='replace')
            except:
                text = data.decode('cp1252', errors='replace')
            self.append_output(text)

    def append_output(self, text):
        """Append text to the output display"""
        self.output.moveCursor(QtGui.QTextCursor.End)
        self.output.insertPlainText(text)
        self.output.moveCursor(QtGui.QTextCursor.End)
        self.output.ensureCursorVisible()

    def clear_output(self):
        """Clear the output display"""
        self.output.clear()

    def on_process_finished(self, exit_code, exit_status):
        """Handle process termination"""
        self.append_output(f"\n[Process exited with code {exit_code}]\n")


class ClaudeConsoleDockWidget(QtWidgets.QDockWidget):
    """Dock widget containing the Claude Console"""

    def __init__(self, parent=None):
        super().__init__("Claude Console", parent)
        self.setObjectName("ClaudeConsoleDock")

        self.terminal = TerminalWidget()
        self.setWidget(self.terminal)

        # Allow docking on bottom or right
        self.setAllowedAreas(
            QtCore.Qt.BottomDockWidgetArea |
            QtCore.Qt.RightDockWidgetArea |
            QtCore.Qt.LeftDockWidgetArea
        )

        # Set minimum size
        self.setMinimumHeight(200)
        self.setMinimumWidth(400)


def show_console():
    """Show the Claude Console panel"""
    global _console_panel

    main_window = FreeCADGui.getMainWindow()

    if _console_panel is None:
        _console_panel = ClaudeConsoleDockWidget(main_window)
        main_window.addDockWidget(QtCore.Qt.BottomDockWidgetArea, _console_panel)

    _console_panel.show()
    _console_panel.raise_()
    return _console_panel


def hide_console():
    """Hide the Claude Console panel"""
    global _console_panel
    if _console_panel:
        _console_panel.hide()


def toggle_console():
    """Toggle the Claude Console panel visibility"""
    global _console_panel
    if _console_panel and _console_panel.isVisible():
        hide_console()
    else:
        show_console()


# FreeCAD Command classes
class ClaudeConsoleToggleCommand:
    """Command to toggle the Claude Console panel"""

    def GetResources(self):
        return {
            'Pixmap': 'terminal',
            'MenuText': 'Toggle Claude Console',
            'ToolTip': 'Show/hide the Claude Console terminal panel',
            'Shortcut': 'Ctrl+Shift+C'
        }

    def Activated(self):
        toggle_console()

    def IsActive(self):
        return True


class ClaudeConsoleClearCommand:
    """Command to clear the Claude Console output"""

    def GetResources(self):
        return {
            'MenuText': 'Clear Console',
            'ToolTip': 'Clear the Claude Console output'
        }

    def Activated(self):
        global _console_panel
        if _console_panel:
            _console_panel.terminal.clear_output()

    def IsActive(self):
        return _console_panel is not None


# Register commands
FreeCADGui.addCommand('ClaudeConsole_Toggle', ClaudeConsoleToggleCommand())
FreeCADGui.addCommand('ClaudeConsole_Clear', ClaudeConsoleClearCommand())
