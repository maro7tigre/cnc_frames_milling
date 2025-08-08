"""
Generate Tab

Simplified file generation tab with sync status highlighting and controlled generation.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QFileDialog, QMessageBox
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
import os
import shutil

from ..widgets.themed_widgets import (ThemedSplitter, ThemedLabel, ThemedLineEdit, ThemedGroupBox,
                                    PurpleButton, GreenButton, OrangeButton)
from .widgets.generated_file_item import GeneratedFileItem


class GenerateTab(QWidget):
    """Generate tab with controlled generation and sync status highlighting"""
    back_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.output_dir = os.path.expanduser("~/CNC/Output")
        self.first_time_opened = True  # Track first opening
        
        # File items organized by side and type
        self.file_items = {
            'left': {},
            'right': {}
        }
        
        # MARK: - UI Setup
        self.setup_ui()
        self.apply_styling()
        self.connect_signals()
        
        # MARK: - Event Subscriptions
        if self.main_window:
            self.main_window.events.subscribe('profiles', self.on_profiles_updated)
            self.main_window.events.subscribe('variables', self.on_variables_updated)
            self.main_window.events.subscribe('generated', self.on_generated_updated)
    
    # MARK: - UI Setup
    
    def apply_styling(self):
        """Apply dark theme styling"""
        self.setStyleSheet("""
            GenerateTab {
                background-color: #282a36;
                color: #ffffff;
            }
        """)
    
    def setup_ui(self):
        """Initialize user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Top toolbar
        toolbar_layout = QHBoxLayout()
        main_layout.addLayout(toolbar_layout)
        
        # Title
        title_label = ThemedLabel("Generated G-Code Files")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        toolbar_layout.addWidget(title_label)
        
        toolbar_layout.addStretch()
        
        # Generate button
        self.generate_button = GreenButton("Generate Files")
        toolbar_layout.addWidget(self.generate_button)
        
        # Main content area with splitter
        content_splitter = ThemedSplitter(Qt.Horizontal)
        main_layout.addWidget(content_splitter, 1)
        
        # Left side files
        left_widget = self.create_side_panel("Left Side", "left")
        content_splitter.addWidget(left_widget)
        
        # Right side files
        right_widget = self.create_side_panel("Right Side", "right")
        content_splitter.addWidget(right_widget)
        
        # Set equal sizes
        content_splitter.setSizes([400, 400])
        
        # Output directory section with export button
        output_layout = QHBoxLayout()
        main_layout.addLayout(output_layout)
        
        output_layout.addWidget(ThemedLabel("Output Directory:"))
        self.output_path = ThemedLineEdit(self.output_dir)
        self.output_path.setReadOnly(True)
        output_layout.addWidget(self.output_path)
        
        browse_button = PurpleButton("Browse")
        browse_button.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(browse_button)
        
        # Export button
        self.export_button = OrangeButton("Export Files")
        self.export_button.clicked.connect(self.export_files)
        output_layout.addWidget(self.export_button)
        
        # Bottom navigation
        nav_layout = QHBoxLayout()
        main_layout.addLayout(nav_layout)
        
        nav_layout.addStretch()
        
        back_button = PurpleButton("← Back")
        back_button.clicked.connect(self.back_clicked)
        nav_layout.addWidget(back_button)
    
    def create_side_panel(self, title, side):
        """Create a panel for left or right side files"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Group box
        group = ThemedGroupBox(title)
        group_layout = QVBoxLayout(group)
        layout.addWidget(group)
        
        # File grid
        grid_layout = QGridLayout()
        group_layout.addLayout(grid_layout)
        
        # Create file items
        file_types = [
            ('frame', f'{title.split()[0]} Frame'),
            ('lock', 'Lock'),
            ('hinge', 'Hinge')
        ]
        
        for i, (file_type, display_name) in enumerate(file_types):
            file_item = GeneratedFileItem(display_name, file_type, side, self.main_window)
            file_item.content_changed.connect(
                lambda content, s=side, ft=file_type: self.on_file_content_changed(s, ft, content)
            )
            
            self.file_items[side][file_type] = file_item
            grid_layout.addWidget(file_item, i // 2, i % 2)
        
        # Add stretch
        group_layout.addStretch()
        
        return widget
    
    def connect_signals(self):
        """Connect widget signals"""
        self.generate_button.clicked.connect(self.generate_files)
    
    def showEvent(self, event):
        """Handle tab being shown - generate files only on first time"""
        super().showEvent(event)
        
        if self.first_time_opened:
            self.first_time_opened = False
            self.generate_files()
    
    # MARK: - Event Handlers
    
    def on_profiles_updated(self):
        """Handle profiles updated - check sync status only"""
        self.check_and_update_sync_status()
    
    def on_variables_updated(self):
        """Handle variables updated - check sync status only"""
        self.check_and_update_sync_status()
    
    def on_generated_updated(self):
        """Handle generated updated - update file items and check sync"""
        self.update_file_items_from_main_window()
        self.check_and_update_sync_status()
    
    def check_and_update_sync_status(self):
        """Check if generated gcodes match processed gcodes and update highlighting"""
        if not self.main_window:
            return
        
        # Get sync status comparison
        sync_status = self.main_window.check_processed_vs_generated()
        
        # Update file item highlighting based on sync status
        for side in ['left', 'right']:
            for file_type in ['frame', 'lock', 'hinge']:
                file_item = self.file_items[side][file_type]
                
                # Map file type to gcode key
                if file_type == 'frame':
                    gcode_key = f"{side}_gcode"
                else:
                    gcode_key = f"{file_type}_gcode"
                
                # Update sync status
                is_synced = sync_status.get(gcode_key, True)
                file_item.set_sync_status(is_synced)
    
    def update_file_items_from_main_window(self):
        """Update file items with content from main_window generated gcodes"""
        if not self.main_window:
            return
        
        # Get generated gcodes from main_window
        generated_gcodes = {
            'hinge_gcode': self.main_window.get_generated_gcode('hinge_gcode'),
            'lock_gcode': self.main_window.get_generated_gcode('lock_gcode'),
            'right_gcode': self.main_window.get_generated_gcode('right_gcode'),
            'left_gcode': self.main_window.get_generated_gcode('left_gcode')
        }
        
        # Update file items
        for side in ['left', 'right']:
            for file_type in ['frame', 'lock', 'hinge']:
                file_item = self.file_items[side][file_type]
                
                # Map file type to gcode key
                if file_type == 'frame':
                    gcode_key = f"{side}_gcode"
                else:
                    gcode_key = f"{file_type}_gcode"
                
                content = generated_gcodes.get(gcode_key, '')
                file_item.update_content(content)
    
    def on_file_content_changed(self, side, file_type, new_content):
        """Handle manual file content changes - update generated gcode directly"""
        if not self.main_window:
            return
        
        # Map file type to gcode key
        if file_type == 'frame':
            gcode_key = f"{side}_gcode"
        else:
            gcode_key = f"{file_type}_gcode"
        
        # Update main_window generated gcode directly
        self.main_window.update_generated_gcode(gcode_key, new_content)
        
        print(f"Updated {gcode_key} in generated gcodes")
    
    # MARK: - File Generation
    
    def generate_files(self):
        """Generate files - only when explicitly called"""
        if not self.main_window:
            return
        
        print("Generating files...")
        
        # Process gcodes in main_window to get latest processed versions
        self.main_window.process_gcodes()
        
        # Copy processed to generated
        self.main_window.copy_to_generated()
        
        print("Files generated successfully!")
    
    # MARK: - File Export
    
    def export_files(self):
        """Export all files to the output directory with proper cnc structure"""
        if not self.main_window:
            QMessageBox.warning(self, "No Data", "No main window data available.")
            return
        
        # Check if we have any files to export
        has_files = False
        for side in ['left', 'right']:
            for file_type in ['frame', 'lock', 'hinge']:
                if self.file_items[side][file_type].has_content():
                    has_files = True
                    break
            if has_files:
                break
        
        if not has_files:
            QMessageBox.warning(self, "No Files", 
                              "No files available to export. Please generate files first.")
            return
        
        try:
            # Ensure output directory exists
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Remove existing cnc directory if it exists
            cnc_dir = os.path.join(self.output_dir, "cnc")
            if os.path.exists(cnc_dir):
                shutil.rmtree(cnc_dir)
            
            # Create new cnc directory structure
            os.makedirs(cnc_dir, exist_ok=True)
            
            exported_files = []
            
            for side_en, side_fr in [('left', 'gauche'), ('right', 'droite')]:
                side_dir = os.path.join(cnc_dir, side_fr)
                os.makedirs(side_dir, exist_ok=True)
                
                for file_type in ['frame', 'lock', 'hinge']:
                    file_item = self.file_items[side_en][file_type]
                    content = file_item.get_content()
                    
                    if content:
                        # Convert line endings to Windows format
                        content_windows = content.replace('\n', '\r\n').replace('\r\r\n', '\r\n')
                        
                        filename = f"{side_en}_{file_type}.txt"
                        filepath = os.path.join(side_dir, filename)
                        
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content_windows)
                        
                        exported_files.append(filepath)
            
            # Show success message
            file_count = len(exported_files)
            QMessageBox.information(self, "Export Successful", 
                                  f"Exported {file_count} files to:\n{cnc_dir}")
        
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", 
                               f"Failed to export files:\n{str(e)}")
    
    def browse_output_dir(self):
        """Browse for output directory"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", self.output_dir
        )
        if dir_path:
            self.output_dir = dir_path
            self.output_path.setText(dir_path)
    
    # MARK: - Configuration
    
    def get_app_config(self):
        """Get tab configuration for saving"""
        return {
            "output_dir": self.output_dir
        }
    
    def set_app_config(self, config):
        """Set tab configuration from loading"""
        self.output_dir = config.get("output_dir", self.output_dir)
        self.output_path.setText(self.output_dir)