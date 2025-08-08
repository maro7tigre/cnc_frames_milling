"""
Widgets Package

Reusable widget components for the CNC Frame Wizard application.
"""

from .themed_widgets import *
from .simple_widgets import *
from .variable_editor import VariableEditor
from .custom_editor import CustomEditor
from .dollar_variable_widgets import (DollarVariableLineEdit, DollarVariableSpinBox, 
                                     DollarVariableCheckBox, DollarVariableRadioGroup)

__all__ = [
    # Themed widgets
    'PurpleButton', 'GreenButton', 'BlueButton', 'OrangeButton',
    'ThemedLineEdit', 'ThemedTextEdit', 'ThemedSpinBox', 'ThemedGroupBox',
    'ThemedScrollArea', 'ThemedSplitter', 'ThemedLabel', 'ThemedCheckBox',
    'ThemedRadioButton', 'ThemedListWidget', 'ThemedMenu',
    
    # Simple widgets
    'ClickableLabel', 'ScaledImageLabel', 'ClickableImageLabel', 'ScaledPreviewLabel',
    'ErrorLineEdit', 'PlaceholderPixmap',
    
    # Dollar variable widgets
    'DollarVariableLineEdit', 'DollarVariableSpinBox', 'DollarVariableCheckBox', 
    'DollarVariableRadioGroup',
    
    # Complex widgets
    'VariableEditor', 'CustomEditor'
]