from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class PreviewDialog(QDialog):

    idx_changed = pyqtSignal(dict)

    def __init__(self, deck, row=0, col=0, parent=None):
        super().__init__(parent)
        self.deck = deck
        self.idx = {'row': row, 'col': col}

        self.document = QTextDocument()
        self.preview = QTextBrowser()
        self.preview.setReadOnly(True)
        self.preview.setDocument(self.document)
        self.row_label = QLabel()
        self.col_label = QLabel()
        self.row_slider = QSlider(Qt.Horizontal)
        self.row_slider.setRange(1, len(self.deck))
        self.row_slider.setInvertedControls(True)
        self.prev_row_btn = QPushButton('<<')
        self.next_row_btn = QPushButton('>>')
        self.prev_col_btn = QPushButton('<')
        self.next_col_btn = QPushButton('>')
        zoom_in_btn = QPushButton('+')
        zoom_out_btn = QPushButton('-')

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.row_label, 0, 0, 1, 4)
        grid_layout.addWidget(self.col_label, 1, 0, 1, 4)
        grid_layout.addWidget(self.preview, 2, 0, 1, 4)
        grid_layout.addWidget(zoom_in_btn, 3, 0, 1, 2)
        grid_layout.addWidget(zoom_out_btn, 3, 2, 1, 2)
        grid_layout.addWidget(self.row_slider, 4, 0, 1, 4)
        grid_layout.addWidget(self.prev_row_btn, 5, 0)
        grid_layout.addWidget(self.prev_col_btn, 5, 1)
        grid_layout.addWidget(self.next_col_btn, 5, 2)
        grid_layout.addWidget(self.next_row_btn, 5, 3)
        button_box = QDialogButtonBox()
        button_box.setStandardButtons(QDialogButtonBox.Close)
        v_layout = QVBoxLayout()
        v_layout.addLayout(grid_layout)
        v_layout.addWidget(button_box)
        self.setLayout(v_layout)

        widget_list = [
            self.preview,
            self.row_slider,
            self.prev_row_btn,
            self.next_row_btn,
            self.prev_col_btn,
            self.next_col_btn,
            zoom_in_btn,
            zoom_out_btn,
            button_box.button(QDialogButtonBox.Close),
        ]
        for widget in widget_list:
            widget.setFocusPolicy(Qt.NoFocus)

        zoom_in_btn.clicked.connect(self.preview.zoomIn)
        zoom_out_btn.clicked.connect(self.preview.zoomOut)
        self.row_slider.valueChanged.connect(self.change_row)
        self.prev_row_btn.clicked.connect(self.prev_row)
        self.next_row_btn.clicked.connect(self.next_row)
        self.prev_col_btn.clicked.connect(self.prev_col)
        self.next_col_btn.clicked.connect(self.next_col)
        self.idx_changed.connect(self.go_to)
        button_box.rejected.connect(self.reject)

        self.setWindowTitle('Preview Card')

        QTimer.singleShot(0, lambda: self.change_idx(self.idx))

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Up:
            self.prev_col()
        elif key == Qt.Key_Down:
            self.next_col()
        elif key == Qt.Key_Left:
            self.prev_row()
        elif key == Qt.Key_Right:
            self.next_row()
        elif key == Qt.Key_Equal or key == Qt.Key_Plus:
            self.preview.zoomIn()
        elif key == Qt.Key_Minus:
            self.preview.zoomOut()
        elif key == Qt.Key_Escape:
            self.reject()

    def prev_row(self):
        idx = {'row': self.idx['row'] - 1, 'col': self.idx['col']}
        if idx['row'] < 0:
            reply = QMessageBox.question(self, 'Reached First Card',
                                         'You have reached the first card.\n'
                                         'Do you wish to view the last card?',
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                idx['row'] = len(self.deck) - 1
                self.change_idx(idx)
        else:
            self.change_idx(idx)

    def next_row(self):
        idx = {'row': self.idx['row'] + 1, 'col': self.idx['col']}
        if idx['row'] >= len(self.deck):
            reply = QMessageBox.question(self, 'Reached Last Card',
                                         'You have reached the last card.\n'
                                         'Do you wish to view the first card?',
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                idx['row'] = 0
                self.change_idx(idx)
        else:
            self.change_idx(idx)

    def prev_col(self):
        idx = {'row': self.idx['row'], 'col': self.idx['col'] - 1}
        if idx['col'] < 0:
            reply = QMessageBox.question(self, 'Reached First Side',
                                         'You have reached the first side.\n'
                                         'Do you wish to view the last side?',
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                idx['col'] = len(self.deck[idx['row']]) - 1
                self.change_idx(idx)
        else:
            self.change_idx(idx)

    def next_col(self):
        idx = {'row': self.idx['row'], 'col': self.idx['col'] + 1}
        if idx['col'] >= len(self.deck[idx['row']]):
            reply = QMessageBox.question(self, 'Reached Last Side',
                                         'You have reached the last side.\n'
                                         'Do you wish to view the first side?',
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                idx['col'] = 0
                self.change_idx(idx)
        else:
            self.change_idx(idx)

    def change_row(self, row_disp):
        idx = {'row': row_disp - 1, 'col': self.idx['col']}
        self.change_idx(idx)

    def change_idx(self, idx_to_validate):
        if 0 <= idx_to_validate['row'] < len(self.deck) \
                and 0 <= idx_to_validate['col'] < len(self.deck[idx_to_validate['row']]):
            self.idx = idx_to_validate
            self.idx_changed.emit(self.idx)

    def go_to(self, idx):
        self.show_preview_at(idx)
        self.handle_widget_view(idx)

    def show_preview_at(self, idx):
        value = self.deck[idx['row']][idx['col']]
        self.document.setHtml(value)

    def handle_widget_view(self, idx):
        row_text = 'Card: {} / {}'.format(idx['row'] + 1, len(self.deck))
        self.row_label.setText(row_text)
        col_text = 'Side: {}'.format(idx['col'] + 1)
        self.col_label.setText(col_text)
        self.row_slider.blockSignals(True)
        self.row_slider.setValue(idx['row'] + 1)
        self.row_slider.blockSignals(False)
        row_btn_enable = len(self.deck) > 1
        self.prev_row_btn.setEnabled(row_btn_enable)
        self.next_row_btn.setEnabled(row_btn_enable)
        prev_col_btn_enable = idx['col'] > 0
        next_col_btn_enable = idx['col'] < len(self.deck[idx['row']]) - 1
        self.prev_col_btn.setEnabled(prev_col_btn_enable)
        self.next_col_btn.setEnabled(next_col_btn_enable)
