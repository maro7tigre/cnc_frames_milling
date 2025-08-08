"""
Dollar Variable Widgets

Special widgets that automatically sync with main_window dollar variables.
"""

from PySide6.QtWidgets import QSpinBox, QCheckBox, QRadioButton, QButtonGroup
from PySide6.QtCore import Signal
from PySide6.QtGui import QDoubleValidator
from .themed_widgets import ThemedLineEdit, ThemedSpinBox, ThemedCheckBox, ThemedRadioButton


class DollarVariableLineEdit(ThemedLineEdit):
    """LineEdit that automatically syncs with a main_window dollar variable"""
    
    def __init__(self, variable_name, main_window=None, parent=None):
        super().__init__(parent=parent)
        self.variable_name = variable_name
        self.main_window = main_window
        self._updating = False  # Prevent loops
        self._is_editing = False  # Track if user is actively typing
        
        # Load initial value
        if self.main_window:
            initial_value = self.main_window.get_dollar_variable(self.variable_name)
            if initial_value is not None:
                self.setText(self._format_value(initial_value))
        
        # Connect signals - use editingFinished instead of textChanged
        self.editingFinished.connect(self._on_editing_finished)
        self.textChanged.connect(self._on_text_changing)
    
    def _format_value(self, value):
        """Format value for display, converting .0 floats to integers"""
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)
    
    def _on_text_changing(self, text):
        """Track that user is actively editing"""
        self._is_editing = True
    
    def _on_editing_finished(self):
        """Handle editing finished and update main_window"""
        if self._updating or not self.main_window:
            return
        
        self._is_editing = False
        text = self.text().strip()
        
        # Get current value from main_window
        current_value = self.main_window.get_dollar_variable(self.variable_name)
        
        # Convert text to appropriate type
        try:
            if not text:
                new_value = 0
            elif '.' in text:
                # Has decimal point - convert to float
                new_value = float(text)
                # If it's a whole number, store as int
                if new_value.is_integer():
                    new_value = int(new_value)
            else:
                # No decimal point - convert to int
                new_value = int(text)
        except ValueError:
            # Invalid input - revert to current value
            self.setText(self._format_value(current_value))
            return
        
        # Only update if value actually changed
        if new_value != current_value:
            self._updating = True
            try:
                self.main_window.update_dollar_variable(self.variable_name, new_value)
            finally:
                self._updating = False
        
        # Update display format
        self.setText(self._format_value(new_value))
    
    def update_from_main_window(self):
        """Update widget value from main_window (called during variable_updated events)"""
        if not self.main_window or self._is_editing:
            return  # Don't update while user is typing
        
        self._updating = True
        try:
            value = self.main_window.get_dollar_variable(self.variable_name)
            if value is not None:
                self.setText(self._format_value(value))
        finally:
            self._updating = False


class DollarVariableSpinBox(ThemedSpinBox):
    """SpinBox that automatically syncs with a main_window dollar variable"""
    
    def __init__(self, variable_name, main_window=None, parent=None):
        super().__init__(parent=parent)
        self.variable_name = variable_name
        self.main_window = main_window
        self._updating = False
        
        # Load initial value
        if self.main_window:
            initial_value = self.main_window.get_dollar_variable(self.variable_name)
            if initial_value is not None:
                self.setValue(int(initial_value))
        
        # Connect signal
        self.valueChanged.connect(self._on_value_changed)
    
    def _on_value_changed(self, value):
        """Handle value change and update main_window if value actually changed"""
        if self._updating or not self.main_window:
            return
        
        current_value = self.main_window.get_dollar_variable(self.variable_name)
        if value == current_value:
            return
        
        self._updating = True
        try:
            self.main_window.update_dollar_variable(self.variable_name, value)
        finally:
            self._updating = False
    
    def update_from_main_window(self):
        """Update widget value from main_window"""
        if not self.main_window:
            return
        
        self._updating = True
        try:
            value = self.main_window.get_dollar_variable(self.variable_name)
            if value is not None:
                self.setValue(int(value))
        finally:
            self._updating = False


class DollarVariableCheckBox(ThemedCheckBox):
    """CheckBox that automatically syncs with a main_window dollar variable"""
    
    def __init__(self, variable_name, text="", main_window=None, parent=None):
        super().__init__(text, parent=parent)
        self.variable_name = variable_name
        self.main_window = main_window
        self._updating = False
        
        # Load initial value
        if self.main_window:
            initial_value = self.main_window.get_dollar_variable(self.variable_name)
            if initial_value is not None:
                self.setChecked(bool(initial_value))
        
        # Connect signal
        self.stateChanged.connect(self._on_state_changed)
    
    def _on_state_changed(self, state):
        """Handle state change and update main_window if value actually changed"""
        if self._updating or not self.main_window:
            return
        
        new_value = 1 if self.isChecked() else 0
        current_value = self.main_window.get_dollar_variable(self.variable_name)
        
        if new_value == current_value:
            return
        
        self._updating = True
        try:
            self.main_window.update_dollar_variable(self.variable_name, new_value)
        finally:
            self._updating = False
    
    def update_from_main_window(self):
        """Update widget value from main_window"""
        if not self.main_window:
            return
        
        self._updating = True
        try:
            value = self.main_window.get_dollar_variable(self.variable_name)
            if value is not None:
                self.setChecked(bool(value))
        finally:
            self._updating = False


class DollarVariableRadioGroup:
    """Radio button group that syncs with a main_window dollar variable"""
    
    def __init__(self, variable_name, main_window=None):
        self.variable_name = variable_name
        self.main_window = main_window
        self.button_group = QButtonGroup()
        self.value_map = {}  # button -> value
        self._updating = False
        
        # Connect signal
        self.button_group.buttonClicked.connect(self._on_button_clicked)
    
    def add_button(self, button, value):
        """Add a radio button with its corresponding value"""
        self.button_group.addButton(button)
        self.value_map[button] = value
        
        # Check if this should be the initial selection
        if self.main_window:
            current_value = self.main_window.get_dollar_variable(self.variable_name)
            if current_value == value:
                button.setChecked(True)
    
    def _on_button_clicked(self, button):
        """Handle button click and update main_window if value actually changed"""
        if self._updating or not self.main_window:
            return
        
        new_value = self.value_map.get(button)
        if new_value is None:
            return
        
        current_value = self.main_window.get_dollar_variable(self.variable_name)
        if new_value == current_value:
            return
        
        self._updating = True
        try:
            self.main_window.update_dollar_variable(self.variable_name, new_value)
        finally:
            self._updating = False
    
    def update_from_main_window(self):
        """Update radio selection from main_window"""
        if not self.main_window:
            return
        
        self._updating = True
        try:
            current_value = self.main_window.get_dollar_variable(self.variable_name)
            for button, value in self.value_map.items():
                if value == current_value:
                    button.setChecked(True)
                    break
        finally:
            self._updating = False