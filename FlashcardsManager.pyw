import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import pystardict
import deck, dictionaries, editbasicdlg, addwizard, previewdlg, dictdlg
import qrc_resources

__version__ = '1.0.0'
MSG_DURATION = 5000


class DictionaryLoader(QThread):
    def __init__(self, dictionaries, dict_paths, signal):
        QThread.__init__(self)
        self.dictionaries = dictionaries
        self.dict_paths = dict_paths
        self.signal = signal

    def run(self):
        for dict_path in self.dict_paths:
            try:
                dictionary = pystardict.Dictionary(dict_path)
                self.dictionaries.add(dictionary)
            except Exception as err:
                print(str(err))
        self.dictionaries.sort()
        self.signal.emit(True)


class FlashcardsManagerMainWindow(QMainWindow):

    file_available = pyqtSignal(bool)
    dictionaries_loaded = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.dictionary_loader = None
        self.dictionaries = dictionaries.DictionaryContainer()
        self.deck = deck.Deck()

        self.table = QTableWidget()
        self.setCentralWidget(self.table)

        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.showMessage('Ready', MSG_DURATION)

        file_new_action = self.create_action('&New File...', self.file_new, QKeySequence.New)
        file_open_action = self.create_action('&Open File...', self.file_open, QKeySequence.Open)
        self.file_save_action = self.create_action('&Save File', self.file_save, QKeySequence.Save)
        self.file_save_as_action = self.create_action('Save &As...', self.file_save_as, QKeySequence.SaveAs)
        file_import_action = self.create_action('&Import...', self.file_import)
        file_export_action = self.create_action('&Export...', self.file_export)
        self.file_close_action = self.create_action('&Close File', self.file_close, 'Ctrl+W')
        file_exit_action = self.create_action('E&xit', self.close)
        file_menu = self.menuBar().addMenu('&File')
        self.add_actions(file_menu, (file_new_action, file_open_action, self.file_save_action,
                                     self.file_save_as_action, None, self.file_close_action,
                                     None, file_exit_action))

        self.edit_add_action = self.create_action('&Add Card...', self.edit_add, 'Ctrl+I')
        self.edit_edit_action = self.create_action('&Edit Card...', self.edit_edit, 'Ctrl+E')
        self.edit_remove_action = self.create_action('&Remove Card...', self.edit_remove, 'Ctrl+R')
        self.edit_add_multiple_action = self.create_action('Add &Multiple Cards...', self.edit_add_multiple, 'Ctrl+M')
        self.edit_quick_add_action = self.create_action('&Quick Add...', self.edit_quick_add, 'Ctrl+Q')
        self.edit_settings_action = self.create_action('&Settings...', self.edit_settings)
        edit_menu = self.menuBar().addMenu('&Edit')
        self.add_actions(edit_menu, (self.edit_add_action, self.edit_edit_action, self.edit_remove_action,
                                     None, self.edit_add_multiple_action,
                                     None, self.edit_settings_action))

        self.view_preview_action = self.create_action('&Preview Flashcards...', self.view_preview, 'Ctrl+P')
        view_menu = self.menuBar().addMenu('&View')
        self.add_actions(view_menu, (self.view_preview_action, ))

        pref_dicts_action = self.create_action('&Dictionaries...', self.pref_dicts)
        pref_pref_action = self.create_action('&Preferences...', self.pref_pref)
        pref_menu = self.menuBar().addMenu('&Preferences')
        self.add_actions(pref_menu, (pref_dicts_action, ))

        help_doc_action = self.create_action('&Documentation', self.help_doc)
        help_check_updates_action = self.create_action('&Check for Updates...', self.help_check_updates)
        help_about_action = self.create_action('&About', self.help_about)
        help_menu = self.menuBar().addMenu('&Help')
        self.add_actions(help_menu, (help_about_action, ))

        self.table.itemDoubleClicked.connect(self.view_preview)
        QShortcut(QKeySequence('Return'), self.table, self.view_preview)

        file_available_action_list = [
            self.file_save_action,
            self.file_save_as_action,
            self.file_close_action,
            self.edit_add_action,
            self.edit_edit_action,
            self.edit_remove_action,
            self.edit_add_multiple_action,
            self.edit_quick_add_action,
            self.edit_settings_action,
            self.view_preview_action,
        ]
        for action in file_available_action_list:
            self.file_available.connect(action.setEnabled)

        self.dictionaries_loaded.connect(lambda _: self.statusBar().showMessage('Dictionaries loaded.', MSG_DURATION))
        dictionaries_loaded_action_list = [
            pref_dicts_action,
        ]
        for action in dictionaries_loaded_action_list:
            action.setEnabled(False)
            self.dictionaries_loaded.connect(lambda _: action.setEnabled(True))

        settings = QSettings()
        self.restoreGeometry(settings.value('MainWindow/Geometry', QByteArray()))
        self.restoreState(settings.value('MainWindow/State', QByteArray()))
        self.setWindowTitle('Flashcards Manager')
        QTimer.singleShot(0, self.load_initial_file)
        QTimer.singleShot(1, self.load_dictionaries)

    def create_action(self, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal='triggered'):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(':/{}.png'.format(icon)))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            getattr(action, signal).connect(slot)
        if checkable:
            action.setCheckable(True)
        return action

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def closeEvent(self, event):
        if self.ok_to_continue():
            settings = QSettings()
            settings.setValue('Dictionaries', [dictionary.path for dictionary in self.dictionaries])
            settings.setValue('LastFile', self.deck.file)
            settings.setValue('MainWindow/Geometry', self.saveGeometry())
            settings.setValue('MainWindow/State', self.saveState())
        else:
            event.ignore()

    def ok_to_continue(self):
        if self.deck.is_dirty():
            reply = QMessageBox.question(self, 'Unsaved Changes', 'Save unsaved changes?',
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                return False
            elif reply == QMessageBox.Yes:
                return self.file_save()
        return True

    def load_dictionaries(self):
        settings = QSettings()
        dict_paths = settings.value('Dictionaries', [], str)
        if dict_paths:
            self.dictionary_loader = DictionaryLoader(self.dictionaries, dict_paths, self.dictionaries_loaded)
            self.dictionary_loader.finished.connect(self.dictionary_loader.deleteLater)
            self.dictionary_loader.start()
        else:
            self.dictionaries_loaded.emit(True)

    def load_initial_file(self):
        settings = QSettings()
        file = settings.value('LastFile')
        if file and QFile.exists(file):
            ok, msg = self.deck.load(file)
            self.statusBar().showMessage(msg, MSG_DURATION)
            if ok:
                self.setWindowTitle('Flashcards Manager - {}'.format(file))
        self.update_table()
        self.file_available.emit(bool(file))

    def update_table(self):
        self.table.setColumnCount(self.deck.col)
        self.table.setRowCount(len(self.deck))
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        for row, flashcard in enumerate(self.deck):
            for col, side in enumerate(flashcard):
                if len(side) > 100:
                    side = side[:99] + '...'
                item = QTableWidgetItem(side)
                self.table.setItem(row, col, item)
        self.table.resizeColumnsToContents()

    def file_new(self):
        if not self.ok_to_continue():
            return
        col, ok = QInputDialog.getInt(self, 'New File', 'Please enter column size:',
                                      value=self.deck.col, min=1, max=5, step=1)
        if ok:
            self.deck.clear()
            self.statusBar().clearMessage()
            self.deck = deck.Deck(col=col)
            self.update_table()
            if ok:
                self.setWindowTitle('Flashcards Manager - {}'.format('New Deck'))
            self.file_available.emit(True)

    def file_open(self):
        if not self.ok_to_continue():
            return
        path = QFileInfo(self.deck.file).path() if self.deck.file else '.'
        file, _ = QFileDialog.getOpenFileName(self, 'Open', path,
                                              'TSV files ({})'.format(deck.TSV_FORMAT))
        if file:
            ok, msg = self.deck.load(file)
            self.statusBar().showMessage(msg, MSG_DURATION)
            if ok:
                self.setWindowTitle('Flashcards Manager - {}'.format(file))
            self.update_table()
            self.file_available.emit(True)

    def file_save(self):
        if not self.deck.file:
            return self.file_save_as()
        else:
            ok, msg = self.deck.save()
            self.statusBar().showMessage(msg, MSG_DURATION)
            return ok

    def file_save_as(self):
        file = self.deck.file if self.deck.file else '.'
        file, _ = QFileDialog.getSaveFileName(self, 'Save', file,
                                              'TSV files ({})'.format(deck.TSV_FORMAT))
        if file:
            if '.' not in file:
                file += '.txt'
            ok, msg = self.deck.save(file)
            self.statusBar().showMessage(msg, MSG_DURATION)
            if ok:
                self.setWindowTitle('Flashcards Manager - {}'.format(file))
            return ok
        return False

    def file_import(self):
        pass

    def file_export(self):
        pass

    def file_close(self):
        if not self.ok_to_continue():
            return
        self.deck.clear()
        self.statusBar().clearMessage()
        self.setWindowTitle('Flashcards Manager')
        self.update_table()
        self.file_available.emit(False)

    def current_flashcard(self):
        row = self.table.currentRow()
        if row > -1:
            return self.deck[row], row
        return None, row

    def edit_add(self):
        flashcard = deck.Flashcard(['' for _ in range(self.deck.col)])
        dlg = editbasicdlg.EditBasicDialog(self.deck, flashcard, parent=self)
        if dlg.exec_():
            self.update_table()

    def edit_edit(self):
        flashcard, row = self.current_flashcard()
        if flashcard is not None:
            dlg = editbasicdlg.EditBasicDialog(self.deck, flashcard, row, self)
            if dlg.exec_():
                self.update_table()

    def edit_remove(self):
        flashcard, row = self.current_flashcard()
        if flashcard is not None:
            reply = QMessageBox.question(self, 'Remove Card',
                                         'Remove card "{:.50}"?'.format(str(flashcard)),
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                del self.deck[row]
                self.update_table()

    def edit_add_multiple(self):
        if len(self.dictionaries) > 0:
            wizard = addwizard.AddMultipleCardsWizard(self.dictionaries, self.deck, self)
            if wizard.exec_():
                self.update_table()
        else:
            QMessageBox.information(self, 'Dictionary Not Available',
                                    'To add multiple cards, add dictionaries first.\n'
                                    'Preferences > Dictionaries...')

    def edit_quick_add(self):
        pass

    def edit_settings(self):
        col, ok = QInputDialog.getInt(self, 'Edit column size', 'Please enter column size:',
                                      value=self.deck.col, min=1, max=5, step=1)
        if ok:
            if len(self.deck) > 0 and col < self.deck.col:
                reply = QMessageBox.question(self, 'Edit column size',
                                             'Are you sure you want to change column size to {}?\n'
                                             'Any unsaved data will be lost.'.format(col),
                                             QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                if reply == QMessageBox.Yes:
                    self.deck.col = col
                    self.update_table()
            else:
                self.deck.col = col
                self.update_table()

    def view_preview(self):
        flashcard, row = self.current_flashcard()
        if row > -1:
            dlg = previewdlg.PreviewDialog(self.deck, row=row, col=0, parent=self)
            dlg.exec_()

    def pref_dicts(self):
        dlg = dictdlg.DictionaryDialog(self.dictionaries, self)
        dlg.exec_()

    def pref_pref(self):
        pass

    def help_doc(self):
        pass

    def help_check_updates(self):
        pass

    def help_about(self):
        msg = '''<b>Flashcards Manager</b> v{}
                 <p>Author: shramana8310@gmail.com<br>
                 GitHub repository: <a href='https://github.com/shramana8310/PyFlashcardsManager'>
                 https://github.com/shramana8310/PyFlashcardsManager</a></p>
                 <p>Icon made by Freepik from www.flaticon.com</p>
                 <p>This work is free software; you can redistribute it and/or modify it
                 under the terms of the GNU Lesser General Public License as published by the
                 Free Software Foundation; either version 2.1 of the License, or (at your option)
                 any later version.</p>
                 <p>This work is distributed in the hope that it will be useful, but <b>without
                 any warranty</b>; without even the implied warranty of <b>merchantability</b> or
                 <b>fitness for a particular purpose</b>. See the GNU Lesser General Public License
                 for more details.</p>'''.format(__version__)
        QMessageBox.about(self, 'About', msg)


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName('Shramana')
    app.setApplicationName('Flashcards Manager')
    app.setWindowIcon(QIcon(':/icon.png'))
    main_window = FlashcardsManagerMainWindow()
    main_window.show()
    app.exec_()

main()
