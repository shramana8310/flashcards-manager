import collections
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import deck

PAGE_INTRO = 0
PAGE_SOURCE = 1
PAGE_DICT = 2
PAGE_TARGET = 3
PAGE_REVIEW = 4
PAGE_PROGRESS = 5
PAGE_RESULT = 6


class AddWizardError(Exception):
    pass


class QMyFileLineEdit(QLineEdit):

    def __init__(self, lst=[], file='', parent=None):
        super().__init__(parent)
        self.file = file
        self.lst = lst

    @pyqtProperty(str)
    def my_file(self):
        return self.file

    @pyqtProperty(list)
    def my_list(self):
        return self.lst


class QMyListWidget(QListWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

    @pyqtProperty(list)
    def my_list(self):
        return [self.item(i) for i in range(self.count())]


class IntroPage(QWizardPage):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('Add multiple cards')
        self.setSubTitle('This wizard will help you add multiple cards to your deck at once.')


class SourcePage(QWizardPage):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle('Select source text')
        self.setSubTitle('Select a text file that contains a list of words/phrases.\n'
                         'Words/Phrases should be entered line by line.')

        source_label = QLabel('Source text file: ')
        self.source_file_path_edit = QMyFileLineEdit()
        self.source_file_path_edit.setEnabled(False)
        browse_button = QPushButton('&Browse')

        v_layout = QVBoxLayout()
        v_layout.addWidget(source_label)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.source_file_path_edit)
        h_layout.addWidget(browse_button)
        v_layout.addLayout(h_layout)
        self.setLayout(v_layout)

        browse_button.clicked.connect(self.browse)

        self.registerField('source.wordlist', self.source_file_path_edit, 'my_list')
        self.registerField('source.file', self.source_file_path_edit, 'my_file')

    def browse(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Select source text', '.', 'Text files (*.txt)')
        if file:
            try:
                with open(file, 'r', encoding='utf-8') as fh:
                    word_list = [line.strip() for line in fh.readlines()]
                    if len(word_list) > 0:
                        self.source_file_path_edit.setText(QFileInfo(file).absoluteFilePath())
                        self.source_file_path_edit.file = file
                        self.source_file_path_edit.lst = word_list
                        self.completeChanged.emit()
                    else:
                        QMessageBox.warning(self, 'Invalid File', 'File must contain at least one word/phrase.')
            except (UnicodeError, IOError, EnvironmentError) as err:
                QMessageBox.warning(self, 'Error', str(err))

    def isComplete(self):
        if self.source_file_path_edit.file and self.source_file_path_edit.lst:
            return True
        else:
            return False


class DictPage(QWizardPage):

    def __init__(self, dictionaries, parent=None):
        super().__init__(parent)

        self.selected_dict_list = QMyListWidget()

        self.setTitle('Select dictionaries')
        self.setSubTitle('Select dictionaries to look up.')

        self.available_dict_list = QListWidget()
        for dictionary in dictionaries:
            item = QListWidgetItem(str(dictionary), self.available_dict_list)
            item.setData(Qt.UserRole, dictionary)
        self.add_btn = QPushButton('&Add')
        self.remove_btn = QPushButton('&Remove')

        h_layout = QHBoxLayout()
        v_left_layout = QVBoxLayout()
        v_left_layout.addWidget(QLabel('Available dictionaries: '))
        v_left_layout.addWidget(self.available_dict_list)
        v_center_layout = QVBoxLayout()
        v_center_layout.setAlignment(Qt.AlignVCenter)
        v_center_layout.addWidget(self.add_btn)
        v_center_layout.addWidget(self.remove_btn)
        v_right_layout = QVBoxLayout()
        v_right_layout.addWidget(QLabel('Selected dictionaries: '))
        v_right_layout.addWidget(self.selected_dict_list)

        h_layout.addLayout(v_left_layout)
        h_layout.addLayout(v_center_layout)
        h_layout.addLayout(v_right_layout)

        self.setLayout(h_layout)
        self.add_btn.clicked.connect(self.add_to_selected)
        self.remove_btn.clicked.connect(self.remove_from_selected)
        self.available_dict_list.currentRowChanged.connect(self.set_widgets_enabled)
        self.selected_dict_list.currentRowChanged.connect(self.set_widgets_enabled)

        self.registerField('dict.selected', self.selected_dict_list, 'my_list')

    def set_widgets_enabled(self):
        enable = True if self.available_dict_list.currentRow() >= 0 else False
        self.add_btn.setEnabled(enable)
        enable = True if self.selected_dict_list.currentRow() >= 0 else False
        self.remove_btn.setEnabled(enable)

    def add_to_selected(self):
        if len(self.selected_dict_list) == 4:
            QMessageBox.information(self, 'Maximum reached', 'You can select up to 4 dictionaries.')
        else:
            row = self.available_dict_list.currentRow()
            item = self.available_dict_list.item(row)
            self.available_dict_list.takeItem(row)
            self.selected_dict_list.insertItem(self.selected_dict_list.count(), item)
            self.completeChanged.emit()

    def remove_from_selected(self):
        row = self.selected_dict_list.currentRow()
        item = self.selected_dict_list.item(row)
        self.selected_dict_list.takeItem(row)
        self.available_dict_list.insertItem(self.available_dict_list.count(), item)
        self.completeChanged.emit()

    def initializePage(self):
        self.set_widgets_enabled()  # really necessary?

    def isComplete(self):
        if self.selected_dict_list:
            return True
        else:
            return False


class TargetPage(QWizardPage):

    def __init__(self, deck=None, parent=None):
        super().__init__(parent)
        self.deck = deck
        self.setTitle('Select target')
        self.setSubTitle('Select the target file.')

        self.cur_deck_radio = QRadioButton('Append search result to the &currently open file.')
        self.cur_deck_radio.setChecked(True)
        self.new_deck_radio = QRadioButton('Save search result to a &new file.')
        new_deck_label = QLabel('Path: ')
        self.new_deck_path_edit = QMyFileLineEdit()
        self.new_deck_path_edit.setReadOnly(True)
        self.browse_btn = QPushButton('&Browse')

        layout = QVBoxLayout()
        layout.addWidget(self.cur_deck_radio)
        layout.addWidget(self.new_deck_radio)
        layout.addWidget(new_deck_label)
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.new_deck_path_edit)
        h_layout.addWidget(self.browse_btn)
        layout.addLayout(h_layout)
        self.setLayout(layout)

        self.new_deck_radio.toggled.connect(self.set_widgets_enabled)
        self.new_deck_radio.toggled.connect(self.completeChanged)
        self.browse_btn.clicked.connect(self.browse)
        QTimer.singleShot(0, self.set_widgets_enabled)

        self.registerField('target.current_deck', self.cur_deck_radio)
        self.registerField('target.new_deck', self.new_deck_radio)
        self.registerField('target.new_deck_path', self.new_deck_path_edit, 'my_file')

    def browse(self):
        file, _ = QFileDialog.getSaveFileName(self, 'Select target file', '.',
                                              'TSV files ({})'.format(deck.TSV_FORMAT))
        if file:
            self.new_deck_path_edit.setText(QFileInfo(file).absoluteFilePath())
            self.new_deck_path_edit.file = file
            self.completeChanged.emit()

    def set_widgets_enabled(self):
        enable = self.new_deck_radio.isChecked()
        self.new_deck_path_edit.setEnabled(enable)
        self.browse_btn.setEnabled(enable)

    def isComplete(self):
        if self.cur_deck_radio.isChecked() and self.deck is not None:
            return True
        elif self.new_deck_radio.isChecked() and self.new_deck_path_edit.file is not None:
            return True
        return False


class ReviewPage(QWizardPage):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('Review job settings')
        self.setSubTitle('The settings you have specified are shown below. '
                         'Select Commit when ready to continue.')
        self.review_edit = QTextEdit()
        self.review_edit.setReadOnly(True)
        layout = QVBoxLayout()
        layout.addWidget(self.review_edit)
        self.setLayout(layout)
        self.setCommitPage(True)

    def initializePage(self):
        source_file = self.field('source.file')
        dict_selected = self.field('dict.selected')
        target_current_deck = self.field('target.current_deck')
        target_new_deck = self.field('target.new_deck')
        target_new_deck_path = self.field('target.new_deck_path')
        msg = '<b>Source: </b>{}<br />' \
              '<b>Selected dictionaries: </b>{}<br />'.format(source_file,
                                                        ', '.join([str(item.data(Qt.UserRole))
                                                                   for item in dict_selected]))
        if target_current_deck:
            msg += '<b>Target: </b>Current file<br />'
        elif target_new_deck:
            msg += '<b>Target: </b>{}<br />'.format(target_new_deck_path)
        else:
            raise AddWizardError('Unexpected AddWizard error')
        self.review_edit.setText(msg)


class AddCardsWorker(QThread):

    notifyProgress = pyqtSignal(int)
    resultReady = pyqtSignal(dict)

    def __init__(self, settings, deck):
        QThread.__init__(self)
        self.pause = False
        self.settings = settings
        self.deck = deck

    def run(self):
        target_current_deck = self.settings['target_current_deck']
        if target_current_deck:
            self.work_current_deck()
        else:
            self.work_new_deck()

    def work_current_deck(self):
        result = collections.defaultdict(int)
        result['cancelled'] = False
        dictionaries = self.settings['dict_selected']
        self.deck.col = max(len(dictionaries) + 1, self.deck.col)
        for idx, word in enumerate(self.settings['source_wordlist']):
            while self.is_paused():
                self.msleep(100)
            if self.isInterruptionRequested():
                break
            row = [word, ]
            for dictionary in dictionaries:
                value = ''
                try:
                    value = dictionary[word]
                    result['_'.join((str(id(dictionary)), 'success'))] += 1
                except KeyError:
                    result['_'.join((str(id(dictionary)), 'notfound'))] += 1
                except (UnicodeError, IOError, EnvironmentError) as err:
                    result['_'.join((str(id(dictionary)), 'error'))] += 1
                row.append(value)
            flashcard = deck.Flashcard(row)
            self.deck.add(flashcard)
            self.notifyProgress.emit(idx)
        if self.isInterruptionRequested():
            result['cancelled'] = True
        self.resultReady.emit(result)

    def work_new_deck(self):
        target_new_deck_path = self.settings['target_new_deck_path']
        result = collections.defaultdict(int)
        result['cancelled'] = False
        dictionaries = self.settings['dict_selected']
        new_deck = deck.Deck(col=len(dictionaries) + 1, file=target_new_deck_path)
        for idx, word in enumerate(self.settings['source_wordlist']):
            while self.is_paused():
                self.msleep(100)
            if self.isInterruptionRequested():
                break
            row = [word, ]
            for dictionary in dictionaries:
                value = ''
                try:
                    value = dictionary[word]
                    result['_'.join((str(id(dictionary)), 'success'))] += 1
                except KeyError:
                    result['_'.join((str(id(dictionary)), 'notfound'))] += 1
                except (UnicodeError, IOError, EnvironmentError) as err:
                    result['_'.join((str(id(dictionary)), 'error'))] += 1
                row.append(value)
            flashcard = deck.Flashcard(row)
            new_deck.add(flashcard)
            self.notifyProgress.emit(idx)
        new_deck.save()
        if self.isInterruptionRequested():
            result['cancelled'] = True
        self.resultReady.emit(result)

    def set_pause(self, pause):
        self.pause = pause

    def is_paused(self):
        return self.pause


class QMyResult(QWidget):

    def __init__(self, result={}, parent=None):
        super().__init__(parent)
        self.result = result

    @pyqtProperty(dict)
    def my_result(self):
        return self.result


class ProgressPage(QWizardPage):

    def __init__(self, deck=None, parent=None):
        super().__init__(parent)
        self.deck = deck
        self.setTitle('Work in progress')
        self.progress = QProgressBar()
        layout = QVBoxLayout()
        layout.addWidget(self.progress)
        self.setLayout(layout)
        self.result_obj = QMyResult()
        self.registerField('result', self.result_obj, 'my_result')

    def pause_work(self):
        self.worker.set_pause(True)
        reply = QMessageBox.question(self, 'Cancel', 'Cancel work?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.worker.requestInterruption()
        self.worker.set_pause(False)

    def work_finished(self, result):
        self.result_obj.result = result
        self.wizard().set_working(working=False, callback=None)
        self.wizard().button(QWizard.NextButton).setEnabled(True)
        self.wizard().next()

    def start_work(self):
        self.progress.setRange(0, len(self.field('source.wordlist')) - 1)
        self.wizard().button(QWizard.NextButton).setEnabled(False)
        self.worker = AddCardsWorker(self.zip_settings(), self.deck)
        # not sure this is the best
        self.wizard().set_working(working=True, callback=self.pause_work)
        self.wizard().button(QWizard.CancelButton).clicked.disconnect(self.wizard().reject)
        self.wizard().button(QWizard.CancelButton).clicked.connect(self.pause_work)
        self.worker.notifyProgress.connect(self.progress.setValue)
        self.worker.resultReady.connect(self.work_finished)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()

    def zip_settings(self):
        source_wordlist = self.field('source.wordlist')
        dict_selected = self.field('dict.selected')
        dict_selected = [item.data(Qt.UserRole) for item in dict_selected]
        target_current_deck = self.field('target.current_deck')
        target_new_deck = self.field('target.new_deck')
        target_new_deck_path = self.field('target.new_deck_path')
        settings = {
            'source_wordlist': source_wordlist,
            'dict_selected': dict_selected,
            'target_current_deck': target_current_deck,
            'target_new_deck': target_new_deck,
            'target_new_deck_path': target_new_deck_path,
        }
        return settings

    def initializePage(self):
        QTimer.singleShot(0, self.start_work)


class ResultPage(QWizardPage):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('Result')
        self.result_edit = QTextEdit()
        self.result_edit.setReadOnly(True)
        layout = QVBoxLayout()
        layout.addWidget(self.result_edit)
        self.setLayout(layout)

    def initializePage(self):
        result = self.field('result')
        if result['cancelled']:
            self.result_edit.setText('Job cancelled.')
        else:
            dict_selected = self.field('dict.selected')
            dict_selected = [item.data(Qt.UserRole) for item in dict_selected]
            target_current_deck = self.field('target.current_deck')
            target_new_deck_path = self.field('target.new_deck_path')
            msg = []
            if target_current_deck:
                msg.append('<b>Target: </b>Current Deck')
            else:
                msg.append('<b>Target: </b>{}'.format(target_new_deck_path))
            for dictionary in dict_selected:
                dictionary_name = '<b>{}</b>'.format(str(dictionary))
                success = 'Success: {}'.format(result['_'.join((str(id(dictionary)), 'success'))])
                not_found = 'Not Found: {}'.format(result['_'.join((str(id(dictionary)), 'notfound'))])
                error = 'Error: {}'.format(result['_'.join((str(id(dictionary)), 'error'))])
                msg.append('<br/>'.join((dictionary_name, success, not_found, error)))
            self.result_edit.setText('<br/><br/>'.join(msg))


class AddMultipleCardsWizard(QWizard):

    def __init__(self, dictionaries, deck=None, parent=None):
        super().__init__(parent)
        self.working = False
        self.callback = None

        page_intro = IntroPage(parent)
        page_source = SourcePage(parent)
        page_dict = DictPage(dictionaries, parent)
        page_target = TargetPage(deck, parent)
        page_review = ReviewPage(parent)
        page_progress = ProgressPage(deck, parent)
        page_result = ResultPage(parent)

        self.setPage(PAGE_INTRO, page_intro)
        self.setPage(PAGE_SOURCE, page_source)
        self.setPage(PAGE_DICT, page_dict)
        self.setPage(PAGE_TARGET, page_target)
        self.setPage(PAGE_REVIEW, page_review)
        self.setPage(PAGE_PROGRESS, page_progress)
        self.setPage(PAGE_RESULT, page_result)

        self.setStartId(PAGE_INTRO)
        self.setOption(QWizard.NoBackButtonOnLastPage)
        self.setOption(QWizard.NoCancelButtonOnLastPage)
        self.setWindowTitle('Add Multiple Cards')

    def set_working(self, working, callback):
        self.working = working
        self.callback = callback

    def is_working(self):
        return self.currentId() == PAGE_PROGRESS and self.working

    def closeEvent(self, event):
        if self.is_working() and self.callback is not None:
            event.ignore()
            self.callback()
