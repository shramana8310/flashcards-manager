#ifndef FM_OPTIONDIALOG_H
#define FM_OPTIONDIALOG_H

#include "fm_option.h"

#include <QDialog>
#include <QPushButton>
#include <QCheckBox>
#include <QLineEdit>

class FlashcardsManagerOptionDialog : public QDialog {
    Q_OBJECT
public:
    FlashcardsManagerOptionDialog(FlashcardsManagerOption*, QWidget* parent = Q_NULLPTR);
private slots:
    void confirmButtonClicked();
private:
    FlashcardsManagerOption* _option;
    QPushButton* confirmButton;
    QPushButton* cancelButton;
    QCheckBox* replaceLineSeparatorCheckBox;
    QLineEdit* lineSeparatorReplacementLineEdit;
    QLineEdit* multipleArticlesDelimiterLineEdit;
};

#endif // FM_OPTIONDIALOG_H
