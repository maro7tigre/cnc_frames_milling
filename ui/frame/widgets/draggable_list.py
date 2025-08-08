"""
Draggable List Widget

Custom list widget with drag and drop reordering capabilities.
"""

from PySide6.QtWidgets import QListWidget
from PySide6.QtCore import Qt, Signal


class DraggableListWidget(QListWidget):
    """Custom list widget with drag and drop reordering"""
    
    order_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QListWidget.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QListWidget.SingleSelection)
        
        # Apply styling
        self.setStyleSheet("""
            QListWidget {
                background-color: #1d1f28;
                color: #ffffff;
                border: 1px solid #6f779a;
                border-radius: 4px;
                padding: 4px;
                outline: none;
            }
            QListWidget::item {
                background-color: #44475c;
                border: 1px solid #6f779a;
                border-radius: 3px;
                padding: 6px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: #BB86FC;
                color: #1d1f28;
                border: 1px solid #BB86FC;
            }
            QListWidget::item:hover {
                background-color: #6f779a;
                border: 1px solid #8b95c0;
            }
        """)
    
    def dropEvent(self, event):
        """Handle drop event and emit signal"""
        super().dropEvent(event)
        self.order_changed.emit()