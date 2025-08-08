from PySide6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QInputDialog, QMessageBox, QFileDialog
from PySide6.QtCore import Qt, QSettings, QObject, Signal
from .profile.profile_tab import ProfileTab
from .frame.frame_tab import FrameTab
from .generate.generate_tab import GenerateTab
import json
import os
import re
import shutil
from datetime import datetime
from typing import Dict, Any, Callable, List


class EventManager(QObject):
    """Simple event manager for the 3 main update types"""
    
    # Event signals
    profiles_updated = Signal()  # Profile set, types, or profiles changed
    variables_updated = Signal()  # $variables changed
    generated_updated = Signal()  # Generated gcodes changed
    
    def __init__(self):
        super().__init__()
        self._subscribers = {
            'profiles': [],
            'variables': [],
            'generated': []
        }
    
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to an event type"""
        if event_type in self._subscribers:
            self._subscribers[event_type].append(callback)
            
            # Connect Qt signal to callback
            if event_type == 'profiles':
                self.profiles_updated.connect(callback)
            elif event_type == 'variables':
                self.variables_updated.connect(callback)
            elif event_type == 'generated':
                self.generated_updated.connect(callback)
    
    def emit_profiles_updated(self):
        """Emit profiles updated event"""
        self.profiles_updated.emit()
    
    def emit_variables_updated(self):
        """Emit variables updated event"""
        self.variables_updated.emit()
    
    def emit_generated_updated(self):
        """Emit generated updated event"""
        self.generated_updated.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CNC Frame Wizard")
        
        # Event manager
        self.events = EventManager()
        
        # MARK: - Variables Initiation
        # Profile set dictionaries
        self.hinges_types = {}      # {type_name: {name, gcode, image, preview, variables}}
        self.locks_types = {}       # {type_name: {name, gcode, image, preview, variables}}
        self.hinges_profiles = {}   # {profile_name: {name, type, l_variables, custom_variables, image}}
        self.locks_profiles = {}    # {profile_name: {name, type, l_variables, custom_variables, image}}
        
        # Gcode dictionaries
        self.current_gcodes = {"hinge_gcode": None, "lock_gcode": None, "right_gcode": None, "left_gcode": None}
        self.processed_gcodes = {"hinge_gcode": None, "lock_gcode": None, "right_gcode": None, "left_gcode": None}
        self.generated_gcodes = {"hinge_gcode": None, "lock_gcode": None, "right_gcode": None, "left_gcode": None}
        
        # $variables dictionary - ordered as desired for the help dialog
        self.dollar_variables = {
            # Frame properties
            "frame_height": 2100,
            "frame_width": 45,
            "door_width": 40,
            
            # Machine offsets
            "machine_x_offset": 0,
            "machine_y_offset": 0,
            "machine_z_offset": 0,
            
            # PM positions
            "pm1_position": -25,
            "pm2_position": 700,
            "pm3_position": 1230,
            "pm4_position": 1540,
            
            # Auto calculation states
            "pm_auto": 0,  # PM auto-positioning
            "lock_auto": 1,  # Lock auto-positioning
            "lock_y_auto": 0,  # Lock Y offset auto-calculation
            "hinge_auto": 1,  # Hinge auto-positioning
            "hinge_y_auto": 0,  # Hinge Y offset auto-calculation
            
            # Lock configuration
            "lock_position": 1050,
            "lock_y_offset": 0,
            "lock_active": 1,
            "lock_order": 0,
            
            # Hinge configuration
            "hinge_y_offset": 0,
            "hinge1_position": 0,
            "hinge1_active": 1,
            "hinge1_order": 0,
            "hinge2_position": 0,
            "hinge2_active": 1,
            "hinge2_order": 0,
            "hinge3_position": 0,
            "hinge3_active": 1,
            "hinge3_order": 0,
            "hinge4_position": 0,
            "hinge4_active": 1,
            "hinge4_order": 0,
            
            # Door orientation
            "orientation": "right",
            
            # Selected profiles
            "selected_hinge": None,
            "selected_lock": None,
        }
        
        # Initialize settings
        self.settings = QSettings("CNCFrameWizard", "AppConfig")
        
        self.default_config_init()
        
        # Setup UI
        self.setup_ui()
        
        # Load configurations
        self.load_app_config()
        self.load_profile_set(current=True)
        
        # Setup event subscriptions
        self.setup_event_subscriptions()
        
    def default_config_init(self):
        """Initialize default configurations if not set"""
        self.profiles_dir = "profiles"
        self.current_file = os.path.join(self.profiles_dir, "current.json")
        self.saved_dir = os.path.join(self.profiles_dir, "saved")
        self.projects_dir = "projects" 
        
        # Ensure directories exist
        os.makedirs(self.saved_dir, exist_ok=True)
        os.makedirs(self.projects_dir, exist_ok=True)
    
    def setup_ui(self):
        """Setup user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.profile_tab = ProfileTab(self)
        self.frame_tab = FrameTab(self)
        self.generate_tab = GenerateTab(self)
        
        # Add tabs
        self.tabs.addTab(self.profile_tab, "Profile Selection")
        self.tabs.addTab(self.frame_tab, "Frame Setup")
        self.tabs.addTab(self.generate_tab, "Generate Files")
        
        # Initially disable tabs 2 and 3
        self.tabs.setTabEnabled(1, False)
        self.tabs.setTabEnabled(2, False)
        
        # Connect basic UI signals
        self.connect_ui_signals()
        
        # Show window
        if not self.settings.contains("geometry"):
            self.showMaximized()
        else:
            self.show()
    
    def setup_event_subscriptions(self):
        """Setup event subscriptions for automatic updates"""
        
        # Subscribe to profile updates
        self.events.subscribe('profiles', self.on_profiles_updated)
        self.events.subscribe('profiles', self.update_tab_states)
        
        # Subscribe to variable updates  
        self.events.subscribe('variables', self.on_variables_updated)
        
        # Subscribe to generated updates
        self.events.subscribe('generated', self.on_generated_updated)
        
        # Let tabs subscribe to events they care about
        if hasattr(self.profile_tab, 'setup_subscriptions'):
            self.profile_tab.setup_subscriptions(self.events)
        if hasattr(self.frame_tab, 'setup_subscriptions'):
            self.frame_tab.setup_subscriptions(self.events)
        if hasattr(self.generate_tab, 'setup_subscriptions'):
            self.generate_tab.setup_subscriptions(self.events)
    
    def connect_ui_signals(self):
        """Connect basic UI signals (not event-based)"""
        
        # Profile tab UI signals
        self.profile_tab.next_clicked.connect(lambda: self.tabs.setCurrentIndex(1))
        self.profile_tab.save_project_button.clicked.connect(self.save_project)
        self.profile_tab.load_project_button.clicked.connect(self.load_project)
        self.profile_tab.save_set_button.clicked.connect(lambda: self.save_profile_set(current=False))
        self.profile_tab.load_set_button.clicked.connect(lambda: self.load_profile_set(current=False))
        
        # Frame tab UI signals
        self.frame_tab.back_clicked.connect(lambda: self.tabs.setCurrentIndex(0))
        self.frame_tab.next_clicked.connect(lambda: self.tabs.setCurrentIndex(2))
        
        # Generate tab UI signals
        self.generate_tab.back_clicked.connect(lambda: self.tabs.setCurrentIndex(1))
        self.generate_tab.generate_button.clicked.connect(self.generate_files)
    
    def closeEvent(self, event):
        """Save app configuration before closing"""
        self.save_app_config()
        event.accept()
    
    # MARK: - Event Handlers (The 3 main update types)
    
    def on_profiles_updated(self):
        """Handle profiles updated event - triggered when profiles/types/sets change"""
        
        # Re-extract gcodes from selected profiles in case they changed
        selected_hinge = self.dollar_variables.get("selected_hinge")
        selected_lock = self.dollar_variables.get("selected_lock")
        
        if selected_hinge:
            hinge_gcode = self.get_hinge_profile_gcode(selected_hinge)
            self.current_gcodes["hinge_gcode"] = hinge_gcode
        
        if selected_lock:
            lock_gcode = self.get_lock_profile_gcode(selected_lock)
            self.current_gcodes["lock_gcode"] = lock_gcode
        
        # Process gcodes with current variables
        self.process_gcodes()
        
        # Auto-save current profile set
        self.save_profile_set(current=True)
        print("Profiles updated - gcodes re-extracted, processed and saved")
    
    def on_variables_updated(self):
        """Handle variables updated event - triggered when $variables change"""
        # Reprocess gcodes with new variables
        self.process_gcodes()
        print("Variables updated - gcodes reprocessed")
    
    def on_generated_updated(self):
        """Handle generated updated event - triggered when generated gcodes change"""
        # Update any displays that show generated content
        print("Generated gcodes updated")
    
    def update_tab_states(self):
        """Update tab enabled states based on current data"""
        # Enable frame tab if profiles are selected
        hinge_selected = self.dollar_variables.get("selected_hinge")
        lock_selected = self.dollar_variables.get("selected_lock")
        
        if hinge_selected and lock_selected:
            self.tabs.setTabEnabled(1, True)
            
            # Enable generate tab if frame is configured
            # Check if basic frame variables are set
            #NOTE: this is just a placeholder
            frame_configured = (
                self.dollar_variables.get("frame_height") and 
                self.dollar_variables.get("frame_width")
            )
            
            if frame_configured:
                self.tabs.setTabEnabled(2, True)
        else:
            self.tabs.setTabEnabled(1, False)
            self.tabs.setTabEnabled(2, False)
    
    # MARK: - Profile Updates
    
    def update_hinge_type(self, name: str, data: Dict[str, Any] = None):
        """Update hinge type (delete if data is None)"""
        if data is None:
            self.hinges_types.pop(name, None)
        else:
            self.hinges_types[name] = data
        self.events.emit_profiles_updated()
    
    def update_lock_type(self, name: str, data: Dict[str, Any] = None):
        """Update lock type (delete if data is None)"""
        if data is None:
            self.locks_types.pop(name, None)
        else:
            self.locks_types[name] = data
        self.events.emit_profiles_updated()
    
    def update_hinge_profile(self, name: str, data: Dict[str, Any] = None):
        """Update hinge profile (delete if data is None)"""
        if data is None:
            self.hinges_profiles.pop(name, None)
        else:
            self.hinges_profiles[name] = data
        self.events.emit_profiles_updated()
    
    def update_lock_profile(self, name: str, data: Dict[str, Any] = None):
        """Update lock profile (delete if data is None)"""
        if data is None:
            self.locks_profiles.pop(name, None)
        else:
            self.locks_profiles[name] = data
        self.events.emit_profiles_updated()
    
    def update_frame_gcode(self, right_gcode: str = None, left_gcode: str = None):
        """Update frame gcodes"""
        self.update_current_gcodes("right_gcode", right_gcode)
        self.update_current_gcodes("left_gcode", left_gcode)
    
    def select_profiles(self, hinge_profile: str, lock_profile: str):
        """Select hinge and lock profiles"""
        # Update variables
        self.dollar_variables["selected_hinge"] = hinge_profile
        self.dollar_variables["selected_lock"] = lock_profile
        
        # Update current gcodes from selected profiles
        hinge_gcode = self.get_hinge_profile_gcode(hinge_profile)
        lock_gcode = self.get_lock_profile_gcode(lock_profile)
        
        self.update_current_gcodes("hinge_gcode", hinge_gcode)
        self.update_current_gcodes("lock_gcode", lock_gcode)
    
    # MARK: - Variable Updates
    
    def update_dollar_variable(self, name: str, value: Any):
        """Update single $variable"""
        if name in self.dollar_variables:
            self.dollar_variables[name] = value
            self.events.emit_variables_updated()
    
    def update_dollar_variables(self, variables: Dict[str, Any]):
        """Update multiple $variables"""
        for name, value in variables.items():
            if name in self.dollar_variables:
                self.dollar_variables[name] = value
        self.events.emit_variables_updated()
    
    # MARK: - Profile Set
    
    def save_profile_set(self, current: bool = False):
        """Save current profile set"""
        if current:
            filename = self.current_file
        else:
            default_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.json")
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save Profile Set", 
                os.path.join(self.saved_dir, default_name),
                "JSON Files (*.json)"
            )
        
        if filename:
            try:
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                
                data = {
                    "hinges": {
                        "types": self.hinges_types,
                        "profiles": self.hinges_profiles
                    },
                    "locks": {
                        "types": self.locks_types,
                        "profiles": self.locks_profiles
                    },
                    "frame_gcode": {
                        "right_gcode": self.current_gcodes["right_gcode"],
                        "left_gcode": self.current_gcodes["left_gcode"]
                    }
                }
                
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                
                if not current:
                    QMessageBox.information(self, "Success", "Profile set saved successfully!")
                return True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save profile set: {str(e)}")
                return False
        return False
    
    def load_profile_set(self, current: bool = False):
        """Load profile set"""
        if current:
            filename = self.current_file
            if not os.path.exists(filename):
                return False
        else:
            filename, _ = QFileDialog.getOpenFileName(
                self, "Load Profile Set", 
                self.saved_dir,
                "JSON Files (*.json)"
            )
        
        if filename and os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                # Load types and profiles
                if "hinges" in data:
                    self.hinges_types = data["hinges"].get("types", {})
                    self.hinges_profiles = data["hinges"].get("profiles", {})
                if "locks" in data:
                    self.locks_types = data["locks"].get("types", {})
                    self.locks_profiles = data["locks"].get("profiles", {})
                
                # Load frame gcodes
                if "frame_gcode" in data:
                    self.current_gcodes["right_gcode"] = data["frame_gcode"].get("right_gcode")
                    self.current_gcodes["left_gcode"] = data["frame_gcode"].get("left_gcode")
                
                if not current:
                    QMessageBox.information(self, "Success", "Profile set loaded successfully!")
                
                self.events.emit_profiles_updated()
                return True
                
            except Exception as e:
                if not current:
                    QMessageBox.critical(self, "Error", f"Failed to load profile set: {str(e)}")
                print(f"Error loading profile set: {str(e)}")
                return False
        return False
    
    # MARK: - Project Management
    
    def save_project(self):
        """Save project as a single JSON file with file dialog"""
        # Generate default filename with current date and time
        default_name = datetime.now().strftime("project_%Y-%m-%d_%H-%M-%S.json")
        
        # Open file dialog for saving
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Project", 
            os.path.join(self.projects_dir, default_name),
            "JSON Files (*.json)"
        )
        
        if not filename:
            return False  # User cancelled
        
        try:
            # Ensure projects directory exists
            os.makedirs(self.projects_dir, exist_ok=True)
            
            # Create project data
            data = {
                "dollar_variables": self.dollar_variables,
                "generated_gcodes": self.generated_gcodes,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save as single JSON file
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            QMessageBox.information(self, "Success", f"Project saved successfully to:\n{filename}")
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save project: {str(e)}")
            return False
    
    def load_project(self):
        """Load complete project"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Load Project", 
            self.projects_dir,
            "JSON Files (*.json)"
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)

                # Load $variables and generated gcodes
                if "dollar_variables" in data:
                    self.dollar_variables.update(data["dollar_variables"])
                    self.events.emit_variables_updated()
                
                if "generated_gcodes" in data:
                    self.generated_gcodes = data["generated_gcodes"]
                    self.events.emit_generated_updated()
                
                QMessageBox.information(self, "Success", "Project loaded successfully!")
                return True
        
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load project: {str(e)}")
            return False
    
    # MARK: - Gcode Processing
    
    def update_current_gcodes(self, name: str, gcode: str):
        """Update current gcode by name"""
        if name in self.current_gcodes:
            self.current_gcodes[name] = gcode
            self.events.emit_profiles_updated()
    
    def process_gcodes(self):
        """Process current gcodes with $variables"""
        for name, gcode in self.current_gcodes.items():
            if gcode:
                processed = self.replace_dollar_variables(gcode)
                self.processed_gcodes[name] = processed
            else:
                self.processed_gcodes[name] = None
                
    def update_generated_gcode(self, name: str, gcode: str):
        """Update single generated gcode"""
        if name in self.generated_gcodes:
            self.generated_gcodes[name] = gcode
            self.events.emit_generated_updated()
    
    def copy_to_generated(self):
        """Copy processed gcodes to generated"""
        self.generated_gcodes = self.processed_gcodes.copy()
        self.events.emit_generated_updated()
        

    def check_processed_vs_generated(self) -> Dict[str, bool]:
        """Check if processed gcodes match generated gcodes"""
        comparison = {}
        
        for gcode_name in self.current_gcodes.keys():
            processed = self.processed_gcodes.get(gcode_name, "")
            generated = self.generated_gcodes.get(gcode_name, "")
            
            # Handle None values
            processed = processed or ""
            generated = generated or ""
            
            comparison[gcode_name] = (processed == generated)
        
        return comparison
    
    def replace_dollar_variables(self, gcode: str) -> str:
        """Replace $variables in gcode with actual values"""
        if not gcode:
            return gcode
        
        result = gcode
        for var_name, value in self.dollar_variables.items():
            pattern = f"{{\\${var_name}}}"
            if value is not None:
                result = re.sub(pattern, str(value), result)
        return result
    
    def replace_profile_variables(self, gcode: str, l_variables: Dict[str, Any], custom_variables: Dict[str, Any]) -> str:
        """Replace L and custom variables in profile gcode"""
        if not gcode:
            return gcode
        
        result = gcode
        
        # Replace L variables - handle both {L1} and {L1:default} formats
        if l_variables:
            for var_name, value in l_variables.items():
                if value is not None and str(value).strip():  # Only replace if value is not empty
                    # Pattern matches both {L1} and {L1:any_default_value}
                    pattern = rf'\{{{re.escape(var_name)}(?::[^}}]+)?\}}'
                    result = re.sub(pattern, str(value), result)
                    print(f"Replaced L variable {var_name} with {value}")
        
        # Replace custom variables - handle both {var} and {var:default} formats
        if custom_variables:
            for var_name, value in custom_variables.items():
                if value is not None and str(value).strip():  # Only replace if value is not empty
                    # Pattern matches both {var_name} and {var_name:any_default_value}
                    pattern = rf'\{{{re.escape(var_name)}(?::[^}}]+)?\}}'
                    result = re.sub(pattern, str(value), result)
                    print(f"Replaced custom variable '{var_name}' with {value}")
    
        return result
    
    # MARK: - Getters
    
    def get_hinge_type(self, name: str) -> Dict[str, Any]:
        """Get hinge type data"""
        return self.hinges_types.get(name, {})
    
    def get_lock_type(self, name: str) -> Dict[str, Any]:
        """Get lock type data"""
        return self.locks_types.get(name, {})
    
    def get_hinge_profile(self, name: str) -> Dict[str, Any]:
        """Get hinge profile data"""
        return self.hinges_profiles.get(name, {})
    
    def get_lock_profile(self, name: str) -> Dict[str, Any]:
        """Get lock profile data"""
        return self.locks_profiles.get(name, {})
    
    def get_hinge_profile_gcode(self, name: str) -> str:
        """Get hinge profile gcode with variables replaced"""
        profile = self.get_hinge_profile(name)
        if not profile or not profile.get("type"):
            return ""
        
        hinge_type = self.get_hinge_type(profile["type"])
        if not hinge_type or not hinge_type.get("gcode"):
            return ""
        
        # Replace L and custom variables in the type gcode
        gcode = hinge_type["gcode"]
        l_variables = profile.get("l_variables", {})
        custom_variables = profile.get("custom_variables", {})
        
        return self.replace_profile_variables(gcode, l_variables, custom_variables)
    
    def get_lock_profile_gcode(self, name: str) -> str:
        """Get lock profile gcode with variables replaced"""
        profile = self.get_lock_profile(name)
        if not profile or not profile.get("type"):
            return ""
        
        lock_type = self.get_lock_type(profile["type"])
        if not lock_type or not lock_type.get("gcode"):
            return ""
        
        # Replace L and custom variables in the type gcode
        gcode = lock_type["gcode"]
        l_variables = profile.get("l_variables", {})
        custom_variables = profile.get("custom_variables", {})
        
        return self.replace_profile_variables(gcode, l_variables, custom_variables)
    
    def get_current_gcode(self, name: str) -> str:
        """Get current gcode"""
        return self.current_gcodes.get(name, "")
    
    def get_processed_gcode(self, name: str) -> str:
        """Get processed gcode"""
        return self.processed_gcodes.get(name, "")
    
    def get_generated_gcode(self, name: str) -> str:
        """Get generated gcode"""
        return self.generated_gcodes.get(name, "")
    
    def get_dollar_variable(self, name: str = None):
        """Get $variable or all $variables if name is None"""
        if name is None:
            return self.dollar_variables.copy()
        return self.dollar_variables.get(name, "")
    
    # MARK: - App Config
    
    def save_app_config(self):
        """Save application configuration"""
        try:
            config = {
                "geometry": self.saveGeometry().data().hex(),
                "windowState": self.saveState().data().hex()
            }
            
            # Get config from each tab
            if hasattr(self.profile_tab, 'get_app_config'):
                config["profile_tab"] = self.profile_tab.get_app_config()
            if hasattr(self.frame_tab, 'get_app_config'):
                config["frame_tab"] = self.frame_tab.get_app_config()
            if hasattr(self.generate_tab, 'get_app_config'):
                config["generate_tab"] = self.generate_tab.get_app_config()
            
            self.settings.setValue("app_config", json.dumps(config))
            self.settings.sync()
        except Exception as e:
            print(f"Error saving app config: {str(e)}")
    
    def load_app_config(self):
        """Load application configuration"""
        try:
            config_str = self.settings.value("app_config")
            if not config_str:
                return
            
            config = json.loads(config_str)
            
            # Restore window state
            if "geometry" in config:
                self.restoreGeometry(bytes.fromhex(config["geometry"]))
            if "windowState" in config:
                self.restoreState(bytes.fromhex(config["windowState"]))
            
            # Load config for each tab
            if hasattr(self.profile_tab, 'set_app_config') and "profile_tab" in config:
                self.profile_tab.set_app_config(config["profile_tab"])
            if hasattr(self.frame_tab, 'set_app_config') and "frame_tab" in config:
                self.frame_tab.set_app_config(config["frame_tab"])
            if hasattr(self.generate_tab, 'set_app_config') and "generate_tab" in config:
                self.generate_tab.set_app_config(config["generate_tab"])
        except Exception as e:
            print(f"Error loading app config: {str(e)}")
    
    def generate_files(self):
        """Generate final gcode files"""        
        # Copy processed to generated
        self.copy_to_generated()
        print("Files generated successfully!")