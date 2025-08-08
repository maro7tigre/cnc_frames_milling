"""
Profile Grid Widget

Simplified scrollable grid for profile management with clear UI/functionality separation.
"""

from PySide6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QGridLayout, QDialog
from PySide6.QtCore import Signal, Qt
from ...widgets.themed_widgets import ThemedLabel
from .profile_item import ProfileItem


class ProfileGrid(QScrollArea):
    """Profile grid with clear separation of UI and functionality"""
    
    # MARK: - Signals
    profile_selected = Signal(str, str)  # (profile_type, profile_name)
    profile_deleted = Signal(str, str)   # (profile_type, profile_name)
    
    def __init__(self, profile_name, dialog_class, parent=None):
        super().__init__(parent)
        
        # MARK: - Properties
        self.profile_name = profile_name  # "hinge" or "lock"
        self.dialog_class = dialog_class  # ProfileEditor class
        self.profile_items = {}  # name -> ProfileItem widget
        self.profiles_data = {}  # name -> profile data
        self.selected_profile = None
        
        # MARK: - UI Setup
        self.setup_ui()
        
    # MARK: - UI Setup
    def setup_ui(self):
        """Setup the grid UI"""
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setStyleSheet("""
            ProfileGrid {
                background-color: #282a36;
                border: 1px solid #44475c;
                border-radius: 4px;
            }
            ProfileGrid QScrollBar:vertical {
                background-color: #1d1f28;
                width: 12px;
                margin: 0px;
            }
            ProfileGrid QScrollBar::handle:vertical {
                background-color: #6f779a;
                min-height: 20px;
                border-radius: 6px;
            }
            ProfileGrid QScrollBar::add-line:vertical, ProfileGrid QScrollBar::sub-line:vertical {
                height: 0px;
            }
            ProfileGrid QScrollBar:horizontal {
                background-color: #1d1f28;
                height: 12px;
                margin: 0px;
            }
            ProfileGrid QScrollBar::handle:horizontal {
                background-color: #6f779a;
                min-width: 20px;
                border-radius: 6px;
            }
            ProfileGrid QScrollBar::add-line:horizontal, ProfileGrid QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        
        # Container widget
        container = QWidget()
        container.setStyleSheet("QWidget { background-color: #282a36; }")
        self.setWidget(container)
        
        # Main layout
        main_layout = QVBoxLayout(container)
        
        # Title
        title = ThemedLabel(f"{self.profile_name.capitalize()} Profiles")
        title.setStyleSheet("""
            QLabel {
                font-size: 16px; 
                font-weight: bold; 
                padding: 10px; 
            }
        """)
        main_layout.addWidget(title)
        
        # Grid layout for items
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        main_layout.addLayout(self.grid_layout)
        main_layout.addStretch()
        
        # Add initial "+" button
        self.add_plus_button()
    
    def add_plus_button(self):
        """Add the '+' button for creating new profiles"""
        add_item = ProfileItem("Add", is_add_button=True)
        add_item.clicked.connect(self.create_new_profile)
        self.grid_layout.addWidget(add_item, 0, 0)
    
    # MARK: - Update Methods
    def update_profiles(self, profiles_dict, selected_name=None):
        """Update grid with profiles dictionary and selected profile"""
        # Store data
        self.profiles_data = profiles_dict.copy()
        self.selected_profile = selected_name
        
        # Clear existing profile items (keep + button)
        for item in list(self.profile_items.values()):
            item.deleteLater()
        self.profile_items.clear()
        
        # Add profiles
        row, col = 0, 1  # Start after + button
        for profile_name, profile_data in profiles_dict.items():
            self.add_profile_item(profile_name, profile_data, row, col)
            col += 1
            if col > self.get_columns_count():
                col = 0
                row += 1
        
        # Update selection states
        self.update_selection_states()
    
    def add_profile_item(self, name, profile_data, row, col):
        """Add a single profile item to the grid"""
        item = ProfileItem(name, profile_data)
        item.clicked.connect(lambda n: self.on_profile_clicked(n))
        item.edit_requested.connect(self.edit_profile)
        item.duplicate_requested.connect(self.duplicate_profile)
        item.delete_requested.connect(self.delete_profile)
        
        self.profile_items[name] = item
        self.grid_layout.addWidget(item, row, col)
    
    def update_selection_states(self):
        """Update visual selection states of all items"""
        for name, item in self.profile_items.items():
            item.set_selected(name == self.selected_profile)
    
    # MARK: - Event Handlers
    def on_profile_clicked(self, name):
        """Handle profile selection"""
        if name == "Add":
            return
        
        self.selected_profile = name
        self.update_selection_states()
        self.profile_selected.emit(self.profile_name, name)
    
    def create_new_profile(self):
        """Create new profile using dialog"""
        dialog = self.dialog_class(self.profile_name, parent=self)
        dialog.exec_()
    
    def edit_profile(self, name):
        """Edit existing profile"""
        if name in self.profiles_data:
            profile_data = self.profiles_data[name].copy()
            dialog = self.dialog_class(self.profile_name, profile_data, parent=self)
            dialog.exec_()
    
    def duplicate_profile(self, name):
        """Duplicate existing profile with unique name"""
        if name not in self.profiles_data:
            return
        
        # Find unique name
        base_name = f"{name} Copy"
        new_name = base_name
        counter = 1
        while new_name in self.profiles_data:
            new_name = f"{base_name} {counter}"
            counter += 1
        
        # Create copy with new name
        profile_data = self.profiles_data[name].copy()
        profile_data["name"] = new_name
        
        dialog = self.dialog_class(self.profile_name, profile_data, parent=self)
        dialog.exec_()
    
    def delete_profile(self, name):
        """Delete profile after confirmation"""
        from PySide6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(self, "Delete Profile", 
                                   f"Are you sure you want to delete '{name}'?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.profile_deleted.emit(self.profile_name, name)
    
    # MARK: - Utility Methods
    def get_columns_count(self):
        """Calculate number of columns based on current width"""
        item_width = 130  # ProfileItem width + spacing
        available_width = self.viewport().width()
        return max(1, available_width // item_width)
    
    def resizeEvent(self, event):
        """Handle resize to rearrange grid"""
        super().resizeEvent(event)
        self.rearrange_grid()
    
    def rearrange_grid(self):
        """Rearrange grid items based on current width"""
        columns = self.get_columns_count()
        
        # Get all widgets
        widgets = []
        for i in range(self.grid_layout.count()):
            item = self.grid_layout.itemAt(i)
            if item and item.widget():
                widgets.append(item.widget())
        
        # Clear grid
        while self.grid_layout.count():
            self.grid_layout.takeAt(0)
        
        # Re-add widgets
        row, col = 0, 0
        for widget in widgets:
            self.grid_layout.addWidget(widget, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1