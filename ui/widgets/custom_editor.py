"""
Custom Editor Widget

Resizable custom variable editor for profile editing.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from .themed_widgets import ThemedLabel, ThemedScrollArea, ThemedLineEdit
import re


class CustomEditor(QWidget):
    """Resizable custom variable editor"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.customs = {}  # var_name -> line_edit
        
        self.setup_ui()
        self.apply_styling()
    
    def apply_styling(self):
        """Apply Python-based styling"""
        self.setStyleSheet("""
            CustomEditor {
                background-color: #282a36;
                color: #ffffff;
            }
        """)
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        self.title_label = ThemedLabel("Custom Variables")
        self.title_label.setStyleSheet("QLabel { font-weight: bold; padding: 5px; }")
        layout.addWidget(self.title_label)
        
        # Scroll area - now resizable
        scroll = ThemedScrollArea()
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(100)  # Minimum height
        
        # Container
        container = QWidget()
        container.setStyleSheet("QWidget { background-color: #1d1f28; }")
        self.customs_layout = QVBoxLayout(container)
        self.customs_layout.setSpacing(5)
        self.customs_layout.setContentsMargins(5, 5, 5, 5)
        
        scroll.setWidget(container)
        layout.addWidget(scroll, 1)
    
    def update_customs(self, gcode):
        """Extract custom variables from gcode and update UI"""
        # Clear existing
        while self.customs_layout.count():
            item = self.customs_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.customs.clear()
        
        # Find custom variables (not L or $ variables) - parse name:default correctly
        pattern = r'\{([^L$][^:}]*?)(?::([^}]+))?\}'
        matches = re.findall(pattern, gcode)
        
        # Create unique customs
        unique_customs = {}
        for var_name, default in matches:
            if var_name not in unique_customs:
                unique_customs[var_name] = default
        
        # Create editors
        for var_name in sorted(unique_customs.keys()):
            default = unique_customs[var_name]
            
            # Custom widget
            custom_widget = QWidget()
            custom_layout = QVBoxLayout(custom_widget)
            custom_layout.setContentsMargins(0, 0, 0, 0)
            
            # Label
            label = ThemedLabel(f"{var_name}:")
            custom_layout.addWidget(label)
            
            # Line edit - supports any content including entire lines
            line_edit = ThemedLineEdit()
            if default:
                line_edit.setText(default)
            line_edit.setPlaceholderText("Enter value or entire line...")
            custom_layout.addWidget(line_edit)
            
            self.customs_layout.addWidget(custom_widget)
            self.customs[var_name] = line_edit
        
        # Add stretch
        self.customs_layout.addStretch()
        
        # Update visibility
        self.setVisible(len(self.customs) > 0)
    
    def get_custom_values(self):
        """Get all custom values as dictionary"""
        values = {}
        for var_name, line_edit in self.customs.items():
            values[var_name] = line_edit.text()
        return values
    
    def set_custom_values(self, values):
        """Set custom values"""
        for var_name, value in values.items():
            if var_name in self.customs:
                self.customs[var_name].setText(str(value))