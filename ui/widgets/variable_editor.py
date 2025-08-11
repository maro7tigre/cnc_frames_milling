"""
Variable Editor Widget

Resizable L variable editor for profile editing.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
from .themed_widgets import ThemedLabel, ThemedScrollArea, ThemedLineEdit
import re


class VariableEditor(QWidget):
    """Resizable L variable editor"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.variables = {}  # var_name -> line_edit
        
        self.setup_ui()
        self.apply_styling()
    
    def apply_styling(self):
        """Apply Python-based styling"""
        self.setStyleSheet("""
            VariableEditor {
                background-color: #282a36;
                color: #ffffff;
            }
        """)
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        self.title_label = ThemedLabel("Variables (L)")
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
        self.vars_layout = QVBoxLayout(container)
        self.vars_layout.setSpacing(5)
        self.vars_layout.setContentsMargins(5, 5, 5, 5)
        
        scroll.setWidget(container)
        layout.addWidget(scroll, 1)
    
    def _sort_l_variables(self, var_names):
        """Sort L variables numerically (L1, L2, L3, L10, L23, L150)"""
        def extract_number(var_name):
            # Extract the number from L variable name (e.g., "L10" -> 10)
            match = re.match(r'L(\d+)', var_name)
            return int(match.group(1)) if match else 0
        
        return sorted(var_names, key=extract_number)
    
    def update_variables(self, gcode):
        """Extract L variables from gcode and update UI"""
        # Clear existing
        while self.vars_layout.count():
            item = self.vars_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.variables.clear()
        
        # Find L variables {L1} or {L1:default}
        pattern = r'\{(L\d+)(?::([^}]+))?\}'
        matches = re.findall(pattern, gcode)
        
        # Create unique variables
        unique_vars = {}
        for var_name, default in matches:
            if var_name not in unique_vars:
                unique_vars[var_name] = default
        
        # Create editors - FIXED: Sort numerically instead of alphabetically
        for var_name in self._sort_l_variables(unique_vars.keys()):
            default = unique_vars[var_name]
            
            # Variable widget
            var_widget = QWidget()
            var_layout = QHBoxLayout(var_widget)
            var_layout.setContentsMargins(0, 0, 0, 0)
            
            # Label
            label = ThemedLabel(f"{var_name}:")
            label.setFixedWidth(60)
            var_layout.addWidget(label)
            
            # Line edit
            line_edit = ThemedLineEdit()
            if default:
                line_edit.setText(default)
            line_edit.setPlaceholderText("Enter value...")
            var_layout.addWidget(line_edit)
            
            self.vars_layout.addWidget(var_widget)
            self.variables[var_name] = line_edit
        
        # Add stretch
        self.vars_layout.addStretch()
        
        # Update visibility
        self.setVisible(len(self.variables) > 0)
    
    def get_variable_values(self):
        """Get all variable values as dictionary"""
        values = {}
        for var_name, line_edit in self.variables.items():
            values[var_name] = line_edit.text()
        return values
    
    def set_variable_values(self, values):
        """Set variable values"""
        for var_name, value in values.items():
            if var_name in self.variables:
                self.variables[var_name].setText(str(value))