#include <QApplication>

#include "fm_proto_dialog.h"

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    FMProtoDialog dialog;
    dialog.show();
    return app.exec();
}
