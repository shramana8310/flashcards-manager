#include "stardictarticlelink.h"
#include "stardictexception.h"

#include <QString>
#include <QFile>
#include <QByteArray>

#include <zlib.h>

using dict::StarDictArticleLink;
using dict::StarDictInvalidDictFileException;

QString StarDictArticleLink::getArticle() const
{
    QFile dictFile(_dictFileName);
    if (_dictFileCompressed) {
        gzFile dictFileCompressed = gzopen(_dictFileName.toStdString().c_str(), "rb");
        if (dictFileCompressed == NULL) {
            throw StarDictInvalidDictFileException();
        }
        if (gzseek(dictFileCompressed, _offset, SEEK_SET) != (int) _offset) {
            throw StarDictInvalidDictFileException();
        }
        char* buf = new char[_size];
        if (gzread(dictFileCompressed, buf, _size) != (int) _size) {
            delete[] buf;
            throw StarDictInvalidDictFileException();
        }
        gzclose(dictFileCompressed);
        delete[] buf;
        QString article = QString::fromUtf8(buf);
        return article;
    } else {
        if (dictFile.open(QFile::ReadOnly)) {
            dictFile.seek(_offset);
            QByteArray byteArray = dictFile.read(_size);
            if (byteArray.isEmpty()) {
                throw StarDictInvalidDictFileException();
            }
            QString article = QString::fromUtf8(byteArray);
            dictFile.close();
            return article;
        } else {
            throw StarDictInvalidDictFileException();
        }
    }
}

const QString& StarDictArticleLink::dictFileName() const
{
    return _dictFileName;
}

quint32 StarDictArticleLink::offset() const
{
    return _offset;
}

quint32 StarDictArticleLink::size() const
{
    return _size;
}

bool StarDictArticleLink::dictFileCompressed() const
{
    return _dictFileCompressed;
}

void StarDictArticleLink::setDictFileName(const QString& dictFileName)
{
    _dictFileName = dictFileName;
}

void StarDictArticleLink::setOffset(quint32 offset)
{
    _offset = offset;
}

void StarDictArticleLink::setSize(quint32 size)
{
    _size = size;
}

void StarDictArticleLink::setDictFileCompressed(bool dictFileCompressed)
{
    _dictFileCompressed = dictFileCompressed;
}
