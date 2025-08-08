import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from ui.main_window import MainWindow
from theme_manager import ThemeManager

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("CNC Frame Wizard")

    # Apply theme with ThemeManager
    theme = ThemeManager("purple")  # Just change "purple" to another theme name
    theme.apply_theme(app)

    # Set dark palette for Linux compatibility
    palette = QPalette()
    dark_color = QColor("#282a36")
    palette.setColor(QPalette.Window, dark_color)
    palette.setColor(QPalette.Base, dark_color)
    palette.setColor(QPalette.Button, dark_color)
    palette.setColor(QPalette.WindowText, QColor("white"))
    palette.setColor(QPalette.Text, QColor("white"))
    palette.setColor(QPalette.ButtonText, QColor("white"))
    app.setPalette(palette)

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
