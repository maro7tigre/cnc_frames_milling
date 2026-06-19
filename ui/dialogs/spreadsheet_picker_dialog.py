"""
Spreadsheet Picker Dialog

Reads a spreadsheet file (.xlsx, .ods, .csv), displays rows as selectable cards,
and applies the chosen row's values to the app's dollar variables.
"""

import csv
import os

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget,
    QPushButton, QLabel, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


def read_spreadsheet(path: str) -> list[list[str]]:
    """Return all rows as lists of strings. First row is the header."""
    ext = os.path.splitext(path)[1].lower()

    if ext == ".csv":
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            return [row for row in reader]

    if ext in (".xlsx", ".xlsm", ".xltx", ".xltm"):
        import openpyxl
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb.active
        rows = []
        for row in ws.iter_rows(values_only=True):
            rows.append([("" if v is None else str(v)) for v in row])
        return rows

    if ext == ".ods":
        from odf.opendocument import load as ods_load
        from odf.table import Table, TableRow, TableCell
        from odf.text import P
        doc = ods_load(path)
        rows = []
        for sheet in doc.spreadsheet.getElementsByType(Table):
            for tr in sheet.getElementsByType(TableRow):
                cells = tr.getElementsByType(TableCell)
                row = []
                for cell in cells:
                    repeat = int(cell.getAttribute("numbercolumnsrepeated") or 1)
                    ps = cell.getElementsByType(P)
                    text = "".join(str(p) for p in ps) if ps else ""
                    row.extend([text] * repeat)
                rows.append(row)
            break  # first sheet only
        return rows

    raise ValueError(f"Unsupported file format: {ext}")


class RowCard(QFrame):
    """A single selectable row card."""

    STATE_DEFAULT = "default"
    STATE_LAST = "last"
    STATE_SELECTED = "selected"

    def __init__(self, row_index: int, values: list[str], headers: list[str], parent=None):
        super().__init__(parent)
        self.row_index = row_index
        self._state = self.STATE_DEFAULT
        self._on_click = None

        self.setFrameShape(QFrame.StyledPanel)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(12)

        # Row number badge
        num_label = QLabel(f"#{row_index}")
        num_label.setFixedWidth(36)
        num_label.setAlignment(Qt.AlignCenter)
        num_label.setFont(QFont("Consolas", 12, QFont.Bold))
        num_label.setStyleSheet("color: #6f779a;")
        layout.addWidget(num_label)

        # Column values — no repeated header label, just the value
        for i, val in enumerate(values):
            val_lbl = QLabel(val if val else "—")
            val_lbl.setFont(QFont("Consolas", 11))
            val_lbl.setStyleSheet("color: #ffffff;")
            layout.addWidget(val_lbl, 1)

        self._apply_style()

    def set_state(self, state: str):
        self._state = state
        self._apply_style()

    def _apply_style(self):
        colors = {
            self.STATE_DEFAULT:  ("transparent", "#44475a"),
            self.STATE_LAST:     ("transparent", "#4a9eff"),
            self.STATE_SELECTED: ("transparent", "#23c87b"),
        }
        bg, border = colors.get(self._state, colors[self.STATE_DEFAULT])
        self.setStyleSheet(f"""
            RowCard {{
                background-color: {bg};
                border: 2px solid {border};
                border-radius: 5px;
                margin: 2px 0;
            }}
            RowCard:hover {{
                background-color: #3a3c4e;
            }}
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._on_click:
            self._on_click(self.row_index)
        super().mousePressEvent(event)

    def set_click_handler(self, fn):
        self._on_click = fn


class SpreadsheetPickerDialog(QDialog):
    """
    Dialog that displays rows from a spreadsheet so the user can pick one
    and apply its values to the app's dollar variables.
    """

    def __init__(self, file_path: str, known_variables: dict,
                 last_row_index: int | None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pick a Row")
        self.setModal(True)
        self.resize(900, 560)

        self._known_variables = known_variables
        self._last_row_index = last_row_index
        self._selected_index = None  # index into self._data_rows (0-based)
        self._cards: list[RowCard] = []

        self.picked_row_index = None   # set on confirm (0-based into data rows)
        self.values_to_apply: dict = {}

        self.setStyleSheet("""
            SpreadsheetPickerDialog {
                background-color: #282a36;
                color: #ffffff;
            }
            QLabel { color: #ffffff; background-color: transparent; }
            QPushButton {
                background-color: #1d1f28;
                color: #BB86FC;
                border: 2px solid #BB86FC;
                border-radius: 4px;
                padding: 6px 14px;
                min-width: 90px;
            }
            QPushButton:hover {
                background-color: #000000;
                color: #9965DA;
                border: 2px solid #9965DA;
            }
            QPushButton:pressed {
                background-color: #BB86FC;
                color: #1d1f28;
            }
            QPushButton:disabled {
                color: #6f779a;
                border: 2px solid #6f779a;
            }
            QScrollArea {
                background-color: #1d1f28;
                border: 1px solid #44475a;
                border-radius: 4px;
            }
        """)

        self._build_ui(file_path)

    def _build_ui(self, file_path: str):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(12, 12, 12, 12)

        # Title
        title = QLabel("Select a row to import")
        title.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(title)

        # File name hint
        hint = QLabel(os.path.basename(file_path))
        hint.setFont(QFont("Consolas", 9))
        hint.setStyleSheet("color: #6f779a;")
        layout.addWidget(hint)

        # Error label (hidden by default)
        self._error_lbl = QLabel()
        self._error_lbl.setStyleSheet("color: #ff5555;")
        self._error_lbl.setVisible(False)
        layout.addWidget(self._error_lbl)

        # Scroll area for rows
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll, 1)

        container = QWidget()
        container.setStyleSheet("background-color: #1d1f28;")
        self._rows_layout = QVBoxLayout(container)
        self._rows_layout.setContentsMargins(6, 6, 6, 6)
        self._rows_layout.setSpacing(4)
        scroll.setWidget(container)

        # Load data
        try:
            all_rows = read_spreadsheet(file_path)
            self._populate_rows(all_rows)
        except Exception as exc:
            self._error_lbl.setText(f"Could not read file: {exc}")
            self._error_lbl.setVisible(True)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self._confirm_btn = QPushButton("Confirm")
        self._confirm_btn.setEnabled(False)
        self._confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #1d1f28;
                color: #23c87b;
                border: 2px solid #23c87b;
                border-radius: 4px;
                padding: 6px 14px;
                min-width: 90px;
            }
            QPushButton:hover {
                background-color: #000000;
                color: #1a945b;
                border: 2px solid #1a945b;
            }
            QPushButton:pressed {
                background-color: #23c87b;
                color: #1d1f28;
            }
            QPushButton:disabled {
                color: #6f779a;
                border: 2px solid #6f779a;
            }
        """)
        self._confirm_btn.clicked.connect(self._on_confirm)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(self._confirm_btn)
        layout.addLayout(btn_row)

    def _populate_rows(self, all_rows: list[list[str]]):
        if not all_rows:
            self._error_lbl.setText("The file appears to be empty.")
            self._error_lbl.setVisible(True)
            return

        # Normalize: pad all rows to the same width
        width = max(len(r) for r in all_rows)
        all_rows = [r + [""] * (width - len(r)) for r in all_rows]

        header = all_rows[0]
        self._data_rows = all_rows[1:]
        self._header = header

        # Build a mapping from column index → variable name (only recognized ones)
        self._col_map: dict[int, str] = {}
        for i, h in enumerate(header):
            clean = h.strip().lstrip("$")
            if clean and clean in self._known_variables:
                self._col_map[i] = clean

        if not self._data_rows:
            self._error_lbl.setText("No data rows found (only a header row).")
            self._error_lbl.setVisible(True)
            return

        # Header labels row (not selectable)
        header_widget = QFrame()
        header_widget.setStyleSheet("background-color: #282a36; border: none;")
        h_layout = QHBoxLayout(header_widget)
        h_layout.setContentsMargins(8, 4, 8, 4)
        h_layout.setSpacing(12)

        spacer = QLabel("    ")
        spacer.setFixedWidth(32)
        h_layout.addWidget(spacer)

        for col in header:
            lbl = QLabel(col)
            lbl.setFont(QFont("Consolas", 9, QFont.Bold))
            lbl.setStyleSheet("color: #BB86FC;")
            h_layout.addWidget(lbl, 1)

        self._rows_layout.addWidget(header_widget)

        # Data row cards
        for i, row in enumerate(self._data_rows):
            card = RowCard(i + 1, row, header)
            card.set_click_handler(self._on_card_clicked)
            self._cards.append(card)
            self._rows_layout.addWidget(card)

        self._rows_layout.addStretch()

        # Mark last selected
        if self._last_row_index is not None:
            idx = self._last_row_index  # 0-based into _data_rows
            if 0 <= idx < len(self._cards):
                self._cards[idx].set_state(RowCard.STATE_LAST)

    def _on_card_clicked(self, row_number: int):
        """row_number is 1-based display number; card index is row_number-1."""
        idx = row_number - 1
        # Reset all cards
        for i, card in enumerate(self._cards):
            if i == idx:
                card.set_state(RowCard.STATE_SELECTED)
            elif self._last_row_index is not None and i == self._last_row_index:
                card.set_state(RowCard.STATE_LAST)
            else:
                card.set_state(RowCard.STATE_DEFAULT)

        self._selected_index = idx
        self._confirm_btn.setEnabled(True)

    def _on_confirm(self):
        if self._selected_index is None:
            return

        row = self._data_rows[self._selected_index]
        result = {}
        for col_i, var_name in self._col_map.items():
            if col_i < len(row):
                val = row[col_i].strip()
                if val:
                    result[var_name] = val
        self.values_to_apply = result
        self.picked_row_index = self._selected_index
        self.accept()
