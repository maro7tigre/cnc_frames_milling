"""
Type Item Widget

Individual type item widget with click forwarding from image to parent.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap
from ...widgets.themed_widgets import ThemedLabel, ThemedMenu
from ...widgets.simple_widgets import PlaceholderPixmap, ClickableImageLabel


class TypeItem(QFrame):
    """Individual type item widget with Python-controlled styling"""
    clicked = Signal(str)
    edit_requested = Signal(str)
    duplicate_requested = Signal(str)
    delete_requested = Signal(str)
    
    def __init__(self, name, image_path=None, is_add_button=False, parent=None):
        super().__init__(parent)
        self.name = name
        self.image_path = image_path
        self.is_add_button = is_add_button
        self.selected = False
        self._is_hovered = False
        
        self.setFixedSize(100, 120)
        self.setCursor(Qt.PointingHandCursor)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Image 
        self.image_label = ClickableImageLabel((80, 80))
        self.image_label.setScaledContents(True)
        
        # REMOVED: Click forwarding that was causing double clicks
        # self.image_label.clicked.connect(lambda: self.clicked.emit(self.name))
        
        # Load image or create placeholder
        self.update_image()
        
        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)
        
        # Name
        self.name_label = ThemedLabel(name)
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)
        
        self.update_style()
    
    def update_image(self):
        """Update displayed image"""
        if self.image_path and not self.is_add_button:
            loaded_pixmap = QPixmap(self.image_path)
            if not loaded_pixmap.isNull():
                self.image_label.setPixmap(loaded_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                return
        
        # Default placeholder
        if self.is_add_button:
            pixmap = PlaceholderPixmap.create_add_button((80, 80))
        else:
            pixmap = PlaceholderPixmap.create_type_placeholder((80, 80))
        
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
                TypeItem {
                    background-color: #1A2E20;
                    border: 3px solid #23c87b;
                    border-radius: 4px;
                }
            """)
        elif self._is_hovered:
            # Hover state
            self.setStyleSheet("""
                TypeItem {
                    background-color: #3a3d4d;
                    border: 2px solid #8b95c0;
                    border-radius: 4px;
                }
            """)
        else:
            # Default state
            self.setStyleSheet("""
                TypeItem {
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
            self.show_context_menu(event.globalPos())
    
    def show_context_menu(self, pos):
        """Show context menu"""
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