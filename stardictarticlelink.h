#ifndef STARDICTARTICLELINK_H
#define STARDICTARTICLELINK_H

#include <QString>

namespace dict {
    class StarDictArticleLink;
}

class dict::StarDictArticleLink {
public:
    QString getArticle() const;

    const QString& dictFileName() const;
    quint32 offset() const;
    quint32 size() const;
    bool dictFileCompressed() const;

    void setDictFileName(const QString&);
    void setOffset(quint32);
    void setSize(quint32);
    void setDictFileCompressed(bool);
private:
    QString _dictFileName;
    quint32 _offset;
    quint32 _size;
    bool _dictFileCompressed;
};

#endif // STARDICTARTICLELINK_H
