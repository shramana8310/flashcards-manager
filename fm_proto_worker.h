#ifndef FM_PROTO_WORKER_H
#define FM_PROTO_WORKER_H

#include <QThread>
#include <QList>
#include <QString>

class FMProtoWorkRequest {
public:
    FMProtoWorkRequest(const QList<QString>& __wordList = QList<QString>{},
                       const QList<QString>& __dictionaryList = QList<QString>{},
                       const QString& __flashcards = QString{})
        : _wordList(__wordList), _dictionaryList(__dictionaryList), _flashcards(__flashcards) {}
    QList<QString> wordList() const { return _wordList; }
    QList<QString> dictionaryList() const { return _dictionaryList; }
    QString flashcards() const { return _flashcards; }
private:
    QList<QString> _wordList;
    QList<QString> _dictionaryList;
    QString _flashcards;
};

class FMProtoWorkResult {
public:
    explicit FMProtoWorkResult(bool __canceled = false,
                               bool __success = false,
                               int __missCount = 0)
        : _canceled(__canceled), _success(__success), _missCount(__missCount) {}

    bool canceled() const { return _canceled; }
    bool success() const { return _success; }
    int missCount() const { return _missCount; }
    void setSuccess(bool __success) { _success = __success; }
    void setMissCount(int __missCount) { _missCount = __missCount; }
private:
    bool _canceled;
    bool _success;
    int _missCount;
};
Q_DECLARE_METATYPE(FMProtoWorkResult)

class FMProtoWorker : public QThread {
    Q_OBJECT
public:
    FMProtoWorker(const FMProtoWorkRequest&);
    virtual void run() override;
signals:
    void progressed(int);
    void done(const FMProtoWorkResult&);
public slots:
    void pause();
    void resume();
    void cancel();
private:
    const FMProtoWorkRequest& request;
    bool paused;
    bool canceled;
    int calcPercentage(int currentWordIndex, int currentDictionaryIndex);
};

#endif // FM_PROTO_WORKER_H
