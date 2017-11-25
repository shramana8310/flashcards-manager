#include "fm_optiondialog.h"
#include "fm_option.h"

#include <QtCore>
#include <QtWidgets>

FlashcardsManagerOptionDialog::FlashcardsManagerOptionDialog(FlashcardsManagerOption* option, QWidget *parent)
    : QDialog(parent), _option(option)
{
    confirmButton = new QPushButton(tr("Confirm"));
    cancelButton = new QPushButton(tr("Cancel"));
    replaceLineSeparatorCheckBox = new QCheckBox(tr("Replace line separator"));
    lineSeparatorReplacementLineEdit = new QLineEdit();
    multipleArticlesDelimiterLineEdit = new QLineEdit();

    replaceLineSeparatorCheckBox->setChecked(_option->replaceLineSeparator());
    lineSeparatorReplacementLineEdit->setEnabled(_option->replaceLineSeparator());
    lineSeparatorReplacementLineEdit->setText(_option->lineSeparatorReplacement());
    multipleArticlesDelimiterLineEdit->setText(_option->multipleArticlesDelimiter());

    connect(confirmButton, SIGNAL(clicked()),
            this, SLOT(confirmButtonClicked()));
    connect(cancelButton, SIGNAL(clicked()),
            this, SLOT(close()));
    connect(replaceLineSeparatorCheckBox, SIGNAL(toggled(bool)),
            lineSeparatorReplacementLineEdit, SLOT(setEnabled(bool)));

    QVBoxLayout* vBoxLayout1 = new QVBoxLayout();
    vBoxLayout1->addWidget(replaceLineSeparatorCheckBox);
    QHBoxLayout* hBoxLayout1 = new QHBoxLayout();
    hBoxLayout1->addWidget(new QLabel(tr("Line separator replacement")));
    hBoxLayout1->addWidget(lineSeparatorReplacementLineEdit);
    QHBoxLayout* hBoxLayout2 = new QHBoxLayout();
    hBoxLayout2->addWidget(new QLabel(tr("Multiple articles delimiter")));
    hBoxLayout2->addWidget(multipleArticlesDelimiterLineEdit);
    vBoxLayout1->addLayout(hBoxLayout1);
    vBoxLayout1->addLayout(hBoxLayout2);

    QVBoxLayout* vBoxLayout2 = new QVBoxLayout();
    vBoxLayout2->addWidget(confirmButton);
    vBoxLayout2->addWidget(cancelButton);

    QHBoxLayout* layout = new QHBoxLayout();
    layout->addLayout(vBoxLayout1);
    layout->addLayout(vBoxLayout2);

    setLayout(layout);
    setWindowTitle(tr("Options"));
}

void FlashcardsManagerOptionDialog::confirmButtonClicked()
{
    _option->setReplaceLineSeparator(replaceLineSeparatorCheckBox->isChecked());
    _option->setLineSeparatorReplacement(lineSeparatorReplacementLineEdit->text());
    _option->setMultipleArticlesDelimiter(multipleArticlesDelimiterLineEdit->text());
    close();
}
