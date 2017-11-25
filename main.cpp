#include "fm_dialog.h"

#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    FlashcardsManagerDialog dialog;
    dialog.show();
    return app.exec();
}
