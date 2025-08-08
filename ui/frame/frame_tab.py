"""
Frame Tab 

Clean architecture with predictable update flow and proper separation of concerns.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFormLayout, QButtonGroup
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QDoubleValidator

from ..widgets.themed_widgets import (ThemedSplitter, ThemedLabel, ThemedRadioButton, 
                                    ThemedGroupBox, PurpleButton, GreenButton, ThemedCheckBox, ThemedSpinBox, ThemedLineEdit)
from ..widgets.simple_widgets import ClickableLabel, ErrorLineEdit
from ..widgets.dollar_variable_widgets import (DollarVariableLineEdit, DollarVariableSpinBox, 
                                             DollarVariableCheckBox, DollarVariableRadioGroup)
from .widgets.frame_preview import FramePreview
from .widgets.order_widget import OrderWidget


class FrameTab(QWidget):
    """frame configuration tab with unified auto-calculation system"""
    back_clicked = Signal()
    next_clicked = Signal()
    
    # Configuration parameters
    MAX_FRAME_HEIGHT = 2500
    MIN_FRAME_HEIGHT = 840
    
    # PM configuration from old code
    PM_CONFIG = {
        'sizes': {
            1: [265, 140],  # PM1 dimensions [width, height]
            2: [140, 175],  # PM2 dimensions
            3: [175, 240],  # PM3 dimensions
            4: [240, 120]   # PM4 dimensions
        },
        'lock_safety_distance': 170,
        'hinge_safety_distance': 170,
        'min_range_size': 120
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        
        # MARK: - Auto-calculation control
        self._auto_calculation_running = False
        
        # MARK: - UI Setup
        self.setup_ui()
        self.apply_styling()
        self.connect_signals()
        
        # MARK: - Event Subscriptions
        if self.main_window:
            self.main_window.events.subscribe('variables', self.on_variables_updated)
        
        # MARK: - Initial Setup
        self.setup_initial_values()
    
    # MARK: - UI Setup
    
    def apply_styling(self):
        """Apply dark theme styling"""
        self.setStyleSheet("""
            FrameTab {
                background-color: #282a36;
                color: #ffffff;
            }
        """)
    
    def setup_ui(self):
        """Initialize user interface with three-panel layout"""
        main_layout = QVBoxLayout(self)
        
        # Content area with splitter
        content_splitter = ThemedSplitter(Qt.Horizontal)
        main_layout.addWidget(content_splitter)
        
        # Left panel
        left_widget = self.create_left_panel()
        content_splitter.addWidget(left_widget)
        
        # Middle panel (preview)
        middle_widget = self.create_middle_panel()
        content_splitter.addWidget(middle_widget)
        
        # Right panel
        right_widget = self.create_right_panel()
        content_splitter.addWidget(right_widget)
        
        # Set initial splitter sizes
        content_splitter.setSizes([300, 400, 300])
        
        # Bottom navigation
        nav_layout = self.create_navigation()
        main_layout.addLayout(nav_layout)
    
    def create_left_panel(self):
        """Create left panel with frame dimensions and PM positions"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Frame dimensions group
        frame_group = ThemedGroupBox("Frame Configuration")
        frame_layout = QFormLayout()
        frame_group.setLayout(frame_layout)
        
        # Frame height with validation
        self.height_input = SimpleDollarLineEdit("frame_height", self)
        self.height_input.setValidator(QDoubleValidator(self.MIN_FRAME_HEIGHT, self.MAX_FRAME_HEIGHT, 2))
        frame_layout.addRow("Frame Height (mm):", self.height_input)
        
        # Frame width
        self.width_input = SimpleDollarLineEdit("frame_width", self)
        self.width_input.setValidator(QDoubleValidator(10, 100, 2))
        frame_layout.addRow("Frame Width (mm):", self.width_input)
        
        # Door width
        self.door_width_input = SimpleDollarLineEdit("door_width", self)
        self.door_width_input.setValidator(QDoubleValidator(10, 100, 2))
        frame_layout.addRow("Door Width (mm):", self.door_width_input)
        
        # Machine offsets
        self.x_offset_input = SimpleDollarLineEdit("machine_x_offset", self)
        self.x_offset_input.setValidator(QDoubleValidator(-1000, 1000, 2))
        #frame_layout.addRow("Machine X Offset:", self.x_offset_input)
        #
        self.y_offset_input = SimpleDollarLineEdit("machine_y_offset", self)
        self.y_offset_input.setValidator(QDoubleValidator(-1000, 1000, 2))
        #frame_layout.addRow("Machine Y Offset:", self.y_offset_input)
        #
        self.z_offset_input = SimpleDollarLineEdit("machine_z_offset", self)
        self.z_offset_input.setValidator(QDoubleValidator(-1000, 1000, 2))
        #frame_layout.addRow("Machine Z Offset:", self.z_offset_input)
        
        layout.addWidget(frame_group)
        
        # PM positions group
        pm_group = ThemedGroupBox("PM Positions")
        pm_layout = QVBoxLayout()
        pm_group.setLayout(pm_layout)
        
        # PM auto checkbox
        self.pm_auto_check = ThemedCheckBox("Auto-position")
        self.pm_auto_check.setChecked(False)
        self.pm_auto_check.stateChanged.connect(self.on_auto_state_changed)
        pm_layout.addWidget(self.pm_auto_check)
        
        # PM position inputs
        self.pm_inputs_widget = QWidget()
        pm_inputs_layout = QFormLayout(self.pm_inputs_widget)
        pm_layout.addWidget(self.pm_inputs_widget)
        
        self.pm_inputs = []
        for i in range(4):
            pm_input = SimpleDollarLineEdit(f"pm{i+1}_position", self)
            pm_input.setValidator(QDoubleValidator(-100, self.MAX_FRAME_HEIGHT, 2))
            pm_inputs_layout.addRow(f"PM{i+1} Position:", pm_input)
            self.pm_inputs.append(pm_input)
        
        layout.addWidget(pm_group)
        layout.addStretch()
        
        return widget
    
    def create_middle_panel(self):
        """Create middle panel with preview and orientation switch"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Orientation switch with G-code edit links
        orientation_group = ThemedGroupBox("Door Orientation")
        orientation_layout = QVBoxLayout()
        orientation_group.setLayout(orientation_layout)
        
        # Radio buttons layout
        radio_layout = QHBoxLayout()
        
        # Create radio group for orientation
        self.orientation_group = SimpleDollarRadioGroup("orientation", self)
        
        self.right_radio = ThemedRadioButton("Right (droite)")
        self.left_radio = ThemedRadioButton("Left (gauche)")
        
        # Add to dollar variable group
        self.orientation_group.add_button(self.right_radio, "right")
        self.orientation_group.add_button(self.left_radio, "left")
        
        radio_layout.addWidget(self.right_radio)
        self.right_gcode_link = ClickableLabel("Edit")
        self.right_gcode_link.clicked.connect(self.edit_right_gcode)
        radio_layout.addWidget(self.right_gcode_link)
        
        radio_layout.addStretch()
        
        radio_layout.addWidget(self.left_radio)
        self.left_gcode_link = ClickableLabel("Edit")
        self.left_gcode_link.clicked.connect(self.edit_left_gcode)
        radio_layout.addWidget(self.left_gcode_link)
        
        orientation_layout.addLayout(radio_layout)
        
        layout.addWidget(orientation_group)
        
        # Preview area
        self.preview = FramePreview()
        layout.addWidget(self.preview, 1)
        
        return widget
    
    def create_right_panel(self):
        """Create right panel with lock and hinge configuration"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Lock configuration
        lock_group = ThemedGroupBox("Lock Configuration")
        lock_layout = QVBoxLayout()
        lock_group.setLayout(lock_layout)
        
        # Auto checkbox and position
        lock_auto_layout = QHBoxLayout()
        self.lock_auto_check = ThemedCheckBox("Auto")
        self.lock_auto_check.setChecked(True)
        self.lock_auto_check.stateChanged.connect(self.on_auto_state_changed)
        lock_auto_layout.addWidget(self.lock_auto_check)
        
        lock_auto_layout.addWidget(ThemedLabel("Position:"))
        self.lock_position_input = SimpleDollarLineEdit("lock_position", self)
        self.lock_position_input.setValidator(QDoubleValidator(0, self.MAX_FRAME_HEIGHT, 2))
        lock_auto_layout.addWidget(self.lock_position_input)
        
        self.lock_active_check = SimpleDollarCheckBox("lock_active", "Active", self)
        lock_auto_layout.addWidget(self.lock_active_check)
        
        lock_layout.addLayout(lock_auto_layout)
        
        # Lock Y offset with auto checkbox
        lock_y_offset_layout = QHBoxLayout()
        self.lock_y_auto_check = ThemedCheckBox("Auto")
        self.lock_y_auto_check.setChecked(True)
        self.lock_y_auto_check.stateChanged.connect(self.on_auto_state_changed)
        lock_y_offset_layout.addWidget(self.lock_y_auto_check)
        
        lock_y_offset_layout.addWidget(ThemedLabel("Y Offset:"))
        self.lock_y_offset_input = SimpleDollarLineEdit("lock_y_offset", self)
        self.lock_y_offset_input.setValidator(QDoubleValidator(-100, 100, 2))
        lock_y_offset_layout.addWidget(self.lock_y_offset_input)
        lock_layout.addLayout(lock_y_offset_layout)
        
        layout.addWidget(lock_group)
        
        # Hinge configuration
        hinge_group = ThemedGroupBox("Hinge Configuration")
        hinge_layout = QVBoxLayout()
        hinge_group.setLayout(hinge_layout)
        
        # Hinge count selector
        count_layout = QHBoxLayout()
        count_layout.addWidget(ThemedLabel("Number of Hinges:"))
        self.hinge_count_spin = ThemedSpinBox()
        self.hinge_count_spin.setRange(0, 4)
        self.hinge_count_spin.setValue(3)
        self.hinge_count_spin.valueChanged.connect(self.update_hinge_count)
        count_layout.addWidget(self.hinge_count_spin)
        count_layout.addStretch()
        hinge_layout.addLayout(count_layout)
        
        # Auto checkbox for positions
        self.hinge_auto_check = ThemedCheckBox("Auto-position")
        self.hinge_auto_check.setChecked(True)
        self.hinge_auto_check.stateChanged.connect(self.on_auto_state_changed)
        hinge_layout.addWidget(self.hinge_auto_check)
        
        # Hinge positions container
        self.hinge_positions_widget = QWidget()
        self.hinge_positions_layout = QVBoxLayout(self.hinge_positions_widget)
        self.hinge_positions_layout.setContentsMargins(0, 0, 0, 0)
        hinge_layout.addWidget(self.hinge_positions_widget)
        
        # Y offset for all hinges with auto checkbox
        y_offset_layout = QHBoxLayout()
        self.hinge_y_auto_check = ThemedCheckBox("Auto")
        self.hinge_y_auto_check.setChecked(True)
        self.hinge_y_auto_check.stateChanged.connect(self.on_auto_state_changed)
        y_offset_layout.addWidget(self.hinge_y_auto_check)
        
        y_offset_layout.addWidget(ThemedLabel("Y Offset (all):"))
        self.hinge_z_offset_input = SimpleDollarLineEdit("hinge_y_offset", self)
        self.hinge_z_offset_input.setValidator(QDoubleValidator(-100, 100, 2))
        y_offset_layout.addWidget(self.hinge_z_offset_input)
        hinge_layout.addLayout(y_offset_layout)
        
        layout.addWidget(hinge_group)
        
        # Execution order widget
        order_group = ThemedGroupBox("Component Order")
        order_layout = QVBoxLayout()
        order_group.setLayout(order_layout)
        
        self.order_widget = OrderWidget()
        self.order_widget.order_changed.connect(self.on_order_changed)
        order_layout.addWidget(self.order_widget, 1)
        
        layout.addWidget(order_group, 1)
        
        return widget
    
    def create_navigation(self):
        """Create bottom navigation buttons"""
        nav_layout = QHBoxLayout()
        nav_layout.addStretch()
        
        self.back_button = PurpleButton("← Back")
        self.next_button = GreenButton("Next →")
        
        nav_layout.addWidget(self.back_button)
        nav_layout.addWidget(self.next_button)
        
        return nav_layout
    
    def connect_signals(self):
        """Connect widget signals"""
        self.back_button.clicked.connect(self.back_clicked)
        self.next_button.clicked.connect(self.next_clicked)
        
        # Connect height input for min/max enforcement
        self.height_input.editingFinished.connect(self.enforce_height_limits)
    
    def setup_initial_values(self):
        """Setup initial values and hinge count"""
        # Update hinge count (will create hinge inputs and set proper defaults)
        self.update_hinge_count(3)  # Default to 3 hinges
        
        # Update UI from main_window
        self.update_ui_from_main_window()
        
        # Run initial auto-calculations
        self.run_auto_calculations()
    
    # MARK: - Auto-Calculation System (UNIFIED)
    
    def run_auto_calculations(self):
        """Unified auto-calculation system - runs in correct order"""
        # Prevent recursion
        if self._auto_calculation_running:
            return
        
        self._auto_calculation_running = True
        try:
            # Collect all changes to apply in batch
            changes = {}
            
            # 1. Lock Auto-Calculation
            if self.lock_auto_check.isChecked():
                lock_pos = self._calculate_lock_position()
                if lock_pos is not None:
                    changes["lock_position"] = round(lock_pos, 1)
            
            # 2. Lock Y Offset Auto-Calculation
            if self.lock_y_auto_check.isChecked():
                lock_y_offset = self._calculate_lock_y_offset()
                if lock_y_offset is not None:
                    changes["lock_y_offset"] = round(lock_y_offset, 1)
            
            # 3. Hinge Auto-Calculation
            if self.hinge_auto_check.isChecked():
                hinge_positions = self._calculate_hinge_positions()
                for i, pos in enumerate(hinge_positions):
                    if i < 4:  # Maximum 4 hinges
                        changes[f"hinge{i+1}_position"] = round(pos, 1)
            
            # 4. Hinge Y Offset Auto-Calculation
            if self.hinge_y_auto_check.isChecked():
                hinge_y_offset = self._calculate_hinge_y_offset()
                if hinge_y_offset is not None:
                    changes["hinge_y_offset"] = round(hinge_y_offset, 1)
            
            # 5. PM Auto-Calculation
            if self.pm_auto_check.isChecked():
                pm_positions = self._calculate_pm_positions()
                for i, pos in enumerate(pm_positions):
                    if i < 4:  # Maximum 4 PMs
                        changes[f"pm{i+1}_position"] = round(pos, 1)
            
            # Apply all changes at once to main_window
            if changes and self.main_window:
                self.main_window.update_dollar_variables(changes)
            
        finally:
            self._auto_calculation_running = False
    
    def _calculate_lock_position(self):
        """Calculate lock position: just 1050"""
        return 1050
    
    def _calculate_lock_y_offset(self):
        """Calculate lock y offset based on frame width and door width"""
        try:
            if not self.main_window:
                return None
            frame_width = self.main_window.get_dollar_variable("frame_width")
            door_width = self.main_window.get_dollar_variable("door_width")
            
            if frame_width is not None and door_width is not None:
                if door_width <= 45:
                    return frame_width - door_width / 2
                else:
                    return frame_width - 45 / 2
        except (ValueError, TypeError):
            pass
        return None
    
    def _calculate_hinge_y_offset(self):
        """Calculate hinge y offset - same algorithm as lock for now"""
        try:
            if not self.main_window:
                return None
            frame_width = self.main_window.get_dollar_variable("frame_width")
            door_width = self.main_window.get_dollar_variable("door_width")
            
            if frame_width is not None and door_width is not None:
                if door_width <= 45:
                    return frame_width - door_width / 2
                else:
                    return frame_width - 45 / 2
        except (ValueError, TypeError):
            pass
        return None
    
    def _calculate_hinge_positions(self):
        """Calculate hinge positions based on count and height (from old code logic)"""
        try:
            if not self.main_window:
                return []
            
            frame_height = self.main_window.get_dollar_variable("frame_height")
            count = self.hinge_count_spin.value()
            
            if not frame_height or frame_height <= 0 or count <= 0:
                return []
            
            if count == 1:
                return [frame_height / 2]
            elif count == 2:
                last_pos = 1800 if frame_height >= 2000 else frame_height - 200
                return [150.0, last_pos]
            elif count == 3:
                last_pos = 1800 if frame_height >= 2000 else frame_height - 200
                # Middle positioned so lower-to-middle is 1.5x upper-to-middle
                middle_pos = 150 + (last_pos - 150) / 2.5
                return [150.0, middle_pos, last_pos]
            elif count == 4:
                last_pos = 1800 if frame_height >= 2000 else frame_height - 200
                # Calculate with cascading 1.5x ratios
                total_distance = last_pos - 150
                d1 = total_distance / 4.75
                return [150.0, 150 + d1, 150 + d1 + 1.5*d1, last_pos]
        except (ValueError, TypeError):
            pass
        return []
    
    def _calculate_pm_positions(self):
        """Calculate PM positions using the complex algorithm from old code"""
        try:
            if not self.main_window:
                return []
            
            frame_height = self.main_window.get_dollar_variable("frame_height")
            pm1_pos = self.main_window.get_dollar_variable("pm1_position")
            
            if not frame_height or frame_height <= 0:
                return []
            
            # Use PM1 position as starting point
            if pm1_pos is None:
                pm1_pos = -25  # Default
            
            # Step 1: Calculate minimum distance from PM1 to PM2
            pm1_size = self.PM_CONFIG['sizes'][1]
            pm2_size = self.PM_CONFIG['sizes'][2]
            min_pm1_to_pm2 = pm1_size[0]/2 + pm2_size[0]/2  # 265/2 + 140/2 = 202.5
            
            # Define available range for PM2-4
            range_start = pm1_pos + min_pm1_to_pm2
            pm4_size = self.PM_CONFIG['sizes'][4]
            range_end = frame_height - pm4_size[1]/2  # height - 120/2
            
            if range_end <= range_start:
                # Not enough space - fallback to minimum distances
                return self._fallback_pm_positions(pm1_pos)
            
            # Step 2: Get obstacles (active lock and hinges)
            obstacles = []
            
            # Add lock obstacle if active
            lock_active = bool(self.main_window.get_dollar_variable("lock_active"))
            if lock_active:
                lock_pos = self.main_window.get_dollar_variable("lock_position")
                if lock_pos and lock_pos > 0:
                    safety = self.PM_CONFIG['lock_safety_distance']
                    obstacles.append((lock_pos - safety, lock_pos + safety))
            
            # Add hinge obstacles
            for i in range(4):
                hinge_active = bool(self.main_window.get_dollar_variable(f"hinge{i+1}_active"))
                if hinge_active:
                    hinge_pos = self.main_window.get_dollar_variable(f"hinge{i+1}_position")
                    if hinge_pos and hinge_pos > 0:
                        safety = self.PM_CONFIG['hinge_safety_distance']
                        obstacles.append((hinge_pos - safety, hinge_pos + safety))
            
            # Step 3: Calculate valid ranges by removing obstacle zones
            valid_ranges = self._calculate_valid_ranges(range_start, range_end, obstacles)
            
            # Step 4: Filter ranges that are too small
            min_size = self.PM_CONFIG['min_range_size']
            valid_ranges = [(start, end) for start, end in valid_ranges if end - start >= min_size]
            
            if not valid_ranges:
                # No valid ranges - fallback
                return self._fallback_pm_positions(pm1_pos)
            
            # Step 5: Place PM4 at end of last valid range
            pm4_pos = valid_ranges[-1][1]
            
            # Step 6: Find optimal positions for PM2 and PM3
            pm2_pos, pm3_pos = self._optimize_pm2_pm3_positions(pm1_pos, pm4_pos, valid_ranges)
            
            return [pm1_pos, pm2_pos, pm3_pos, pm4_pos]
            
        except (ValueError, TypeError):
            pass
        return self._fallback_pm_positions(pm1_pos if pm1_pos is not None else -25)
    
    def _calculate_valid_ranges(self, range_start, range_end, obstacles):
        """Calculate valid ranges by removing obstacle zones"""
        # Sort obstacles by start position
        obstacles = sorted(obstacles, key=lambda x: x[0])
        
        valid_ranges = []
        current_start = range_start
        
        for obstacle_start, obstacle_end in obstacles:
            # Only consider obstacles that overlap with our range
            obstacle_start = max(obstacle_start, range_start)
            obstacle_end = min(obstacle_end, range_end)
            
            if obstacle_start < range_end and obstacle_end > range_start:
                # This obstacle overlaps with our range
                if obstacle_start > current_start:
                    # Add range before this obstacle
                    valid_ranges.append((current_start, obstacle_start))
                
                # Move current start past this obstacle
                current_start = max(current_start, obstacle_end)
        
        # Add final range if there's space after last obstacle
        if current_start < range_end:
            valid_ranges.append((current_start, range_end))
        
        return valid_ranges
    
    def _optimize_pm2_pm3_positions(self, pm1_pos, pm4_pos, valid_ranges):
        """Find optimal positions for PM2 and PM3 that maximize distances"""
        # Calculate minimum distances
        pm2_size = self.PM_CONFIG['sizes'][2]
        pm3_size = self.PM_CONFIG['sizes'][3]
        min_pm1_to_pm2 = self.PM_CONFIG['sizes'][1][0]/2 + pm2_size[0]/2  # 202.5
        min_pm2_to_pm3 = pm2_size[0]/2 + pm3_size[0]/2  # 157.5
        min_pm3_to_pm4 = pm3_size[0]/2 + self.PM_CONFIG['sizes'][4][0]/2  # 207.5
        
        # Start with minimum distances
        pm2_pos = pm1_pos + min_pm1_to_pm2
        pm3_pos = pm4_pos - min_pm3_to_pm4
        
        # Check if we have enough space between PM2 and PM3
        if pm3_pos - pm2_pos < min_pm2_to_pm3:
            # Not enough space - use minimum distances from PM1
            pm2_pos = pm1_pos + min_pm1_to_pm2
            pm3_pos = pm2_pos + min_pm2_to_pm3
            return pm2_pos, pm3_pos
        
        # Try to place PM2 and PM3 in valid ranges
        best_pm2 = pm2_pos
        best_pm3 = pm3_pos
        
        # Check if PM2 position is in a valid range
        if not self._position_in_valid_ranges(pm2_pos, valid_ranges):
            # Find the closest valid range for PM2
            for start, end in valid_ranges:
                if start >= pm1_pos + min_pm1_to_pm2:
                    best_pm2 = start
                    break
        
        # Check if PM3 position is in a valid range  
        if not self._position_in_valid_ranges(pm3_pos, valid_ranges):
            # Find the closest valid range for PM3
            for start, end in reversed(valid_ranges):
                if end <= pm4_pos - min_pm3_to_pm4:
                    best_pm3 = end
                    break
        
        # Ensure minimum distance between PM2 and PM3
        if best_pm3 - best_pm2 < min_pm2_to_pm3:
            # Adjust positions to maintain minimum distance
            mid_point = (best_pm2 + best_pm3) / 2
            best_pm2 = mid_point - min_pm2_to_pm3 / 2
            best_pm3 = mid_point + min_pm2_to_pm3 / 2
            
            # Ensure they're still in valid ranges
            if not self._position_in_valid_ranges(best_pm2, valid_ranges):
                best_pm2 = pm1_pos + min_pm1_to_pm2
            if not self._position_in_valid_ranges(best_pm3, valid_ranges):
                best_pm3 = best_pm2 + min_pm2_to_pm3
        
        return best_pm2, best_pm3
    
    def _position_in_valid_ranges(self, position, valid_ranges):
        """Check if a position is within any valid range"""
        for start, end in valid_ranges:
            if start <= position <= end:
                return True
        return False
    
    def _fallback_pm_positions(self, pm1_pos):
        """Fallback to minimum distances when optimization fails"""
        # Calculate minimum distances
        min_distances = [
            self.PM_CONFIG['sizes'][1][0]/2 + self.PM_CONFIG['sizes'][2][0]/2,  # PM1-PM2: 202.5
            self.PM_CONFIG['sizes'][2][0]/2 + self.PM_CONFIG['sizes'][3][0]/2,  # PM2-PM3: 157.5
            self.PM_CONFIG['sizes'][3][0]/2 + self.PM_CONFIG['sizes'][4][0]/2   # PM3-PM4: 207.5
        ]
        
        positions = [pm1_pos]
        current_pos = pm1_pos
        
        for min_dist in min_distances:
            current_pos += min_dist
            positions.append(current_pos)
        
        return positions
    
    # MARK: - Event Handlers
    
    def on_variables_updated(self):
        """Handle variables updated from main_window"""
        # Update UI from main_window values
        self.update_ui_from_main_window()
        
        # Run auto-calculations (will be ignored if already running)
        self.run_auto_calculations()
        
        # Update preview and validation
        self.update_preview()
        self.run_validation()
    
    def on_auto_state_changed(self):
        """Handle auto checkbox state changes"""
        # Update enabled states
        self.update_enabled_states()
        
        # Run auto-calculations
        self.run_auto_calculations()
    
    def on_variable_changed(self, var_name, value):
        """Handle variable changes from simple dollar widgets"""
        if self.main_window and not self._auto_calculation_running:
            # Apply single change to main_window
            self.main_window.update_dollar_variable(var_name, value)
    
    def on_order_changed(self, order):
        """Handle execution order changes"""
        if not self.main_window or self._auto_calculation_running:
            return
        
        # Convert order to dollar variables
        changes = {}
        order_map = {}
        for idx, item_id in enumerate(order):
            order_map[item_id] = idx + 1
        
        changes["lock_order"] = order_map.get("lock", 0)
        for i in range(4):
            changes[f"hinge{i+1}_order"] = order_map.get(f"hinge{i+1}", 0)
        
        # Apply changes
        self.main_window.update_dollar_variables(changes)
    
    def update_hinge_count(self, count):
        """Update hinge position inputs based on count"""
        # Clear existing inputs
        while self.hinge_positions_layout.count():
            item = self.hinge_positions_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.hinge_inputs = []
        self.hinge_active_checks = []
        
        # Batch changes to apply to main_window
        changes = {}
        
        # Create new inputs for active hinges
        for i in range(count):
            hinge_layout = QHBoxLayout()
            
            hinge_layout.addWidget(ThemedLabel(f"Hinge {i+1}:"))
            
            # Position input
            position_input = SimpleDollarLineEdit(f"hinge{i+1}_position", self)
            position_input.setValidator(QDoubleValidator(0, self.MAX_FRAME_HEIGHT, 2))
            hinge_layout.addWidget(position_input)
            self.hinge_inputs.append(position_input)
            
            # Active checkbox
            active_check = SimpleDollarCheckBox(f"hinge{i+1}_active", "Active", self)
            hinge_layout.addWidget(active_check)
            self.hinge_active_checks.append(active_check)
            
            self.hinge_positions_layout.addLayout(hinge_layout)
            
            # Set new hinges as active by default (only if not already set)
            if self.main_window:
                current_active = self.main_window.get_dollar_variable(f"hinge{i+1}_active")
                if current_active is None or current_active == 0:
                    changes[f"hinge{i+1}_active"] = 1
        
        # Clear/deactivate unused hinges (for when count is reduced)
        for i in range(count, 4):  # From count to 4
            changes[f"hinge{i+1}_active"] = 0
            changes[f"hinge{i+1}_position"] = 0
        
        # Apply changes to main_window
        if changes and self.main_window:
            self.main_window.update_dollar_variables(changes)
        
        # Update enabled states and run calculations
        self.update_enabled_states()
        self.update_order_widget()
        self.run_auto_calculations()
    
    def update_enabled_states(self):
        """Update enabled/disabled states based on auto checkboxes"""
        # Lock position input
        self.lock_position_input.setEnabled(not self.lock_auto_check.isChecked())
        
        # Lock y offset input
        self.lock_y_offset_input.setEnabled(not self.lock_y_auto_check.isChecked())
        
        # Hinge position inputs
        hinge_auto = self.hinge_auto_check.isChecked()
        for input_field in getattr(self, 'hinge_inputs', []):
            input_field.setEnabled(not hinge_auto)
        
        # Hinge y offset input
        self.hinge_z_offset_input.setEnabled(not self.hinge_y_auto_check.isChecked())
        
        # PM position inputs (first PM always enabled, others depend on auto state)
        pm_auto = self.pm_auto_check.isChecked()
        for i, input_field in enumerate(self.pm_inputs):
            if i == 0:  # PM1 always editable
                input_field.setEnabled(True)
            else:
                input_field.setEnabled(not pm_auto)
    
    def update_order_widget(self):
        """Update order widget with active components"""
        if not self.main_window:
            return
        
        lock_active = bool(self.main_window.get_dollar_variable("lock_active"))
        hinge_count = len(getattr(self, 'hinge_inputs', []))
        hinge_active = []
        
        for i in range(4):
            active = bool(self.main_window.get_dollar_variable(f"hinge{i+1}_active"))
            hinge_active.append(active)
        
        self.order_widget.update_items(lock_active, hinge_count, hinge_active)
    
    def update_ui_from_main_window(self):
        """Update all UI elements from main_window values"""
        if not self.main_window:
            return
        
        # Update basic inputs
        dollar_vars = self.main_window.get_dollar_variable()
        
        # Update all simple dollar widgets
        for widget in [self.height_input, self.width_input, self.door_width_input, self.x_offset_input, self.y_offset_input, 
                      self.z_offset_input, self.lock_position_input, self.lock_y_offset_input,
                      self.hinge_z_offset_input] + self.pm_inputs:
            widget.update_from_main_window()
        
        # Update checkboxes
        self.lock_active_check.update_from_main_window()
        for check in getattr(self, 'hinge_active_checks', []):
            check.update_from_main_window()
        
        # Update radio buttons
        self.orientation_group.update_from_main_window()
        
        # Update hinge inputs if they exist
        for input_field in getattr(self, 'hinge_inputs', []):
            input_field.update_from_main_window()
    
    def update_preview(self):
        """Update preview with current configuration"""
        if not self.main_window:
            return
        
        config = self.get_current_config()
        self.preview.update_config(config)
    
    def get_current_config(self):
        """Get current configuration from main_window"""
        if not self.main_window:
            return {}
        
        dollar_vars = self.main_window.get_dollar_variable()
        
        # Build arrays
        hinge_positions = []
        hinge_active = []
        for i in range(4):
            pos = dollar_vars.get(f"hinge{i+1}_position", 0)
            active = bool(dollar_vars.get(f"hinge{i+1}_active", 0))
            hinge_positions.append(pos)
            hinge_active.append(active)
        
        pm_positions = []
        for i in range(4):
            pos = dollar_vars.get(f"pm{i+1}_position", 0)
            pm_positions.append(pos)
        
        return {
            'width': dollar_vars.get("frame_width", 45),
            'height': dollar_vars.get("frame_height", 2100),
            'lock_position': dollar_vars.get("lock_position", 1050),
            'lock_y_offset': dollar_vars.get("lock_y_offset", 0),
            'lock_active': bool(dollar_vars.get("lock_active", 1)),
            'hinge_positions': hinge_positions,
            'hinge_active': hinge_active,
            'hinge_y_offset': dollar_vars.get("hinge_y_offset", 0),
            'pm_positions': pm_positions,
            'orientation': dollar_vars.get("orientation", "right"),
        }
    
    # MARK: - Validation System
    
    def run_validation(self):
        """Run validation on PM positions and update UI styling"""
        if not self.main_window:
            return
        
        # Get current PM positions
        pm_positions = []
        for i in range(4):
            pos = self.main_window.get_dollar_variable(f"pm{i+1}_position") or 0
            pm_positions.append(pos)
        
        # Get frame height for boundary checking
        frame_height = self.main_window.get_dollar_variable("frame_height") or 0
        
        # Validate PM positions using old code logic
        min_distances = {
            '1-2': self.PM_CONFIG['sizes'][1][0]/2 + self.PM_CONFIG['sizes'][2][0]/2,  # 202.5
            '2-3': self.PM_CONFIG['sizes'][2][0]/2 + self.PM_CONFIG['sizes'][3][0]/2,  # 157.5
            '3-4': self.PM_CONFIG['sizes'][3][0]/2 + self.PM_CONFIG['sizes'][4][0]/2   # 207.5
        }
        
        # Track errors for each PM
        errors = [False] * 4
        
        # Check minimum distances between consecutive PMs
        distance_checks = [
            (0, 1, min_distances['1-2']),
            (1, 2, min_distances['2-3']),
            (2, 3, min_distances['3-4'])
        ]
        
        for i, j, min_dist in distance_checks:
            if pm_positions[j] - pm_positions[i] < min_dist:
                errors[i] = True
                errors[j] = True
        
        # Check distance from obstacles (lock and hinges)
        obstacles = []
        
        # Add lock position if active
        lock_active = bool(self.main_window.get_dollar_variable("lock_active"))
        if lock_active:
            lock_pos = self.main_window.get_dollar_variable("lock_position")
            if lock_pos and lock_pos > 0:
                obstacles.append(lock_pos)
        
        # Add active hinge positions
        for i in range(4):
            hinge_active = bool(self.main_window.get_dollar_variable(f"hinge{i+1}_active"))
            if hinge_active:
                hinge_pos = self.main_window.get_dollar_variable(f"hinge{i+1}_position")
                if hinge_pos and hinge_pos > 0:
                    obstacles.append(hinge_pos)
        
        # Check each PM against obstacles
        lock_safety = self.PM_CONFIG['lock_safety_distance'] 
        hinge_safety = self.PM_CONFIG['hinge_safety_distance']
        safety_distance = max(lock_safety, hinge_safety)
        
        for i, pm_pos in enumerate(pm_positions):
            for obstacle_pos in obstacles:
                if abs(pm_pos - obstacle_pos) < safety_distance:
                    errors[i] = True
        
        # Check if PM4 exceeds frame height constraint
        if frame_height > 0:
            pm4_height_limit = frame_height - self.PM_CONFIG['sizes'][4][1]/2  # PM4 height/2
            if pm_positions[3] > pm4_height_limit:
                errors[3] = True
        
        # Apply error styling to PM inputs
        for pm_input, has_error in zip(self.pm_inputs, errors):
            if hasattr(pm_input, 'set_error'):
                pm_input.set_error(has_error)
    
    def enforce_height_limits(self):
        """Enforce min/max height limits"""
        if not self.main_window:
            return
        
        try:
            current_height = self.main_window.get_dollar_variable("frame_height") or 0
            if current_height < self.MIN_FRAME_HEIGHT:
                self.main_window.update_dollar_variable("frame_height", self.MIN_FRAME_HEIGHT)
            elif current_height > self.MAX_FRAME_HEIGHT:
                self.main_window.update_dollar_variable("frame_height", self.MAX_FRAME_HEIGHT)
        except (ValueError, TypeError):
            self.main_window.update_dollar_variable("frame_height", self.MIN_FRAME_HEIGHT)
    
    # MARK: - G-code Editing
    
    def edit_right_gcode(self):
        """Edit right door G-code"""
        from ..dialogs.gcode_dialog import ProfileGCodeDialog
        from PySide6.QtWidgets import QDialog
        
        current_gcode = self.main_window.get_current_gcode("right_gcode")
        
        dialog = ProfileGCodeDialog("Right Door G-Code", current_gcode, self)
        if dialog.exec_() == QDialog.Accepted:
            new_gcode = dialog.get_gcode()
            self.main_window.update_current_gcodes("right_gcode", new_gcode)
    
    def edit_left_gcode(self):
        """Edit left door G-code"""
        from ..dialogs.gcode_dialog import ProfileGCodeDialog
        from PySide6.QtWidgets import QDialog
        
        current_gcode = self.main_window.get_current_gcode("left_gcode")
        
        dialog = ProfileGCodeDialog("Left Door G-Code", current_gcode, self)
        if dialog.exec_() == QDialog.Accepted:
            new_gcode = dialog.get_gcode()
            self.main_window.update_current_gcodes("left_gcode", new_gcode)


# MARK: - Simplified Dollar Variable Widgets

class SimpleDollarLineEdit(ThemedLineEdit):
    """Simplified line edit that sends changes to frame_tab without auto-syncing"""
    
    def __init__(self, variable_name, frame_tab, parent=None):
        super().__init__(parent=parent)
        self.variable_name = variable_name
        self.frame_tab = frame_tab
        self._updating = False
        self._has_error = False
        
        # Load initial value
        self.update_from_main_window()
        
        # Connect signal
        self.editingFinished.connect(self._on_editing_finished)
    
    def _format_value(self, value):
        """Format value for display"""
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)
    
    def _on_editing_finished(self):
        """Send change to frame_tab"""
        if self._updating or not self.frame_tab.main_window:
            return
        
        text = self.text().strip()
        
        # Convert to appropriate type
        try:
            if not text:
                new_value = 0
            elif '.' in text:
                new_value = float(text)
                if new_value.is_integer():
                    new_value = int(new_value)
            else:
                new_value = int(text)
        except ValueError:
            # Invalid input - revert
            self.update_from_main_window()
            return
        
        # Send to frame_tab
        self.frame_tab.on_variable_changed(self.variable_name, new_value)
    
    def update_from_main_window(self):
        """Update value from main_window"""
        if not self.frame_tab.main_window:
            return
        
        self._updating = True
        try:
            value = self.frame_tab.main_window.get_dollar_variable(self.variable_name)
            if value is not None:
                self.setText(self._format_value(value))
        finally:
            self._updating = False
    
    def set_error(self, has_error):
        """Set error state and update styling"""
        self._has_error = has_error
        if has_error:
            self.setStyleSheet("""
                QLineEdit {
                    background-color: #1d1f28;
                    color: #ffffff;
                    border: 2px solid #ff4444;
                    border-radius: 4px;
                    padding: 4px;
                }
                QLineEdit:focus {
                    border: 2px solid #ff4444;
                }
            """)
        else:
            # Reset to normal themed style
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
    
    def has_error(self):
        """Check if widget has error state"""
        return self._has_error


class SimpleDollarCheckBox(ThemedCheckBox):
    """Simplified checkbox that sends changes to frame_tab"""
    
    def __init__(self, variable_name, text, frame_tab, parent=None):
        super().__init__(text, parent=parent)
        self.variable_name = variable_name
        self.frame_tab = frame_tab
        self._updating = False
        
        # Load initial value
        self.update_from_main_window()
        
        # Connect signal
        self.stateChanged.connect(self._on_state_changed)
    
    def _on_state_changed(self):
        """Send change to frame_tab"""
        if self._updating:
            return
        
        new_value = 1 if self.isChecked() else 0
        self.frame_tab.on_variable_changed(self.variable_name, new_value)
        
        # Also update order widget if this is an active checkbox
        if self.variable_name.endswith('_active'):
            self.frame_tab.update_order_widget()
    
    def update_from_main_window(self):
        """Update value from main_window"""
        if not self.frame_tab.main_window:
            return
        
        self._updating = True
        try:
            value = self.frame_tab.main_window.get_dollar_variable(self.variable_name)
            if value is not None:
                self.setChecked(bool(value))
        finally:
            self._updating = False


class SimpleDollarRadioGroup:
    """Simplified radio group that sends changes to frame_tab"""
    
    def __init__(self, variable_name, frame_tab):
        self.variable_name = variable_name
        self.frame_tab = frame_tab
        self.button_group = QButtonGroup()
        self.value_map = {}
        self._updating = False
        
        # Connect signal
        self.button_group.buttonClicked.connect(self._on_button_clicked)
    
    def add_button(self, button, value):
        """Add button with value"""
        self.button_group.addButton(button)
        self.value_map[button] = value
        
        # Set initial state
        self.update_from_main_window()
    
    def _on_button_clicked(self, button):
        """Send change to frame_tab"""
        if self._updating:
            return
        
        value = self.value_map.get(button)
        if value is not None:
            self.frame_tab.on_variable_changed(self.variable_name, value)
    
    def update_from_main_window(self):
        """Update selection from main_window"""
        if not self.frame_tab.main_window:
            return
        
        self._updating = True
        try:
            current_value = self.frame_tab.main_window.get_dollar_variable(self.variable_name)
            for button, value in self.value_map.items():
                if value == current_value:
                    button.setChecked(True)
                    break
        finally:
            self._updating = False