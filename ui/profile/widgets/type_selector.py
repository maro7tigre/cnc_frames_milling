"""
Type Selector Widget

Horizontal scrollable type selector with selection state preservation.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QDialog, QMessageBox
from PySide6.QtCore import Signal, Qt
from ...widgets.themed_widgets import ThemedLabel, ThemedScrollArea
from .type_item import TypeItem
from ...dialogs.type_editor import TypeEditor


class TypeSelector(QWidget):
    """Type selector with selection state preservation"""
    
    # MARK: - Signals
    type_selected = Signal(dict)
    types_modified = Signal()
    
    def __init__(self, profile_type, dollar_variables_info=None, parent=None):
        super().__init__(parent)
        
        # MARK: - Properties
        self.profile_type = profile_type  # "hinge" or "lock"
        self.dollar_variables_info = dollar_variables_info or {}
        self.main_window = self.find_main_window(parent)
        self.selected_type_name = None  # Store the name instead of the object
        self.types = {}  # name -> type_data
        self.type_items = {}  # name -> TypeItem widget
        
        # MARK: - UI Setup
        self.setup_ui()
    
    # MARK: - UI Setup
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = ThemedLabel(f"{self.profile_type.capitalize()} Types")
        title.setStyleSheet("QLabel { font-weight: bold; padding: 5px; }")
        layout.addWidget(title)
        
        # Scroll area
        scroll = ThemedScrollArea()
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFixedHeight(150)
        scroll.setWidgetResizable(True)
        
        # Container
        container = QWidget()
        container.setStyleSheet("QWidget { background-color: #1d1f28; }")
        self.items_layout = QHBoxLayout(container)
        self.items_layout.setSpacing(10)
        self.items_layout.setContentsMargins(5, 5, 5, 5)
        
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
        # Add initial "+" button
        self.add_type_button()
    
    def add_type_button(self):
        """Add the '+' button"""
        add_item = TypeItem("Add", is_add_button=True)
        add_item.clicked.connect(self.add_new_type)
        self.items_layout.insertWidget(0, add_item)
    
    # MARK: - Data Management
    def load_types(self, types_data):
        """Load types from data and preserve selection"""
        # Remember current selection
        previously_selected = self.selected_type_name
        
        # Clear existing (except add button)
        for item in list(self.type_items.values()):
            item.deleteLater()
        self.type_items.clear()
        self.types.clear()
        
        # Add types
        for type_name, type_data in types_data.items():
            self.add_type_item(type_data)
        
        # Restore selection if the type still exists
        if previously_selected and previously_selected in self.types:
            self.restore_selection(previously_selected)
        else:
            # Clear selection if type no longer exists
            self.selected_type_name = None
    
    def restore_selection(self, type_name):
        """Restore selection to a specific type"""
        if type_name in self.type_items and type_name in self.types:
            self.selected_type_name = type_name
            self.type_items[type_name].set_selected(True)
            # Don't emit signal during restoration to avoid unnecessary updates
    
    def add_type_item(self, type_data):
        """Add a type item to the selector"""
        name = type_data["name"]
        
        # Create item
        item = TypeItem(name, type_data.get("image"))
        item.clicked.connect(lambda n: self.on_type_clicked(n))
        item.edit_requested.connect(self.edit_type)
        item.duplicate_requested.connect(self.duplicate_type)
        item.delete_requested.connect(self.delete_type)
        
        # Store data and widget
        self.types[name] = type_data
        self.type_items[name] = item
        
        # Add to layout (after the "+" button)
        self.items_layout.addWidget(item)
    
    def get_types_data(self):
        """Get all types data"""
        return self.types.copy()
    
    # MARK: - Event Handlers
    def on_type_clicked(self, name):
        """Handle type selection with explicit state management"""
        # Clear previous selection
        if self.selected_type_name and self.selected_type_name in self.type_items:
            self.type_items[self.selected_type_name].set_selected(False)
        
        # Set new selection
        self.selected_type_name = name
        if name in self.type_items:
            self.type_items[name].set_selected(True)
            self.type_selected.emit(self.types[name])
    
    def add_new_type(self):
        """Create new type"""
        dialog = TypeEditor(self.profile_type, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            # Refresh from main_window after dialog closes
            self.refresh_from_main_window()
            self.types_modified.emit()
    
    def edit_type(self, name):
        """Edit existing type"""
        if name in self.types:
            # Get fresh data from main_window to avoid stale data
            if self.main_window:
                if self.profile_type == "hinge":
                    current_data = self.main_window.hinges_types.get(name, {}).copy()
                else:
                    current_data = self.main_window.locks_types.get(name, {}).copy()
            else:
                current_data = self.types[name].copy()
            
            dialog = TypeEditor(self.profile_type, current_data, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                # Refresh from main_window after dialog closes
                self.refresh_from_main_window()
                self.types_modified.emit()
    
    def duplicate_type(self, name):
        """Duplicate type"""
        if name in self.types:
            # Get fresh data from main_window to avoid stale data
            if self.main_window:
                if self.profile_type == "hinge":
                    current_data = self.main_window.hinges_types.get(name, {}).copy()
                else:
                    current_data = self.main_window.locks_types.get(name, {}).copy()
            else:
                current_data = self.types[name].copy()
            
            # Find unique name - also check main_window for latest data
            if self.main_window:
                if self.profile_type == "hinge":
                    existing_names = set(self.main_window.hinges_types.keys())
                else:
                    existing_names = set(self.main_window.locks_types.keys())
            else:
                existing_names = set(self.types.keys())
            
            base_name = f"{name} Copy"
            new_name = base_name
            counter = 1
            
            while new_name in existing_names:
                new_name = f"{base_name} {counter}"
                counter += 1
            
            # Create copy with new name
            copy_data = current_data.copy()
            copy_data["name"] = new_name
            
            dialog = TypeEditor(self.profile_type, copy_data, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                # Refresh from main_window after dialog closes
                self.refresh_from_main_window()
                self.types_modified.emit()
    
    def delete_type(self, name):
        """Delete type"""
        reply = QMessageBox.question(self, "Delete Type", 
                                   f"Delete type '{name}'?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes and name in self.types and self.main_window:
            # Clear selection if deleting selected type
            if self.selected_type_name == name:
                self.selected_type_name = None
            
            # Delete from main_window
            if self.profile_type == "hinge":
                self.main_window.update_hinge_type(name, None)
            else:
                self.main_window.update_lock_type(name, None)
            
            # Refresh from main_window after deletion
            self.refresh_from_main_window()
            self.types_modified.emit()
    
    # MARK: - Main Window Integration
    def refresh_from_main_window(self):
        """Refresh types from main_window while preserving selection"""
        if not self.main_window:
            return
        
        # Get updated types from main_window
        if self.profile_type == "hinge":
            types_data = self.main_window.hinges_types
        else:
            types_data = self.main_window.locks_types
        
        self.load_types(types_data)
    
    def find_main_window(self, parent):
        """Find main_window from parent hierarchy"""
        current = parent
        while current:
            if hasattr(current, 'main_window'):
                return current.main_window
            elif hasattr(current, 'parent') and callable(current.parent):
                current = current.parent()
            else:
                break
        return None