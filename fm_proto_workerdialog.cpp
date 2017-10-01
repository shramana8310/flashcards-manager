#include <QtGui>
#include <QtWidgets>

#include "fm_proto_workerdialog.h"
#include "fm_proto_worker.h"

FMProtoWorkerDialog::FMProtoWorkerDialog(const FMProtoWorkRequest& request, QWidget *parent) : QDialog(parent)
{
    worker = new FMProtoWorker(request);
    progressBar = new QProgressBar;
    cancelButton = new QPushButton(tr("Cancel"));

    connect(worker, SIGNAL(done(FMProtoWorkResult)), this, SLOT(handleWorkResult(FMProtoWorkResult)));
    connect(worker, SIGNAL(finished()), worker, SLOT(deleteLater()));
    connect(worker, SIGNAL(progressed(int)), progressBar, SLOT(setValue(int)));
    connect(cancelButton, SIGNAL(clicked(bool)), this, SLOT(cancelClicked()));

    QVBoxLayout* layout = new QVBoxLayout;
    layout->addWidget(progressBar);
    layout->addWidget(cancelButton);
    setLayout(layout);

    worker->start();
}

void FMProtoWorkerDialog::cancelClicked()
{
    worker->pause();
    int ret = QMessageBox::question(this, tr("Cancel"), tr("Are you sure?"));
    if (ret == QMessageBox::Yes) {
        worker->cancel();
    } else {
        worker->resume();
    }
}

void FMProtoWorkerDialog::handleWorkResult(const FMProtoWorkResult& result)
{
    this->hide();
    if (result.canceled()) {
        QMessageBox::information(this, tr("Result"), tr("Task canceled"));
    } else {
        if (result.success()) {
            QMessageBox::information(this, tr("Success"), QString("Task done. Miss count: %1").arg(result.missCount()));
        } else {
            QMessageBox::critical(this, tr("Failure"), tr("Task failed."));
        }
    }
}
