#ifndef FM_WORKER_H
#define FM_WORKER_H

#include "fm_option.h"

#include <QThread>
#include <QList>
#include <QString>

class FlashcardsManagerWorkRequest {
public:
    const QList<QString>& wordList() const
    {
        return _wordList;
    }

    const QList<QString>& dictionaryList() const
    {
        return _dictionaryList;
    }

    const QString& flashcards() const
    {
        return _flashcards;
    }

    const FlashcardsManagerOption& option() const
    {
        return _option;
    }

    void setWordList(const QList<QString>& wordList)
    {
        _wordList = wordList;
    }

    void setDictionaryList(const QList<QString>& dictionaryList)
    {
        _dictionaryList = dictionaryList;
    }

    void setFlashcards(const QString& flashcards)
    {
        _flashcards = flashcards;
    }
    void setOption(const FlashcardsManagerOption& option)
    {
        _option = option;
    }
private:
    QList<QString> _wordList;
    QList<QString> _dictionaryList;
    QString _flashcards;
    FlashcardsManagerOption _option;
};

class FlashcardsManagerWorkResult {
public:
    bool success() const
    {
        return _success;
    }

    int missCount() const
    {
        return _missCount;
    }

    void setSuccess(bool success)
    {
        _success = success;
    }

    void setMissCount(int missCount)
    {
        _missCount = missCount;
    }
private:
    bool _success;
    int _missCount;
};
Q_DECLARE_METATYPE(FlashcardsManagerWorkResult)

class FlashcardsManagerWorker : public QThread {
    Q_OBJECT
public:
    FlashcardsManagerWorker(const FlashcardsManagerWorkRequest&);
    virtual void run() override;
signals:
    void progressed(int);
    void done(const FlashcardsManagerWorkResult&);
private:
    FlashcardsManagerWorkRequest request;
};

#endif // FM_WORKER_H
