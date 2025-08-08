"""
Generated File Item Widget

File item with sync status highlighting and direct generated gcode editing.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QDialog
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from ...widgets.themed_widgets import ThemedLabel
from ...widgets.simple_widgets import ClickableImageLabel, PlaceholderPixmap


class GCodeEditDialog(QDialog):
    """Dialog for editing G-code with the full editor"""
    
    def __init__(self, title, content, main_window=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit {title}")
        self.setModal(True)
        self.resize(800, 600)
        self.main_window = main_window
        
        # Enable maximize/minimize buttons
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | 
                           Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | 
                           Qt.WindowCloseButtonHint)
        
        # Apply styling
        self.setStyleSheet("""
            GCodeEditDialog {
                background-color: #282a36;
                color: #ffffff;
            }
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
            QPushButton#cancel_button {
                color: #BB86FC;
                border: 2px solid #BB86FC;
            }
            QPushButton#cancel_button:hover {
                color: #9965DA;
                border: 2px solid #9965DA;
            }
        """)
        
        self.setup_ui(content)
    
    def setup_ui(self, content):
        """Setup the dialog UI"""
        from ...gcode_ide import GCodeEditor
        from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton
        
        layout = QVBoxLayout(self)
        
        # G-code editor with $ variables from main_window
        self.editor = GCodeEditor(self)
        if self.main_window:
            dollar_vars = self.main_window.get_dollar_variable()
            self.editor.set_dollar_variables_info(dollar_vars)
        
        self.editor.setPlainText(content)
        layout.addWidget(self.editor)
        
        # Buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("cancel_button")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        button_layout.addWidget(save_button)
    
    def get_content(self):
        """Get the edited content"""
        return self.editor.toPlainText()


class GeneratedFileItem(QFrame):
    """File item with sync status highlighting and content management"""
    
    content_changed = Signal(str)  # Emits new content when edited
    
    def __init__(self, name, file_type, side, main_window=None, parent=None):
        super().__init__(parent)
        self.name = name
        self.file_type = file_type  # 'frame', 'lock', 'hinge'
        self.side = side  # 'left', 'right'
        self.main_window = main_window
        
        # Current content and sync status
        self.content = ""
        self.is_synced = True  # True = green (synced), False = red (out of sync)
        
        self.setFixedSize(140, 100)
        self.setCursor(Qt.PointingHandCursor)
        
        # MARK: - UI Setup
        self.setup_ui()
        self.update_visual_state()
    
    # MARK: - UI Setup
    
    def setup_ui(self):
        """Setup the widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Icon area
        self.icon_label = ClickableImageLabel((60, 60))
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setScaledContents(True)
        self.update_icon()
        layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        
        # Name label
        self.name_label = ThemedLabel(self.name)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setFont(QFont("Arial", 9, QFont.Bold))
        layout.addWidget(self.name_label)
    
    def update_icon(self):
        """Update the icon based on file type"""
        # Different icons for different file types
        if self.file_type == 'frame':
            icon = "🔲"
        elif self.file_type == 'lock':
            icon = "🔒"
        elif self.file_type == 'hinge':
            icon = "🔗"
        else:
            icon = "📄"
        
        pixmap = PlaceholderPixmap.create((60, 60), icon, "#44475c", "#bdbdc0")
        self.icon_label.setPixmap(pixmap)
    
    # MARK: - Content Management
    
    def update_content(self, content):
        """Update the content and visual state"""
        self.content = content
        self.update_visual_state()
    
    def get_content(self):
        """Get the current content"""
        return self.content
    
    def has_content(self):
        """Check if file has any content"""
        return bool(self.content and self.content.strip())
    
    # MARK: - Sync Status Management
    
    def set_sync_status(self, is_synced):
        """Set sync status and update visual state"""
        self.is_synced = is_synced
        self.update_visual_state()
    
    def update_visual_state(self):
        """Update visual state based on content and sync status"""
        has_content = self.has_content()
        
        if not has_content:
            # No content - gray border
            border_color = "#6f779a"
            bg_color = "#44475c"
        elif self.is_synced:
            # Has content and synced - green border
            border_color = "#23c87b"
            bg_color = "#1f2d20"
        else:
            # Has content but out of sync - red border
            border_color = "#ff4444"
            bg_color = "#2d1f1f"
        
        self.setStyleSheet(f"""
            GeneratedFileItem {{
                background-color: {bg_color};
                border: 3px solid {border_color};
                border-radius: 6px;
            }}
            GeneratedFileItem:hover {{
                background-color: #3a3d4d;
                border: 3px solid #BB86FC;
            }}
        """)
    
    # MARK: - Event Handling
    
    def mousePressEvent(self, event):
        """Handle click to open editor"""
        if event.button() == Qt.LeftButton:
            self.open_editor()
    
    def open_editor(self):
        """Open G-code editor dialog"""
        dialog = GCodeEditDialog(
            f"{self.side.title()} {self.name}", 
            self.content, 
            self.main_window,
            self
        )
        
        if dialog.exec_() == QDialog.Accepted:
            new_content = dialog.get_content()
            self.content = new_content
            self.update_visual_state()
            self.content_changed.emit(new_content)