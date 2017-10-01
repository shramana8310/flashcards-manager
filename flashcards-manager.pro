TEMPLATE = app
TARGET = flashcards-manager
INCLUDEPATH += .

DEFINES += QT_DEPRECATED_WARNINGS

HEADERS += fm_proto_dialog.h \
    fm_proto_worker.h \
    fm_proto_workerdialog.h
SOURCES += fm_proto_dialog.cpp main.cpp \
    fm_proto_worker.cpp \
    fm_proto_workerdialog.cpp

QT += core gui widgets
