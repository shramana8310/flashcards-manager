TEMPLATE = app
TARGET = flashcards-manager
VERSION = 1.0.0

QT += core widgets

INCLUDEPATH += $$PWD/include
LIBS += -L$${PWD}/libs -lz

DEFINES += QT_DEPRECATED_WARNINGS

HEADERS += query.h \
    sortingpolicy.h \
    stardict.h \
    stardictarticlelink.h \
    stardictexception.h \
    fm_dialog.h \
    fm_workerdialog.h \
    fm_worker.h \
    fm_optiondialog.h \
    fm_option.h
SOURCES += main.cpp \
    query.cpp \
    stardict.cpp \
    stardictarticlelink.cpp \
    fm_dialog.cpp \
    fm_workerdialog.cpp \
    fm_worker.cpp \
    fm_optiondialog.cpp
