from PySide6.QtWidgets import (QWidget, QVBoxLayout, QDialog, QScrollArea, QLabel, QDialogButtonBox)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, Signal


class DollarVariablesDialog(QDialog):
    """Simplified dialog showing available $ variables in MainWindow order"""
    
    variable_selected = Signal(str)  # Emits variable name when selected
    
    def __init__(self, variables_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Available $ Variables")
        self.setModal(True)
        self.resize(600, 500)
        
        # Apply styling
        self.setStyleSheet("""
            DollarVariablesDialog {
                background-color: #282a36;
                color: #ffffff;
            }
            DollarVariablesDialog QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            DollarVariablesDialog QPushButton {
                background-color: #1d1f28;
                color: #BB86FC;
                border: 2px solid #BB86FC;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 80px;
            }
            DollarVariablesDialog QPushButton:hover {
                background-color: #000000;
                color: #9965DA;
                border: 2px solid #9965DA;
            }
            DollarVariablesDialog QPushButton:pressed {
                background-color: #BB86FC;
                color: #1d1f28;
            }
            QScrollArea {
                background-color: #1d1f28;
                border: 1px solid #6f779a;
                border-radius: 4px;
            }
        """)
        
        self.setup_ui(variables_info)
    
    def setup_ui(self, variables_info):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Available $ Variables")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel("Click on a variable to insert it into your G-code:")
        layout.addWidget(instructions)
        
        # Scroll area for variables
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll, 1)
        
        # Container for variables
        container = QWidget()
        container.setStyleSheet("QWidget { background-color: #1d1f28; }")
        container_layout = QVBoxLayout(container)
        scroll.setWidget(container)
        
        # List all variables in their original order (no sorting)
        # Python dictionaries maintain insertion order since 3.7+
        for var_name in variables_info.keys():
            value = variables_info[var_name]
            var_widget = self.create_variable_widget(var_name, value)
            container_layout.addWidget(var_widget)
        
        container_layout.addStretch()
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.accept)
        layout.addWidget(buttons)
    
    def create_variable_widget(self, var_name, value):
        """Create a clickable variable widget showing {$key} : value"""
        widget = QWidget()
        widget.setCursor(Qt.PointingHandCursor)
        widget.setStyleSheet("""
            QWidget {
                background-color: #44475c;
                border: 1px solid #6f779a;
                border-radius: 4px;
                padding: 5px;
                margin: 2px;
            }
            QWidget:hover {
                background-color: #6f779a;
                border: 1px solid #BB86FC;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 5, 8, 5)
        
        # Variable name and value - show {$key} : value
        name_label = QLabel(f"{{${var_name}}} : {value}")
        name_label.setFont(QFont("Consolas", 11, QFont.Bold))
        name_label.setStyleSheet("QLabel { color: #23c87b; }")
        layout.addWidget(name_label)
        
        # Make clickable - Emit {$var_name} when clicked
        def on_click():
            self.variable_selected.emit(f"{{${var_name}}}")
            self.accept()
        
        widget.mousePressEvent = lambda event: on_click() if event.button() == Qt.LeftButton else None
        
        return widget