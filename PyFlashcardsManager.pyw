import sys
import os
import csv
import pystardict
from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QDialogButtonBox, \
    QTextEdit, QGridLayout, QFileDialog, QMessageBox, QProgressDialog, QApplication
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class PrototypeDialog(QDialog):

    optionsChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.options = {'word_list': '', 'stardict': '', 'flashcards': ''}

        word_list_btn = QPushButton('단어 목록 파일')
        self.word_list_path = QLineEdit()
        self.word_list_path.setReadOnly(True)

        stardict_btn = QPushButton('스타딕 파일')
        self.stardict_path = QLineEdit()
        self.stardict_path.setReadOnly(True)

        flashcards_btn = QPushButton('단어장 파일')
        self.flashcards_path = QLineEdit()
        self.flashcards_path.setReadOnly(True)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok |
                                      QDialogButtonBox.Close)

        help_message = self.load_help_message()
        help_message_area = QTextEdit()
        help_message_area.setText(help_message)
        help_message_area.setReadOnly(True)

        layout = QGridLayout()

        layout.addWidget(word_list_btn, 0, 0)
        layout.addWidget(self.word_list_path, 0, 1)
        layout.addWidget(stardict_btn, 1, 0)
        layout.addWidget(self.stardict_path, 1, 1)
        layout.addWidget(flashcards_btn, 2, 0)
        layout.addWidget(self.flashcards_path, 2, 1)
        layout.addWidget(help_message_area, 3, 0, 1, 2, Qt.AlignCenter)
        layout.addWidget(button_box, 4, 0, 1, 2, Qt.AlignCenter)

        self.setLayout(layout)

        word_list_btn.clicked.connect(self.set_word_list_file)
        stardict_btn.clicked.connect(self.set_stardict_file)
        flashcards_btn.clicked.connect(self.set_flashcards_file)
        self.optionsChanged.connect(self.update_state)
        button_box.button(QDialogButtonBox.Ok).clicked.connect(
            self.validate_and_work)
        button_box.button(QDialogButtonBox.Close).clicked.connect(
            self.ask_and_close)

        self.setWindowTitle('Flashcards Manager 시험판')

    def load_help_message(self):
        try:
            with open('./res/help.txt', encoding='utf-8') as fi:
                return fi.read()
        except IOError:
            pass

    def set_word_list_file(self):
        file_name = QFileDialog.getOpenFileName(self, caption='단어 목록 파일', filter='텍스트 파일 (*.txt)',
                                                directory=os.path.expanduser('~'))[0]
        self.options['word_list'] = file_name
        self.optionsChanged.emit()

    def set_stardict_file(self):
        file_name = QFileDialog.getOpenFileName(self, caption='스타딕 파일', filter='스타딕 파일 (*.ifo)',
                                                directory=os.path.expanduser('~'))[0]
        self.options['stardict'] = file_name[:-4]
        self.optionsChanged.emit()

    def set_flashcards_file(self):
        file_name = QFileDialog.getSaveFileName(self, caption='단어장 파일', filter='텍스트 파일 (*.txt)',
                                                directory=os.path.expanduser('~'))[0]
        self.options['flashcards'] = file_name
        self.optionsChanged.emit()

    def update_state(self):
        self.word_list_path.setText(self.options['word_list'])
        self.stardict_path.setText(self.options['stardict'])
        self.flashcards_path.setText(self.options['flashcards'])

    def validate_and_work(self):
        for value in self.options.values():
            if not value:
                QMessageBox.warning(self, '파일 지정', '파일을 지정하십시오.')
                return
        if self.options['word_list'] == self.options['flashcards']:
            QMessageBox.warning(self, '파일 지정 오류', '단어 목록 파일과 단어장 파일은 다른 파일이어야 합니다.')
            return
        try:
            with open(self.options['word_list'], encoding='utf-8') as word_list_file:
                word_list = [line.strip() for line in word_list_file.readlines()]
            stardict = pystardict.Dictionary(self.options['stardict'])
        except Exception as err:
            QMessageBox.warning(self, 'Error', str(err))
        else:
            answer = QMessageBox.question(self, '확인',
                                          '작업을 진행해도 좋습니까?\n\n'
                                          '단어 목록: {word_list}\n'
                                          '스타딕: {stardict}\n'
                                          '단어장: {flashcards}'.format(
                                              **self.options))
            if answer == QMessageBox.Yes:
                self.worker = PrototypeWorker(word_list, stardict, self.options['flashcards'])

                self.progress = QProgressDialog()
                self.progress.setWindowTitle('작업중...')
                self.progress.setRange(0, len(word_list) - 1)
                self.progress.setWindowModality(Qt.WindowModal)

                self.progress.canceled.connect(self.worker.requestInterruption)
                self.worker.notifyProgress.connect(self.progress.setValue)
                self.worker.resultReady.connect(self.handle_result)
                self.worker.finished.connect(self.worker.deleteLater)

                self.progress.show()
                self.worker.start()

    def handle_result(self, result):
        if self.progress.wasCanceled():
            QMessageBox.information(self, '작업 중단', '작업을 중단했습니다.\n\n'
                                                   '성공: {success}\n'
                                                   '실패: {failure}'.format(**result))
            try:
                self.progress.close()
            except Exception:
                pass
        else:
            QMessageBox.information(self, '작업 완료', '작업을 완료했습니다.\n\n'
                                                   '성공: {success}\n'
                                                   '실패: {failure}'.format(**result))

    def reject(self):
        self.ask_and_close()

    def ask_and_close(self):
        answer = QMessageBox.question(self, '종료', '정말로 종료하시겠습니까?')
        if answer == QMessageBox.Yes:
            self.done(0)


class PrototypeWorker(QThread):

    notifyProgress = pyqtSignal(int)
    resultReady = pyqtSignal(dict)

    def __init__(self, word_list, stardict, flashcards_path):
        QThread.__init__(self)
        self.word_list = word_list
        self.stardict = stardict
        self.flashcards_path = flashcards_path
        self.result = {'success': 0, 'failure': 0}

    def run(self):
        with open(self.flashcards_path, 'w', encoding='utf-8', newline='\n') as fo:
            writer = csv.writer(fo, delimiter='\t')
            writer.writerow(['Text 1', 'Text 2'])
            for i, word in enumerate(self.word_list):
                translated = ''
                if self.isInterruptionRequested():
                    break
                try:
                    translated = self.stardict[word]
                    self.result['success'] += 1
                except KeyError:
                    self.result['failure'] += 1
                writer.writerow([word, translated])
                self.notifyProgress.emit(i)
        self.resultReady.emit(self.result)


def main():
    app = QApplication(sys.argv)
    dialog = PrototypeDialog()
    dialog.show()
    sys.exit(app.exec_())

main()
