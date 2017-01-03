import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class DictionaryLoader(QThread):
    def __init__(self, dictionaries, path, recursive, signal):
        QThread.__init__(self)
        self.dictionaries = dictionaries
        self.path = path
        self.recursive = recursive
        self.signal = signal

    def run(self):
        self.dictionaries.load(self.path, self.recursive)
        self.dictionaries.sort()
        self.signal.emit()


class DictionaryDialog(QDialog):

    dictionaries_changed = pyqtSignal()

    def __init__(self, dictionaries, parent=None):
        super().__init__(parent)

        self.dictionaries = dictionaries

        self.dict_list = QListWidget()
        self.path_edit = QTextEdit()
        self.path_edit.setReadOnly(True)

        add_btn = QPushButton('&Add')
        self.remove_btn = QPushButton('&Remove')

        grid_layout = QGridLayout()
        grid_layout.addWidget(QLabel('Available Dictionaries: '), 0, 0, 1, 2)
        grid_layout.addWidget(self.dict_list, 1, 0, 1, 2)
        grid_layout.addWidget(add_btn, 2, 0, 1, 1)
        grid_layout.addWidget(self.remove_btn, 2, 1, 1, 1)
        grid_layout.addWidget(QLabel('Selected Dictionary: '), 0, 2, 1, 2)
        grid_layout.addWidget(self.path_edit, 1, 2, 2, 2)
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        layout = QVBoxLayout()
        layout.addLayout(grid_layout)
        layout.addWidget(button_box)
        self.setLayout(layout)

        self.dictionaries_changed.connect(self.update_list)
        self.dict_list.itemClicked.connect(self.handle_item_clicked)
        button_box.rejected.connect(self.reject)
        add_btn.clicked.connect(self.add_dict)
        self.remove_btn.clicked.connect(self.remove_dict)

        self.setWindowTitle('Dictionaries')

        QTimer.singleShot(0, self.update_list)

    def handle_item_clicked(self, item):
        dictionary = item.data(Qt.UserRole)
        # pystardict-specific info
        text = '<p><b>Path:</b> <br>{}</p>' \
               '<p><b>Dictionary name:</b> <br>{}</p>' \
               '<p><b>Word count:</b> {}</p>' \
               '<p><b>Author:</b> {}</p>' \
               '<p><b>Email:</b> {}</p>' \
               '<p><b>Website:</b> {}</p>' \
               '<p><b>Description:</b> <br>{}</p>'.format(dictionary.path,
                                                          dictionary.ifo.bookname,
                                                          dictionary.ifo.wordcount,
                                                          dictionary.ifo.author,
                                                          dictionary.ifo.email,
                                                          dictionary.ifo.website,
                                                          dictionary.ifo.description)
        self.path_edit.setText(text)
        enable_remove_btn = item is not None
        self.remove_btn.setEnabled(enable_remove_btn)

    def update_list(self):
        self.dict_list.clear()
        for dictionary in self.dictionaries:
            item = QListWidgetItem(str(dictionary))
            item.setData(Qt.UserRole, dictionary)
            self.dict_list.addItem(item)
        enable_remove_btn = self.dict_list.currentItem() is not None
        self.remove_btn.setEnabled(enable_remove_btn)

    def add_dict(self):
        path = QFileDialog.getExistingDirectory(self, 'Open directory', '.',
                                                QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if os.path.exists(path):
            if len(list(filter(lambda filename: os.path.isdir(os.path.join(path, filename)),
                               os.listdir(path)))) > 0:
                recursive = QMessageBox.question(self, 'Find recursively?',
                                                 'Do you wish to find dictionary file recursively?',
                                                 QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes
            else:
                recursive = False
            progress_dlg = QDialog(self)
            layout = QVBoxLayout()
            layout.addWidget(QLabel('Please wait while loading...'))
            progress_dlg.setLayout(layout)
            progress_dlg.closeEvent = lambda event: event.ignore()
            dictionary_loader = DictionaryLoader(self.dictionaries, path, recursive, self.dictionaries_changed)
            dictionary_loader.finished.connect(dictionary_loader.deleteLater)
            dictionary_loader.finished.connect(progress_dlg.reject)
            dictionary_loader.start()
            progress_dlg.exec_()

    def remove_dict(self):
        item = self.dict_list.currentItem()
        dictionary = item.data(Qt.UserRole)
        if dictionary is not None:
            reply = QMessageBox.question(self, 'Remove dictionary',
                                         'Are you sure you want to remove '
                                         'the following dictionary?\n{}'.format(str(dictionary)),
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.dictionaries.remove(dictionary)
                self.dictionaries_changed.emit()
