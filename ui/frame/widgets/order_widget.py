"""
Order Widget

Resizable widget for configuring lock and hinge execution order.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidgetItem
from PySide6.QtCore import Qt, Signal
from ...widgets.themed_widgets import ThemedLabel, PurpleButton
from .draggable_list import DraggableListWidget


class OrderWidget(QWidget):
    """Resizable widget for configuring lock and hinge execution order"""
    
    order_changed = Signal(list)  # Emits list of items in order
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = ThemedLabel("Execution Order")
        title.setStyleSheet("QLabel { font-weight: bold; padding: 5px; }")
        layout.addWidget(title)
        
        # Instructions
        instructions = ThemedLabel("Drag items to reorder execution sequence:")
        instructions.setStyleSheet("QLabel { color: #bdbdc0; font-size: 11px; }")
        layout.addWidget(instructions)
        
        # Draggable list - now resizable by user
        self.order_list = DraggableListWidget()
        self.order_list.setMinimumHeight(100)  # Minimum height
        self.order_list.order_changed.connect(self.emit_order_changed)
        layout.addWidget(self.order_list, 1)  # Give it stretch factor
        
        # Control buttons
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)
        
        self.move_up_btn = PurpleButton("↑ Up")
        self.move_up_btn.clicked.connect(self.move_up)
        self.move_up_btn.setStyleSheet("""
            QPushButton {
                background-color: #1d1f28;
                color: #BB86FC;
                border: 1px solid #BB86FC;
                border-radius: 3px;
                padding: 4px 8px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #000000;
                color: #9965DA;
                border: 1px solid #9965DA;
            }
            QPushButton:pressed {
                background-color: #BB86FC;
                color: #1d1f28;
            }
        """)
        button_layout.addWidget(self.move_up_btn)
        
        self.move_down_btn = PurpleButton("↓ Down")
        self.move_down_btn.clicked.connect(self.move_down)
        self.move_down_btn.setStyleSheet("""
            QPushButton {
                background-color: #1d1f28;
                color: #BB86FC;
                border: 1px solid #BB86FC;
                border-radius: 3px;
                padding: 4px 8px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #000000;
                color: #9965DA;
                border: 1px solid #9965DA;
            }
            QPushButton:pressed {
                background-color: #BB86FC;
                color: #1d1f28;
            }
        """)
        button_layout.addWidget(self.move_down_btn)
        
        button_layout.addStretch()
    
    def update_items(self, lock_active, hinge_count, hinge_active):
        """Update the list based on active components"""
        self.order_list.clear()
        
        # Add lock if active
        if lock_active:
            item = QListWidgetItem("Lock")
            item.setData(Qt.UserRole, "lock")
            self.order_list.addItem(item)
        
        # Add active hinges
        for i in range(hinge_count):
            if i < len(hinge_active) and hinge_active[i]:
                item = QListWidgetItem(f"Hinge {i+1}")
                item.setData(Qt.UserRole, f"hinge{i+1}")
                self.order_list.addItem(item)
        
        self.emit_order_changed()
    
    def move_up(self):
        """Move selected item up"""
        current_row = self.order_list.currentRow()
        if current_row > 0:
            item = self.order_list.takeItem(current_row)
            self.order_list.insertItem(current_row - 1, item)
            self.order_list.setCurrentRow(current_row - 1)
            self.emit_order_changed()
    
    def move_down(self):
        """Move selected item down"""
        current_row = self.order_list.currentRow()
        if current_row < self.order_list.count() - 1:
            item = self.order_list.takeItem(current_row)
            self.order_list.insertItem(current_row + 1, item)
            self.order_list.setCurrentRow(current_row + 1)
            self.emit_order_changed()
    
    def emit_order_changed(self):
        """Emit the current order"""
        order = []
        for i in range(self.order_list.count()):
            item = self.order_list.item(i)
            order.append(item.data(Qt.UserRole))
        self.order_changed.emit(order)
    
    def get_order(self):
        """Get current execution order"""
        order = []
        for i in range(self.order_list.count()):
            item = self.order_list.item(i)
            order.append(item.data(Qt.UserRole))
        return order
    
    def set_order(self, order_list):
        """Set the execution order"""
        self.order_list.clear()
        
        for item_id in order_list:
            if item_id == "lock":
                item = QListWidgetItem("Lock")
                item.setData(Qt.UserRole, "lock")
                self.order_list.addItem(item)
            elif item_id.startswith("hinge"):
                hinge_num = item_id.replace("hinge", "")
                item = QListWidgetItem(f"Hinge {hinge_num}")
                item.setData(Qt.UserRole, item_id)
                self.order_list.addItem(item)