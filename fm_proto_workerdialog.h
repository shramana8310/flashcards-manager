#ifndef FM_PROTO_WORKERDIALOG_H
#define FM_PROTO_WORKERDIALOG_H

#include <QDialog>
#include <QProgressBar>
#include <QPushButton>

#include "fm_proto_worker.h"

class FMProtoWorkerDialog : public QDialog {
    Q_OBJECT
public:
    FMProtoWorkerDialog(const FMProtoWorkRequest&, QWidget* parent = Q_NULLPTR);
private slots:
    void cancelClicked();
    void handleWorkResult(const FMProtoWorkResult&);
private:
    FMProtoWorker* worker;
    QProgressBar* progressBar;
    QPushButton* cancelButton;
};

#endif // FM_PROTO_WORKERDIALOG_H
