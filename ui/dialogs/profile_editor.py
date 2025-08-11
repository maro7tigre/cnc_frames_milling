"""
Profile Editor Dialog

Profile editor with proper scaling type preview that maintains aspect ratio.
Now with relative path support for images within the profiles directory.
"""

from PySide6.QtWidgets import QDialog, QWidget, QHBoxLayout, QVBoxLayout, QDialogButtonBox, QMessageBox, QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import os

from ..widgets.themed_widgets import ThemedLabel, ThemedLineEdit, ThemedSplitter
from ..widgets.simple_widgets import ClickableImageLabel, PlaceholderPixmap, ScaledPreviewLabel
from ..profile.widgets.type_selector import TypeSelector
from ..widgets.variable_editor import VariableEditor
from ..widgets.custom_editor import CustomEditor


class ProfileEditor(QDialog):
    """Profile editor with proper scaling preview that maintains aspect ratio"""
    
    def __init__(self, profile_type, profile_data=None, parent=None):
        super().__init__(parent)
        
        # MARK: - Properties
        self.profile_type = profile_type  # "hinge" or "lock"
        self.profile_data = profile_data or {}
        self.main_window = self.find_main_window(parent)
        self.current_type = None
        self.profile_image_path = profile_data.get("image") if profile_data else None
        self.is_editing = bool(profile_data)
        self.original_name = profile_data.get("name") if profile_data else None
        
        # Setup profiles images directory
        self.profiles_images_dir = os.path.join("profiles", "images")
        os.makedirs(self.profiles_images_dir, exist_ok=True)
        
        # MARK: - UI Setup
        self.setup_ui()
        self.connect_signals()
        self.setup_subscriptions()  # Subscribe to events
        self.load_data()
    
    # MARK: - UI Setup
    def setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle(f"{'Edit' if self.is_editing else 'New'} {self.profile_type.capitalize()} Profile")
        self.setModal(True)
        self.resize(1100, 700)
        
        # Enable maximize/minimize buttons
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | 
                           Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | 
                           Qt.WindowCloseButtonHint)
        
        self.setStyleSheet("""
            ProfileEditor {
                background-color: #282a36;
                color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Type selector - pass self as parent so TypeSelector can find main_window
        dollar_vars = self.main_window.get_dollar_variable() if self.main_window else {}
        self.type_selector = TypeSelector(self.profile_type, dollar_vars, parent=self)
        layout.addWidget(self.type_selector)
        
        # Main content with splitter
        content_widget = self.create_main_content()
        layout.addWidget(content_widget, 1)
        
        # Dialog buttons
        buttons = self.create_dialog_buttons()
        layout.addWidget(buttons)
    
    def create_main_content(self):
        """Create main content area with splitter"""
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        
        # Splitter - resizable by user
        splitter = ThemedSplitter(Qt.Horizontal)
        content_layout.addWidget(splitter)
        
        # Left - Variables
        left_widget = self.create_variables_section()
        splitter.addWidget(left_widget)
        
        # Middle - Type preview
        middle_widget = self.create_preview_section()
        splitter.addWidget(middle_widget)
        
        # Right - Profile info
        right_widget = self.create_profile_info_section()
        splitter.addWidget(right_widget)
         
        # Give all extra space to the middle pane by stretch factor
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
         
        return content_widget
    
    def create_variables_section(self):
        """Create variables section with resizable splitter for equal height distribution"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Create vertical splitter for variables and custom editors
        variables_splitter = ThemedSplitter(Qt.Vertical)
        left_layout.addWidget(variables_splitter, 1)  # Give splitter all available space
        
        # Variables editor
        self.variable_editor = VariableEditor()
        self.variable_editor.setVisible(False)
        variables_splitter.addWidget(self.variable_editor)
        
        # Custom editor
        self.custom_editor = CustomEditor()
        self.custom_editor.setVisible(False)
        variables_splitter.addWidget(self.custom_editor)
        
        # Set equal sizes by default (50% each)
        variables_splitter.setSizes([400, 400])  # Equal distribution
        
        # Optional: Set stretch factors to ensure equal growth/shrinking
        variables_splitter.setStretchFactor(0, 1)  # Variable editor gets equal stretch
        variables_splitter.setStretchFactor(1, 1)  # Custom editor gets equal stretch
        
        return left_widget
    
    def create_preview_section(self):
        """Create type preview section with proper scaling"""
        middle_widget = QWidget()
        middle_layout = QVBoxLayout(middle_widget)
        
        # Title
        title_label = ThemedLabel("Type Preview:")
        title_label.setStyleSheet("QLabel { font-weight: bold; padding: 5px; }")
        middle_layout.addWidget(title_label)
        
        self.preview_image_label = ScaledPreviewLabel()
        self.preview_image_label.setText("")
        
        # Give the preview label all available vertical space
        middle_layout.addWidget(self.preview_image_label, 1)
        
        return middle_widget
    
    def create_profile_info_section(self):
        """Create profile info section"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Profile name
        right_layout.addWidget(ThemedLabel("Profile Name:"))
        self.profile_name_edit = ThemedLineEdit()
        right_layout.addWidget(self.profile_name_edit)
        
        right_layout.addSpacing(20)
        
        # Profile image
        right_layout.addWidget(ThemedLabel("Profile Image:"))
        self.profile_image_label = ClickableImageLabel((150, 150))
        self.profile_image_label.clicked.connect(self.select_profile_image)
        self.set_profile_placeholder()
        right_layout.addWidget(self.profile_image_label, alignment=Qt.AlignCenter)
        
        right_layout.addStretch()
        
        return right_widget
    
    def create_dialog_buttons(self):
        """Create dialog buttons"""
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.setStyleSheet("""
            QDialogButtonBox QPushButton {
                background-color: #1d1f28;
                color: #23c87b;
                border: 2px solid #23c87b;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 80px;
            }
            QDialogButtonBox QPushButton:hover {
                background-color: #000000;
                color: #1a945b;
                border: 2px solid #1a945b;
            }
            QDialogButtonBox QPushButton:pressed {
                background-color: #23c87b;
                color: #1d1f28;
            }
        """)
        return buttons
    
    def connect_signals(self):
        """Connect UI signals"""
        # Type selector signals
        self.type_selector.type_selected.connect(self.on_type_selected)
        self.type_selector.types_modified.connect(self.on_types_modified)
        
        # Dialog buttons
        buttons = self.findChild(QDialogButtonBox)
        if buttons:
            buttons.accepted.connect(self.accept_profile)
            buttons.rejected.connect(self.reject)
    
    def setup_subscriptions(self):
        """Subscribe to main_window events"""
        if self.main_window:
            self.main_window.events.subscribe('profiles', self.on_profiles_updated)
    
    # MARK: - Event Handlers
    def on_profiles_updated(self):
        """Handle profile updates from main_window - refresh type selector"""
        if not self.main_window:
            return
        
        # Update type selector with latest data from main_window
        if self.profile_type == "hinge":
            types_data = self.main_window.hinges_types
        else:
            types_data = self.main_window.locks_types
        
        self.type_selector.load_types(types_data)
        
        # Reselect current type if it still exists
        if self.current_type and self.current_type["name"] in types_data:
            self.type_selector.on_type_clicked(self.current_type["name"])
    
    # MARK: - Data Loading
    def load_data(self):
        """Load existing profile data and types from main_window"""
        if not self.main_window:
            return
        
        # Load types from main_window
        if self.profile_type == "hinge":
            types_data = self.main_window.hinges_types
        else:
            types_data = self.main_window.locks_types
        
        self.type_selector.load_types(types_data)
        
        # Load profile data
        if self.profile_data:
            self.profile_name_edit.setText(self.profile_data.get("name", ""))
            
            if self.profile_image_path:
                pixmap = QPixmap(self.profile_image_path)
                if not pixmap.isNull():
                    self.profile_image_label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio))
            
            # Select type if profile has one
            if self.profile_data.get("type"):
                self.type_selector.on_type_clicked(self.profile_data["type"])
    
    # MARK: - Event Handlers
    def on_type_selected(self, type_data):
        """Handle type selection with improved preview scaling"""
        self.current_type = type_data
        
        # Update variable editors using gcode from type
        gcode = type_data.get("gcode", "")
        self.variable_editor.update_variables(gcode)
        self.custom_editor.update_customs(gcode)
        
        # Load saved variable values if editing
        if self.profile_data.get("type") == type_data["name"]:
            if self.profile_data.get("l_variables"):
                self.variable_editor.set_variable_values(self.profile_data["l_variables"])
            if self.profile_data.get("custom_variables"):
                self.custom_editor.set_custom_values(self.profile_data["custom_variables"])
        
        self.update_type_preview(type_data)
    
    def update_type_preview(self, type_data):
        """Update type preview with proper scaling and robust error handling"""
        if not type_data:
            self.preview_image_label.setText("No type selected")
            return
        
        preview_path = type_data.get("preview")
        
        # Handle all cases where preview is not available
        if not preview_path:
            # Preview path is None or empty string
            self.preview_image_label.setText("No preview available\nfor this type")
            return
        
        # Clean the path and check if it exists
        preview_path = str(preview_path).strip()
        if not preview_path:
            # Empty path after stripping
            self.preview_image_label.setText("No preview available\nfor this type")
            return
        
        if not os.path.exists(preview_path):
            # File doesn't exist
            self.preview_image_label.setText("Preview file not found:\n" + os.path.basename(preview_path))
            return
        
        try:
            # Try to load the image
            pixmap = QPixmap(preview_path)
            if not pixmap.isNull():
                # Successfully loaded image
                self.preview_image_label.setPixmap(pixmap)
            else:
                # QPixmap couldn't load the file (corrupt/unsupported format)
                self.preview_image_label.setText("Preview image corrupted\nor unsupported format")
        
        except Exception as e:
            # Any other error during loading
            self.preview_image_label.setText(f"Error loading preview:\n{str(e)}")
    
    def on_types_modified(self):
        """Handle when types are modified in the selector"""
        # TypeSelector already handles updating main_window directly
        # Just refresh our data in case anything changed
        if self.main_window:
            # Update dollar variables in type selector in case they changed
            dollar_vars = self.main_window.get_dollar_variable()
            self.type_selector.dollar_variables_info = dollar_vars
    
    def select_profile_image(self):
        """Select profile image with profiles/images as default directory"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select Profile Image", self.profiles_images_dir,
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.tiff);;All Files (*)"
        )
        if filename:
            self.profile_image_path = filename
            pixmap = QPixmap(filename)
            self.profile_image_label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio))
    
    def accept_profile(self):
        """Validate and save profile"""
        # Validate profile name
        name = self.profile_name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Name", 
                              "Please enter a profile name before saving.")
            self.profile_name_edit.setFocus()
            return
        
        # Validate type selection
        if not self.current_type:
            QMessageBox.warning(self, "No Type Selected", 
                              "Please select a type before saving.")
            return
        
        # Check for name conflicts
        if self.main_window:
            existing_profiles = (self.main_window.hinges_profiles if self.profile_type == "hinge" 
                               else self.main_window.locks_profiles)
            
            # Allow same name if editing the same profile
            if name in existing_profiles and (not self.is_editing or name != self.original_name):
                QMessageBox.warning(self, "Name Exists", 
                                  f"A profile named '{name}' already exists.")
                return
        
        # Save profile to main_window
        self.save_to_main_window(name)
        
        # Close dialog
        super().accept()
    
    # MARK: - Main Window Integration
    def save_to_main_window(self, name):
        """Save profile data to main_window"""
        if not self.main_window:
            return
        
        profile_data = {
            "name": name,
            "type": self.current_type["name"] if self.current_type else None,
            "l_variables": self.variable_editor.get_variable_values(),
            "custom_variables": self.custom_editor.get_custom_values(),
            "image": self.profile_image_path
        }
        
        # Remove old profile if name changed
        if self.is_editing and self.original_name and self.original_name != name:
            if self.profile_type == "hinge":
                self.main_window.update_hinge_profile(self.original_name, None)
            else:
                self.main_window.update_lock_profile(self.original_name, None)
        
        # Save new/updated profile
        if self.profile_type == "hinge":
            self.main_window.update_hinge_profile(name, profile_data)
        else:
            self.main_window.update_lock_profile(name, profile_data)
    
    def find_main_window(self, parent):
        """Find main_window from parent hierarchy"""
        current = parent
        while current:
            if hasattr(current, 'main_window'):
                return current.main_window
            current = current.parent()
        return None
    
    def set_profile_placeholder(self):
        """Set placeholder for profile image"""
        pixmap = PlaceholderPixmap.create_profile_placeholder((150, 150))
        self.profile_image_label.setPixmap(pixmap)