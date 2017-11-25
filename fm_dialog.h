#ifndef FM_DIALOG_H
#define FM_DIALOG_H

#include "fm_option.h"

#include <QDialog>
#include <QPushButton>
#include <QListWidget>

class FlashcardsManagerDialog : public QDialog {
    Q_OBJECT
public:
    FlashcardsManagerDialog(QWidget* parent = Q_NULLPTR);

protected:
    virtual void closeEvent(QCloseEvent*) override;

private slots:
    void wordLineEditTextChanged(const QString&);
    void checkForExecution();
    void addWord();
    void addWordFromFile();
    void addDictionary();
    void removeSelectedDictionary();
    void upSelectedDictionary();
    void downSelectedDictionary();
    void dictionarySelectionChanged();
    void optionButtonClicked();
    void execute();

private:
    QListWidget* wordList;
    QLineEdit* wordLineEdit;
    QPushButton* addWordButton;
    QPushButton* addWordListFileButton;
    QPushButton* clearWordListButton;

    QListWidget* dictionaryList;
    QPushButton* addDictionaryButton;
    QPushButton* removeDictionaryButton;
    QPushButton* upDictionaryButton;
    QPushButton* downDictionaryButton;

    QPushButton* executeButton;
    QPushButton* closeButton;
    QPushButton* optionButton;

    FlashcardsManagerOption* option;
};

#endif // FM_DIALOG_H
