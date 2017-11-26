#include "fm_dialog.h"
#include "fm_workerdialog.h"
#include "fm_option.h"
#include "fm_optiondialog.h"

#include <QtCore>
#include <QtWidgets>

FlashcardsManagerDialog::FlashcardsManagerDialog(QWidget* parent) : QDialog(parent)
{
    // initialize
    wordList = new QListWidget;
    wordLineEdit = new QLineEdit;
    addWordButton = new QPushButton(tr("Add"));
    addWordListFileButton = new QPushButton(tr("Add From File"));
    clearWordListButton = new QPushButton("Clear");

    dictionaryList = new QListWidget;
    addDictionaryButton = new QPushButton(tr("Add"));
    removeDictionaryButton = new QPushButton(tr("Remove"));
    upDictionaryButton = new QPushButton(tr("Up"));
    downDictionaryButton = new QPushButton(tr("Down"));

    executeButton = new QPushButton(tr("Execute"));
    closeButton = new QPushButton(tr("Close"));
    optionButton = new QPushButton(tr("Option"));

    option = new FlashcardsManagerOption();

    // wire up
    connect(wordLineEdit, SIGNAL(textChanged(const QString&)),
            this, SLOT(wordLineEditTextChanged(const QString&)));
    connect(closeButton, SIGNAL(clicked()),
            this, SLOT(close()));
    connect(addWordButton, SIGNAL(clicked()),
            this, SLOT(addWord()));
    connect(wordLineEdit, SIGNAL(returnPressed()),
            this, SLOT(addWord()));
    connect(clearWordListButton, SIGNAL(clicked()),
            wordList, SLOT(clear()));
    connect(clearWordListButton, SIGNAL(clicked()),
            this, SLOT(checkForExecution()));
    connect(addWordListFileButton, SIGNAL(clicked()),
            this, SLOT(addWordFromFile()));
    connect(addDictionaryButton, SIGNAL(clicked()),
            this, SLOT(addDictionary()));
    connect(removeDictionaryButton, SIGNAL(clicked()),
            this, SLOT(removeSelectedDictionary()));
    connect(upDictionaryButton, SIGNAL(clicked()),
            this, SLOT(upSelectedDictionary()));
    connect(downDictionaryButton, SIGNAL(clicked()),
            this, SLOT(downSelectedDictionary()));
    connect(dictionaryList, SIGNAL(itemSelectionChanged()),
            this, SLOT(dictionarySelectionChanged()));
    connect(wordList->model(), SIGNAL(rowsInserted(QModelIndex,int,int)),
            this, SLOT(checkForExecution()));
    connect(wordList->model(), SIGNAL(rowsRemoved(QModelIndex,int,int)),
            this, SLOT(checkForExecution()));
    connect(dictionaryList->model(), SIGNAL(rowsInserted(QModelIndex,int,int)),
            this, SLOT(checkForExecution()));
    connect(dictionaryList->model(), SIGNAL(rowsRemoved(QModelIndex,int,int)),
            this, SLOT(checkForExecution()));
    connect(executeButton, SIGNAL(clicked()),
            this, SLOT(execute()));
    connect(optionButton, SIGNAL(clicked()),
            this, SLOT(optionButtonClicked()));

    // layout
    QVBoxLayout* buttonLayout = new QVBoxLayout;
    QGroupBox* wordListGroup = new QGroupBox(tr("Word List"));

    QHBoxLayout* hBoxLayout1 = new QHBoxLayout;
    hBoxLayout1->addWidget(wordLineEdit);
    hBoxLayout1->addWidget(addWordButton);

    QHBoxLayout* hBoxLayout2 = new QHBoxLayout;
    hBoxLayout2->addWidget(addWordListFileButton);
    hBoxLayout2->addWidget(clearWordListButton);

    QVBoxLayout* vBoxLayout1 = new QVBoxLayout;
    vBoxLayout1->addWidget(wordList);
    vBoxLayout1->addLayout(hBoxLayout1);
    vBoxLayout1->addLayout(hBoxLayout2);

    wordListGroup->setLayout(vBoxLayout1);

    QGroupBox* dictionaryListGroup = new QGroupBox(tr("Dictionary List"));

    QHBoxLayout* hBoxLayout3 = new QHBoxLayout;
    hBoxLayout3->addWidget(addDictionaryButton);
    hBoxLayout3->addWidget(removeDictionaryButton);
    hBoxLayout3->addWidget(upDictionaryButton);
    hBoxLayout3->addWidget(downDictionaryButton);

    QVBoxLayout* vBoxLayout2 = new QVBoxLayout;
    vBoxLayout2->addWidget(dictionaryList);
    vBoxLayout2->addLayout(hBoxLayout3);

    dictionaryListGroup->setLayout(vBoxLayout2);

    buttonLayout->addWidget(executeButton);
    buttonLayout->addWidget(closeButton);
    buttonLayout->addStretch();
    buttonLayout->addWidget(optionButton);

    QHBoxLayout* layout = new QHBoxLayout;
    layout->addWidget(wordListGroup);
    layout->addWidget(dictionaryListGroup);
    layout->addLayout(buttonLayout);

    setLayout(layout);
    setWindowTitle(tr("Flashcards Generator"));

    // manual check
    removeDictionaryButton->setEnabled(false);
    upDictionaryButton->setEnabled(false);
    downDictionaryButton->setEnabled(false);
    executeButton->setEnabled(false);
}

void FlashcardsManagerDialog::wordLineEditTextChanged(const QString& text)
{
    addWordButton->setEnabled(!text.isEmpty());
}

void FlashcardsManagerDialog::checkForExecution()
{
    executeButton->setEnabled(wordList->count() > 0 && dictionaryList->count() > 0);
}

void FlashcardsManagerDialog::addWord()
{
    const QString& text = wordLineEdit->text();
    if (!text.isEmpty()) {
        wordList->addItem(text);
        wordList->scrollToBottom();
        wordLineEdit->clear();
        wordLineEdit->setFocus();
    }
}

void FlashcardsManagerDialog::addWordFromFile()
{
    const QString& fileName = QFileDialog::getOpenFileName(this, tr("Open File"), 
        ".", tr("Text files (*.txt)"));
    if (!fileName.isNull()) {
        QFile file(fileName);
        if (file.open(QFile::ReadOnly)) {
            QTextStream stream(&file);
            stream.setCodec("UTF-8");
            QString line;
            while (stream.readLineInto(&line)) {
                wordList->addItem(line);
            }
            wordList->scrollToBottom();
        }
    }
}

void FlashcardsManagerDialog::closeEvent(QCloseEvent* event)
{
    int ret = QMessageBox::question(this, tr("Close"), tr("Are you sure?"));
    if (ret == QMessageBox::Yes) {
        event->accept();
    } else {
        event->ignore();
    }
}

void FlashcardsManagerDialog::addDictionary()
{
    const QString& fileName =
            QFileDialog::getOpenFileName(this, tr("Open File"), ".", tr("StarDict dictionary file (*.ifo)"));
    if (!fileName.isNull()) {
        QFile file(fileName);
        if (file.exists()) {
            dictionaryList->addItem(fileName);
        }
        dictionaryList->scrollToBottom();
    }
}

void FlashcardsManagerDialog::removeSelectedDictionary()
{
    dictionaryList->takeItem(dictionaryList->currentRow());
}

void FlashcardsManagerDialog::upSelectedDictionary()
{
    int currentIndex = dictionaryList->currentRow();
    QListWidgetItem* currentItem = dictionaryList->takeItem(currentIndex);
    dictionaryList->insertItem(currentIndex - 1, currentItem);
    dictionaryList->setCurrentRow(currentIndex - 1);
}

void FlashcardsManagerDialog::downSelectedDictionary()
{
    int currentIndex = dictionaryList->currentRow();
    QListWidgetItem* currentItem = dictionaryList->takeItem(currentIndex);
    dictionaryList->insertItem(currentIndex + 1, currentItem);
    dictionaryList->setCurrentRow(currentIndex + 1);
}

void FlashcardsManagerDialog::dictionarySelectionChanged()
{
    bool empty = dictionaryList->selectedItems().isEmpty();
    int currentRow = dictionaryList->currentRow();
    removeDictionaryButton->setEnabled(!empty);
    upDictionaryButton->setEnabled(!empty && currentRow != 0);
    downDictionaryButton->setEnabled(!empty && currentRow < dictionaryList->count() - 1);
}

void FlashcardsManagerDialog::optionButtonClicked()
{
    FlashcardsManagerOptionDialog* dialog = new FlashcardsManagerOptionDialog(option);
    dialog->setModal(true);
    dialog->show();
}

void FlashcardsManagerDialog::execute()
{
    QString fileName = QFileDialog::getSaveFileName(this, tr("Save File"),
          "./untitled.txt", tr("Text Files (*.txt)"));
    if (!fileName.isNull()) {
        QList<QString> wordListReq;
        for (int i = 0; i < wordList->count(); ++i)
            wordListReq.append(wordList->item(i)->text());
        QList<QString> dictionaryListReq;
        for (int i = 0; i < dictionaryList->count(); ++i)
            dictionaryListReq.append(dictionaryList->item(i)->text());

        FlashcardsManagerWorkRequest req;
        req.setFlashcards(fileName);
        req.setDictionaryList(dictionaryListReq);
        req.setWordList(wordListReq);
        req.setOption(*option);

        FlashcardsManagerWorkerDialog* dialog = new FlashcardsManagerWorkerDialog(req);
        dialog->show();
    }
}
