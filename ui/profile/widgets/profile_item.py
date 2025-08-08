"""
Profile Item Widget

Individual profile item widget with selection states and context menus.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap
from ...widgets.themed_widgets import ThemedLabel, ThemedMenu
from ...widgets.simple_widgets import PlaceholderPixmap, ClickableImageLabel


class ProfileItem(QFrame):
    """Individual profile item widget with Python-controlled styling"""
    clicked = Signal(str)
    edit_requested = Signal(str)
    duplicate_requested = Signal(str)
    delete_requested = Signal(str)
    
    def __init__(self, name, profile_data=None, is_add_button=False, parent=None):
        super().__init__(parent)
        self.name = name
        self.profile_data = profile_data or {}
        self.is_add_button = is_add_button
        self.selected = False
        self._is_hovered = False
        
        self.setFixedSize(120, 140)
        self.setCursor(Qt.PointingHandCursor)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Image placeholder 
        self.image_label = ClickableImageLabel((100, 100))
        self.image_label.setScaledContents(True)
        
        # REMOVED: Click forwarding that was causing double clicks
        # self.image_label.clicked.connect(lambda: self.clicked.emit(self.name))
        
        # Create or load image
        self.update_image()
        
        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        
        # Name label
        self.name_label = ThemedLabel(name)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)
        
        # Set initial style
        self.update_style()
    
    def update_image(self):
        """Update the displayed image"""
        if self.is_add_button:
            # Add button placeholder
            pixmap = PlaceholderPixmap.create_add_button((100, 100))
        elif self.profile_data.get("image"):
            # Load profile image
            loaded_pixmap = QPixmap(self.profile_data["image"])
            if not loaded_pixmap.isNull():
                pixmap = loaded_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            else:
                pixmap = PlaceholderPixmap.create_file_icon((100, 100))
        else:
            # Default profile icon
            pixmap = PlaceholderPixmap.create_file_icon((100, 100))
        
        self.image_label.setPixmap(pixmap)
    
    def set_selected(self, selected):
        """Update selection state with immediate styling"""
        self.selected = selected
        self.update_style()
    
    def update_style(self):
        """Apply styling based on current state"""
        if self.selected:
            # Selected state - green theme
            self.setStyleSheet("""
                ProfileItem {
                    background-color: #1A2E20;
                    border: 3px solid #23c87b;
                    border-radius: 4px;
                }
            """)
        elif self._is_hovered:
            # Hover state
            self.setStyleSheet("""
                ProfileItem {
                    background-color: #3a3d4d;
                    border: 2px solid #8b95c0;
                    border-radius: 4px;
                }
            """)
        else:
            # Default state
            self.setStyleSheet("""
                ProfileItem {
                    background-color: #44475c;
                    border: 2px solid #6f779a;
                    border-radius: 4px;
                }
            """)
        
        # Force immediate update
        self.update()
    
    def enterEvent(self, event):
        """Handle mouse enter"""
        if not self.selected:  # Don't override selected state
            self._is_hovered = True
            self.update_style()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave"""
        self._is_hovered = False
        self.update_style()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse clicks """
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.name)
        elif event.button() == Qt.RightButton and not self.is_add_button:
            # Show context menu for non-add buttons
            self.show_context_menu(event.globalPos())
    
    def show_context_menu(self, pos):
        """Show right-click context menu"""
        menu = ThemedMenu(self)
        
        edit_action = menu.addAction("Edit")
        duplicate_action = menu.addAction("Duplicate")
        menu.addSeparator()
        delete_action = menu.addAction("Delete")
        
        action = menu.exec_(pos)
        
        if action == edit_action:
            self.edit_requested.emit(self.name)
        elif action == duplicate_action:
            self.duplicate_requested.emit(self.name)
        elif action == delete_action:
            self.delete_requested.emit(self.name)