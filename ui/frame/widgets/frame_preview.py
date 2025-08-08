"""
Frame Preview Widget

Visual preview area for frame configuration with interactive drawing.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen, QBrush


class FramePreview(QWidget):
    """Visual preview area for frame configuration"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Default configuration values
        self.frame_height = 2100
        self.frame_width = 1200
        self.lock_position = 1050
        self.lock_y_offset = 0
        self.lock_active = True
        self.hinge_positions = []
        self.hinge_active = []
        self.hinge_y_offset = 0
        self.pm_positions = []
        self.orientation = "right"  # "right" or "left"
        
        self.setMinimumSize(400, 600)
        self.setStyleSheet("background-color: #f0f0f0;")
    
    def update_config(self, config):
        """Update preview with new configuration"""
        self.frame_height = config.get('height', 2100)
        self.frame_width = config.get('width', 45)
        self.lock_position = config.get('lock_position', 1050)
        self.lock_y_offset = config.get('lock_y_offset', 0)
        self.lock_active = config.get('lock_active', True)
        self.hinge_positions = config.get('hinge_positions', [])
        self.hinge_active = config.get('hinge_active', [])
        self.hinge_y_offset = config.get('hinge_y_offset', 0)
        self.pm_positions = config.get('pm_positions', [])
        self.orientation = config.get('orientation', 'right')
        self.update()
    
    def paintEvent(self, event):
        """Draw the frame preview"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate scaling to fit the widget
        widget_width = self.width()
        widget_height = self.height()
        
        # Frame dimensions in preview (scaled)
        scale = min(widget_height / (self.frame_height + 100), 
                   widget_width / (self.frame_width * 2 + 100))
        
        frame_height_scaled = self.frame_height * scale
        frame_width_scaled = self.frame_width * scale 
        frame_fixed_width = 50 * scale  
        
        # PMs dimensions
        large_PM = [300 * scale, 130 * scale]
        small_PM = [152 * scale, 82 * scale]
        
        frame_gap = small_PM[0]
        
        # Center the drawing
        start_x = widget_width / 2
        start_y = (widget_height - frame_height_scaled) / 2
        
        # Draw PMs large (behind frames)
        painter.setBrush(QBrush(QColor(128, 128, 128)))
        painter.setPen(QPen(QColor(64, 64, 64), 2))
        
        for pm_pos in self.pm_positions:
            pm_y = start_y + pm_pos * scale  # Position from top
            # Large rectangle below frames
            painter.drawRect(start_x - large_PM[0]/2, pm_y - large_PM[1]/2, large_PM[0], large_PM[1])
                
        # Draw frames
        # First frame (left)
        painter.setBrush(QBrush(QColor(160, 82, 45)))  # Light brown
        painter.setPen(QPen(QColor(101, 67, 33), 2))
        painter.drawRect(start_x - frame_gap/2 - frame_fixed_width, start_y, 
                        frame_fixed_width, frame_height_scaled)
        
        painter.setBrush(QBrush(QColor(139, 69, 19)))  # Dark brown
        painter.drawRect(start_x - frame_gap/2, start_y, 
                        frame_width_scaled, frame_height_scaled)
        
        # Second frame (right) - mirrored
        painter.setBrush(QBrush(QColor(139, 69, 19)))  # Dark brown
        painter.drawRect(start_x + frame_gap/2 - frame_width_scaled, start_y, 
                        frame_width_scaled, frame_height_scaled)
        
        painter.setBrush(QBrush(QColor(160, 82, 45)))  # Light brown
        painter.drawRect(start_x + frame_gap/2, start_y, 
                        frame_fixed_width, frame_height_scaled)
        
        # Draw PMs small (above frames)
        painter.setBrush(QBrush(QColor(192, 192, 192)))  # Lighter grey
        painter.setPen(QPen(QColor(64, 64, 64), 2))
        
        for pm_pos in self.pm_positions:
            pm_y = start_y + pm_pos * scale  # Position from top
            # Small rectangle above frames
            painter.drawRect(start_x - small_PM[0]/2, pm_y - small_PM[1]/2, 
                           small_PM[0], small_PM[1])
        
        # Draw lock
        lock_calculated_position = self.frame_height - self.lock_position
        if self.lock_active and lock_calculated_position > 0 and lock_calculated_position < self.frame_height:
            painter.setBrush(QBrush(QColor(0, 255, 0)))  # Green
            painter.setPen(QPen(QColor(0, 128, 0), 2))
            
            lock_y = start_y + lock_calculated_position * scale  # Position from top
            lock_width = 35 * scale
            lock_height = 180 * scale
            
            if self.orientation == "right":
                lock_x = start_x - frame_gap/2 - lock_width/2 + self.lock_y_offset*scale
            else:  # left
                lock_x = start_x + frame_gap/2 - lock_width/2 - self.lock_y_offset*scale
            
            painter.drawRect(lock_x, lock_y - lock_height/2, lock_width, lock_height)
        
        # Draw hinges
        painter.setBrush(QBrush(QColor(0, 0, 255)))  # Blue
        painter.setPen(QPen(QColor(0, 0, 128), 2))
        
        for i, (hinge_pos, active) in enumerate(zip(self.hinge_positions, self.hinge_active)):
            if active and hinge_pos > 0:
                hinge_y = start_y + hinge_pos * scale  # Position from top
                hinge_width = 20 * scale
                hinge_height = 80 * scale
                
                if self.orientation == "right":
                    hinge_x = start_x + frame_gap/2 - hinge_width/2 - self.hinge_y_offset*scale
                else:  # left
                    hinge_x = start_x - frame_gap/2 - hinge_width/2 + self.hinge_y_offset*scale
                
                painter.drawRect(hinge_x, hinge_y - hinge_height/2, hinge_width, hinge_height)