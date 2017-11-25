#include "stardict.h"
#include "query.h"
#include "stardictarticlelink.h"
#include "stardictexception.h"
#include "sortingpolicy.h"

#include <QDir>
#include <QFile>
#include <QString>
#include <QVector>
#include <QFileInfo>
#include <QIODevice>
#include <QTextStream>
#include <QStringList>
#include <QDataStream>
#include <QByteArray>
#include <QtEndian>

#include <zlib.h>

using dict::StarDict;
using dict::Query;
using dict::StarDictArticleLink;
using dict::StarDictInitializationFailedException;
using dict::SortingPolicy;

StarDict::StarDict(const QFile &ifoFile)
{
    QFileInfo ifoFileInfo(ifoFile);
    init(ifoFileInfo.dir(), ifoFileInfo.baseName());
}

StarDict::StarDict(const QDir &directory, const QString& baseName)
{
    init(directory, baseName);
}

void StarDict::init(const QDir &directory, const QString& baseName)
{
    _ifoFile.setFileName(directory.path() + "/" + baseName + ".ifo");
    if (!_ifoFile.exists()) {
        throw StarDictInitializationFailedException();
    }

    QFile idxFileCandidate(directory.path() + "/" + baseName + ".idx");
    if (idxFileCandidate.exists()) {
        _idxFile.setFileName(idxFileCandidate.fileName());
        _idxFileCompressed = false;
    } else {
        QFile compressedIdxFileCandidate(directory.path() + "/" + baseName + ".idx.gz");
        if (compressedIdxFileCandidate.exists()) {
            _idxFile.setFileName(compressedIdxFileCandidate.fileName());
            _idxFileCompressed = true;
        } else {
            throw StarDictInitializationFailedException();
        }
    }

    QFile dictFileCandidate(directory.path() + "/" + baseName + ".dict");
    if (dictFileCandidate.exists()) {
        _dictFile.setFileName(dictFileCandidate.fileName());
        _dictFileCompressed = false;
    } else {
        QFile compressedDictFileCandidate(directory.path() + "/" + baseName + ".dict.dz");
        if (compressedDictFileCandidate.exists()) {
            _dictFile.setFileName(compressedDictFileCandidate.fileName());
            _dictFileCompressed = true;
        } else {
            throw StarDictInitializationFailedException();
        }
    }

    if (_ifoFile.open(QIODevice::ReadOnly)) {
        QTextStream ifoFileTextStream(&_ifoFile);
        while (!ifoFileTextStream.atEnd()) {
            QString line = ifoFileTextStream.readLine();

            // TODO extremely tedious. needs refactoring.
            if (line.startsWith("version")) {
                QStringList list = line.split('=');
                if (list.size() == 2) {
                    _version = list.at(1);
                }
            } else if (line.startsWith("idxoffsetbits")) {
                QStringList list = line.split('=');
                if (list.size() == 2) {
                    bool tmp;
                    int idxoffsetbits = list.at(1).toInt(&tmp);
                    if (!tmp || idxoffsetbits != 32) {
                        throw StarDictInitializationFailedException();
                    }
                } else {
                    throw StarDictInitializationFailedException();
                }
            } else if (line.startsWith("wordcount")) {
                QStringList list = line.split('=');
                if (list.size() == 2) {
                    bool tmp;
                    _wordcount = list.at(1).toLong(&tmp);
                    if (!tmp) {
                        throw StarDictInitializationFailedException();
                    }
                } else {
                    throw StarDictInitializationFailedException();
                }
            } else if (line.startsWith("idxfilesize")) {
                QStringList list = line.split('=');
                if (list.size() == 2) {
                    bool tmp;
                    _idxfilesize = list.at(1).toLong(&tmp);
                    if (!tmp) {
                        throw StarDictInitializationFailedException();
                    }
                } else {
                    throw StarDictInitializationFailedException();
                }
            } else if (line.startsWith("bookname")) {
                QStringList list = line.split('=');
                if (list.size() == 2) {
                    _bookname = list.at(1);
                } else {
                    throw StarDictInitializationFailedException();
                }
            } else if (line.startsWith("description")) {
                QStringList list = line.split('=');
                if (list.size() == 2) {
                    _description = list.at(1);
                } else {
                    throw StarDictInitializationFailedException();
                }
            }
        }
        _ifoFile.close();
    }

    if (_idxFileCompressed) {
        gzFile idxFileCompressed = gzopen(_idxFile.fileName().toStdString().c_str(), "rb");
        if (idxFileCompressed == NULL) {
            throw StarDictInitializationFailedException();
        }

        // I hate this, but it kinda works.
        quint64 mapWordcount = 0;
        do {
            char c = gzgetc(idxFileCompressed);
            if (gzeof(idxFileCompressed)) {
                break;
            }
            QByteArray headwordBuffer;
            while (c != '\0') {
                headwordBuffer.append(c);
                c = gzgetc(idxFileCompressed);
                if (c == -1) {
                    throw StarDictInitializationFailedException();
                }
            }
            QString headword = QString::fromUtf8(headwordBuffer);

            int offset_size = sizeof(quint32);
            char* offset_buf = new char[offset_size];
            if (gzread(idxFileCompressed, offset_buf, offset_size) != offset_size) {
                delete[] offset_buf;
                throw StarDictInitializationFailedException();
            }
            quint32 offset = qFromBigEndian<quint32>(offset_buf);
            delete[] offset_buf;

            int size_size = sizeof(quint32);
            char* size_buf = new char[size_size];
            if (gzread(idxFileCompressed, size_buf, size_size) != size_size) {
                delete[] size_buf;
                throw StarDictInitializationFailedException();
            }
            quint32 size = qFromBigEndian<quint32>(size_buf);
            delete[] size_buf;

            StarDictArticleLink articleLink;
            articleLink.setDictFileName(_dictFile.fileName());
            articleLink.setOffset(offset);
            articleLink.setSize(size);
            articleLink.setDictFileCompressed(_dictFileCompressed);

            if (!_dictionary.contains(headword)) {
                _dictionary[headword] = QVector<StarDictArticleLink>();
            }
            _dictionary[headword].append(articleLink);

            mapWordcount++;
        } while (true);
        gzclose(idxFileCompressed);
        if (mapWordcount != _wordcount) {
            throw StarDictInitializationFailedException();
        }

    } else {
        if (_idxFile.open(QIODevice::ReadOnly)) {
            if ((quint64) _idxFile.size() != _idxfilesize) {
                throw StarDictInitializationFailedException();
            }
            QDataStream idxFileDataStream(&_idxFile);
            idxFileDataStream.setByteOrder(QDataStream::BigEndian);
            quint64 mapWordcount = 0;
            while (!_idxFile.atEnd()) {
                QByteArray headwordBuffer;
                for (char c; _idxFile.getChar(&c) && c != '\0'; ) {
                    headwordBuffer.append(c);
                }
                QString headword = QString::fromUtf8(headwordBuffer);
                quint32 offset;
                quint32 size;
                idxFileDataStream >> offset >> size;

                StarDictArticleLink articleLink;
                articleLink.setDictFileName(_dictFile.fileName());
                articleLink.setOffset(offset);
                articleLink.setSize(size);
                articleLink.setDictFileCompressed(_dictFileCompressed);

                if (!_dictionary.contains(headword)) {
                    _dictionary[headword] = QVector<StarDictArticleLink>();
                }
                _dictionary[headword].append(articleLink);

                mapWordcount++;
            }
            if (mapWordcount != _wordcount) {
                throw StarDictInitializationFailedException();
            }
        }
    }
}

QVector<StarDictArticleLink> StarDict::executeQuery(const Query& query)
{
    if (_dictionary.contains(query.headword())) {
        QVector<StarDictArticleLink> articleLinks = _dictionary[query.headword()];
        if (query.sortingPolicy() == SortingPolicy::Descending) {
            QVector<StarDictArticleLink> reversedArticleLinks;
            for (QVector<StarDictArticleLink>::reverse_iterator i = articleLinks.rbegin(); i != articleLinks.rend(); ++i) {
                reversedArticleLinks.append(*i);
            }
            return reversedArticleLinks;
        } else  {
            return articleLinks;
        }
    } else {
        return QVector<StarDictArticleLink>();
    }
}
