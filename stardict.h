#ifndef STARDICT_H
#define STARDICT_H

#include "stardictarticlelink.h"

#include <QDir>
#include <QFile>
#include <QString>
#include <QVector>
#include <QMap>

namespace dict {
    class StarDict;
    class Query;
    class StarDictArticleLink;
}

class dict::StarDict {
public:
    StarDict(const QFile& ifoFile);
    StarDict(const QDir& directory, const QString& baseName);
    QVector<StarDictArticleLink> executeQuery(const Query& query);
private:
    void init(const QDir& directory, const QString& baseName);

    QFile _ifoFile;
    QFile _idxFile;
    QFile _dictFile;

    bool _idxFileCompressed;
    bool _dictFileCompressed;

    // StarDict ifo
    QString _version;
    quint64 _wordcount;
    quint64 _idxfilesize;
    QString _bookname;
    QString _description;

    // temporary implementation (seems pretty expensive)
    QMap<QString, QVector<StarDictArticleLink>> _dictionary;
};

#endif // STARDICT_H
