from PyQt5.QtWidgets import *
import deck


class EditBasicDialog(QDialog):

    def __init__(self, deck, flashcard, row=-1, parent=None):
        super().__init__(parent)

        self.deck = deck
        self.flashcard = flashcard
        self.row = row

        self.edits = []

        self.tab = QTabWidget()
        for col, side in enumerate(flashcard):
            edit = QPlainTextEdit(side)
            self.edits.append(edit)
            layout = QVBoxLayout()
            layout.addWidget(QLabel('Value:'))
            layout.addWidget(edit)
            widget = QWidget()
            widget.setLayout(layout)
            self.tab.addTab(widget, 'Side {}'.format(col + 1))

        button_box = QDialogButtonBox()
        button_box.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        layout = QVBoxLayout()
        layout.addWidget(self.tab)
        layout.addWidget(button_box)
        self.setLayout(layout)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        self.setWindowTitle('Edit Card')

    def accept(self):
        flashcard = deck.Flashcard([edit.toPlainText() for edit in self.edits])
        if self.row == -1:
            self.deck.add(flashcard)
        else:
            self.deck[self.row] = flashcard
        QDialog.accept(self)
