
import json
import os
from PySide6.QtGui import QPalette, QColor

class ThemeManager:
    """Manages application themes from JSON and QSS files"""
    
    def __init__(self, theme_name="purple"):
        self.theme_name = theme_name
        self.theme_dir = os.path.join("themes", theme_name)
        self.colors = {}
        self.control_styles = {}
        self.graph_styles = {}
        
    def load_theme(self):
        """Load theme files"""
        # Load color scheme
        color_file = os.path.join(self.theme_dir, f"{self.theme_name}.json")
        if os.path.exists(color_file):
            with open(color_file, 'r') as f:
                self.colors = json.load(f)
        
        # Load control styles
        control_file = os.path.join(self.theme_dir, "control_styles.json")
        if os.path.exists(control_file):
            with open(control_file, 'r') as f:
                self.control_styles = json.load(f)
        
        # Load graph styles
        graph_file = os.path.join(self.theme_dir, "graph_styles.json")
        if os.path.exists(graph_file):
            with open(graph_file, 'r') as f:
                self.graph_styles = json.load(f)
    
    def apply_palette(self, app):
        """Apply color palette to application"""
        if not self.colors:
            return
            
        palette = QPalette()
        
        # Window colors
        palette.setColor(QPalette.Window, QColor(self.colors["background"]["primary"]))
        palette.setColor(QPalette.WindowText, QColor(self.colors["text"]["primary"]))
        
        # Base colors
        palette.setColor(QPalette.Base, QColor(self.colors["background"]["secondary"]))
        palette.setColor(QPalette.AlternateBase, QColor(self.colors["background"]["tertiary"]))
        
        # Text colors
        palette.setColor(QPalette.Text, QColor(self.colors["text"]["primary"]))
        palette.setColor(QPalette.BrightText, QColor(self.colors["accent"]["error"]))
        
        # Button colors
        palette.setColor(QPalette.Button, QColor(self.colors["background"]["tertiary"]))
        palette.setColor(QPalette.ButtonText, QColor(self.colors["text"]["primary"]))
        
        # Highlight colors
        palette.setColor(QPalette.Highlight, QColor(self.colors["selection"]["background"]))
        palette.setColor(QPalette.HighlightedText, QColor(self.colors["text"]["primary"]))
        
        # Disabled colors
        palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(self.colors["text"]["disabled"]))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(self.colors["text"]["disabled"]))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(self.colors["text"]["disabled"]))
        
        app.setPalette(palette)
    
    def load_stylesheet(self):
        """Load QSS stylesheet"""
        qss_file = os.path.join(self.theme_dir, f"{self.theme_name}.qss")
        if os.path.exists(qss_file):
            with open(qss_file, 'r') as f:
                return f.read()
        return ""
    
    def apply_theme(self, app):
        """Apply complete theme to application"""
        self.load_theme()
        self.apply_palette(app)
        
        # Load and apply stylesheet
        stylesheet = self.load_stylesheet()
        if stylesheet:
            app.setStyleSheet(stylesheet)
        
        # Store theme data in app for access by other components
        app.theme_colors = self.colors
        app.control_styles = self.control_styles
        app.graph_styles = self.graph_styles