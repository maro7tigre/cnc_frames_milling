"""
Themed Widgets Module

Basic styled widgets that only need color/theme changes.
All widgets follow the dark theme with purple accents.
"""

from PySide6.QtWidgets import (QPushButton, QLineEdit, QTextEdit, QSpinBox, QGroupBox,
                             QScrollArea, QSplitter, QLabel, QCheckBox, QRadioButton,
                             QListWidget, QMenu)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class PurpleButton(QPushButton):
    """Standard purple theme button - most common button type"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #1d1f28;
                color: #BB86FC;
                border: 2px solid #BB86FC;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #000000;
                color: #9965DA;
                border: 2px solid #9965DA;
            }
            QPushButton:pressed {
                background-color: #BB86FC;
                color: #1d1f28;
            }
            QPushButton:disabled {
                background-color: #1d1f28;
                color: #6f779a;
                border: 2px solid #6f779a;
            }
        """)


class GreenButton(QPushButton):
    """Green success/next buttons"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #1d1f28;
                color: #23c87b;
                border: 2px solid #23c87b;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #000000;
                color: #1a945b;
                border: 2px solid #1a945b;
            }
            QPushButton:pressed {
                background-color: #23c87b;
                color: #1d1f28;
            }
            QPushButton:disabled {
                background-color: #1d1f28;
                color: #6f779a;
                border: 2px solid #6f779a;
            }
        """)


class BlueButton(QPushButton):
    """Blue project buttons"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #1d1f28;
                color: #00c4fe;
                border: 2px solid #00c4fe;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #000000;
                color: #0099cc;
                border: 2px solid #0099cc;
            }
            QPushButton:pressed {
                background-color: #00c4fe;
                color: #1d1f28;
            }
        """)


class OrangeButton(QPushButton):
    """Orange export buttons"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #1d1f28;
                color: #ff8c00;
                border: 2px solid #ff8c00;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #000000;
                color: #e67300;
                border: 2px solid #e67300;
            }
            QPushButton:pressed {
                background-color: #ff8c00;
                color: #1d1f28;
            }
        """)


class ThemedLineEdit(QLineEdit):
    """Dark themed line edit with focus states"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #1d1f28;
                color: #ffffff;
                border: 1px solid #6f779a;
                border-radius: 4px;
                padding: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #BB86FC;
            }
            QLineEdit:disabled {
                background-color: #0d0f18;
                color: #6f779a;
            }
        """)


class ThemedTextEdit(QTextEdit):
    """Dark themed text edit"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1d1f28;
                color: #ffffff;
                border: 1px solid #6f779a;
                border-radius: 4px;
                padding: 4px;
            }
            QTextEdit:focus {
                border: 1px solid #BB86FC;
            }
        """)


class ThemedSpinBox(QSpinBox):
    """Dark themed spin box with custom arrows"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QSpinBox {
                background-color: #1d1f28;
                color: #ffffff;
                border: 1px solid #6f779a;
                border-radius: 4px;
                padding: 4px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #44475c;
                border: none;
                width: 16px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #6f779a;
            }
        """)


class ThemedGroupBox(QGroupBox):
    """Dark themed group box with border"""
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setStyleSheet("""
            QGroupBox {
                border: 2px solid #44475c;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #ffffff;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)


class ThemedScrollArea(QScrollArea):
    """Dark themed scroll area with custom scrollbars"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QScrollArea {
                background-color: #1d1f28;
                border: 1px solid #6f779a;
                border-radius: 4px;
            }
            QScrollArea QScrollBar:vertical {
                background-color: #1d1f28;
                width: 12px;
                margin: 0px;
            }
            QScrollArea QScrollBar::handle:vertical {
                background-color: #6f779a;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollArea QScrollBar::add-line:vertical, QScrollArea QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollArea QScrollBar:horizontal {
                background-color: #1d1f28;
                height: 12px;
                margin: 0px;
            }
            QScrollArea QScrollBar::handle:horizontal {
                background-color: #6f779a;
                min-width: 20px;
                border-radius: 6px;
            }
            QScrollArea QScrollBar::add-line:horizontal, QScrollArea QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)


class ThemedSplitter(QSplitter):
    """Custom splitter handles"""
    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setStyleSheet("""
            QSplitter::handle {
                background-color: #44475c;
                width: 4px;
            }
            QSplitter::handle:horizontal {
                width: 4px;
            }
            QSplitter::handle:vertical {
                height: 4px;
            }
            QSplitter::handle:hover {
                background-color: #BB86FC;
            }
        """)


class ThemedLabel(QLabel):
    """White text labels"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
        """)


class ThemedCheckBox(QCheckBox):
    """Custom checkbox with purple accent"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QCheckBox {
                color: #ffffff;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #6f779a;
                background-color: #1d1f28;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #23c87b;
                border-color: #23c87b;
            }
        """)


class ThemedRadioButton(QRadioButton):
    """Custom radio button with purple accent"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QRadioButton {
                color: #ffffff;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #6f779a;
                background-color: #1d1f28;
                border-radius: 8px;
            }
            QRadioButton::indicator:checked {
                background-color: #23c87b;
                border-color: #23c87b;
            }
        """)


class ThemedListWidget(QListWidget):
    """Dark themed list widget"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QListWidget {
                background-color: #1d1f28;
                color: #ffffff;
                border: 1px solid #6f779a;
                border-radius: 4px;
                padding: 4px;
                outline: none;
            }
            QListWidget::item {
                background-color: #44475c;
                border: 1px solid #6f779a;
                border-radius: 3px;
                padding: 6px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: #BB86FC;
                color: #1d1f28;
                border: 1px solid #BB86FC;
            }
            QListWidget::item:hover {
                background-color: #6f779a;
                border: 1px solid #8b95c0;
            }
        """)


class ThemedMenu(QMenu):
    """Dark themed context menu"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QMenu {
                background-color: #1d1f28;
                color: #ffffff;
                border: 1px solid #6f779a;
                border-radius: 4px;
            }
            QMenu::item {
                background-color: transparent;
                padding: 6px 16px;
            }
            QMenu::item:selected {
                background-color: #6f779a;
            }
        """)