#include "fm_workerdialog.h"
#include "fm_worker.h"

#include <QtGui>
#include <QtWidgets>

FlashcardsManagerWorkerDialog::FlashcardsManagerWorkerDialog(const FlashcardsManagerWorkRequest& request, QWidget *parent) : QDialog(parent)
{
    setWindowFlags(Qt::FramelessWindowHint);
    worker = new FlashcardsManagerWorker(request);
    progressBar = new QProgressBar;
    progressBar->setMaximum(request.wordList().size());

    connect(worker, SIGNAL(done(FlashcardsManagerWorkResult)), this, SLOT(handleWorkResult(FlashcardsManagerWorkResult)));
    connect(worker, SIGNAL(finished()), worker, SLOT(deleteLater()));
    connect(worker, SIGNAL(progressed(int)), progressBar, SLOT(setValue(int)));

    QVBoxLayout* layout = new QVBoxLayout;
    layout->addWidget(progressBar);
    setLayout(layout);

    worker->start();
}

void FlashcardsManagerWorkerDialog::handleWorkResult(const FlashcardsManagerWorkResult& result)
{
    this->hide();
    if (result.success()) {
        QMessageBox::information(this, tr("Success"), QString("Task done. Miss count: %1").arg(result.missCount()));
    } else {
        QMessageBox::critical(this, tr("Failure"), tr("Task failed."));
    }
}
