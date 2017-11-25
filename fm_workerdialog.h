#ifndef FM_WORKERDIALOG_H
#define FM_WORKERDIALOG_H

#include "fm_worker.h"

#include <QDialog>
#include <QProgressBar>
#include <QPushButton>

class FlashcardsManagerWorkerDialog : public QDialog {
    Q_OBJECT
public:
    FlashcardsManagerWorkerDialog(const FlashcardsManagerWorkRequest&, QWidget* parent = Q_NULLPTR);
private slots:
    void handleWorkResult(const FlashcardsManagerWorkResult&);
private:
    FlashcardsManagerWorker* worker;
    QProgressBar* progressBar;
};

#endif // FM_WORKERDIALOG_H
