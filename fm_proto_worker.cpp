#include <QtCore>

#include "fm_proto_worker.h"

FMProtoWorker::FMProtoWorker(const FMProtoWorkRequest &req)
    : request(req), paused(false), canceled(false)
{
    qRegisterMetaType<FMProtoWorkResult>("FMProtoWorkResult");
}

void FMProtoWorker::run()
{
    QList<QString> wordList = request.wordList();

    bool successful = true;
    int missCount = 0;

    // this is really really terrible
    QFile file (request.flashcards());
    if (file.open(QFile::WriteOnly)) {
        QTextStream out(&file);
        for (int i = 0; i < wordList.size(); ++i) {
            QString word = wordList[i];
            QList<QString> dictionaryList = request.dictionaryList();
            out << word << '\t';
            for (int j = 0; j < dictionaryList.size(); ++j) {
                QFile dictFile (dictionaryList[j]);
                if (dictFile.open(QFile::ReadOnly)) {
                    QTextStream in(&dictFile);
                    QString line;
                    bool found = false;
                    while (in.readLineInto(&line)) {
                        QStringList sList = line.split('\t');
                        if (sList.size() > 1 && sList[0] == word) {
                            out << sList[1];
                            found = true;
                            break;
                        }

                        while (paused) msleep(100);
                        if (canceled) {
                            FMProtoWorkResult canceledResult(true);
                            emit done(canceledResult);
                            return;
                        } else {
                            emit progressed(calcPercentage(i, j));
                        }
                    }
                    if (!found) ++missCount;
                } else {
                    successful = false;
                    FMProtoWorkResult unsuccessfulResult(false, true);
                    emit done(unsuccessfulResult);
                    return;
                }
                if (j != dictionaryList.size() -1)
                    out << '\t';
            }
            out << '\n';
        }
    } else {
        successful = false;
        FMProtoWorkResult unsuccessfulResult(false, true);
        emit done(unsuccessfulResult);
        return;
    }

    FMProtoWorkResult result (false, successful, missCount);
    emit done(result);
}

void FMProtoWorker::pause()
{
    paused = true;
}

void FMProtoWorker::resume()
{
    paused = false;
}

void FMProtoWorker::cancel()
{
    canceled = true;
    paused = false;
}

int FMProtoWorker::calcPercentage(int currentWordIndex, int currentDictionaryIndex)
{
    int total = request.dictionaryList().size() * request.wordList().size();
    int passed = request.dictionaryList().size() * currentWordIndex;
    int offset = currentDictionaryIndex;
    return (passed + offset) / total;
}
