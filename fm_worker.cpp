#include "fm_worker.h"
#include "stardict.h"
#include "query.h"
#include "sortingpolicy.h"
#include "stardictarticlelink.h"
#include "stardictexception.h"

#include <QtCore>

using namespace dict;

FlashcardsManagerWorker::FlashcardsManagerWorker(const FlashcardsManagerWorkRequest& req)
    : request(req)
{
    // probably not a good idea
    qRegisterMetaType<FlashcardsManagerWorkResult>("FlashcardsManagerWorkResult");
}

void FlashcardsManagerWorker::run()
{
    try {
        QList<QString> wordList = request.wordList();

        int missCount = 0;

        QVector<StarDict*> starDicts;

        QList<QString> dictionaryList = request.dictionaryList();
        for (QList<QString>::iterator i = dictionaryList.begin(); i != dictionaryList.end(); ++i) {
            try {
                starDicts.append(new StarDict(QFile(*i)));
            } catch (StarDictInitializationFailedException) {
                for (QVector<StarDict*>::iterator j = starDicts.begin(); j != starDicts.end(); ++j)
                    delete *j;
                throw StarDictException();
            }
        }

        QFile tsvFile(request.flashcards());
        if (tsvFile.open(QIODevice::WriteOnly)) {
            QTextStream tsvStream(&tsvFile);
            tsvStream.setCodec("UTF-8");
            for (int i = 0; i < wordList.size(); ++i) {
                QString word = wordList[i];
                tsvStream << word << '\t';
                Query query = QueryBuilder()
                        .sortingPolicy(SortingPolicy::Ascending)
                        .headword(word)
                        .build();
                for (int j = 0; j < starDicts.size(); ++j) {
                    StarDict* starDictPtr = starDicts[j];
                    QVector<StarDictArticleLink> articleLinks = starDictPtr->executeQuery(query);
                    if (articleLinks.isEmpty()) {
                        ++missCount;
                    }
                    for (int k = 0; k < articleLinks.size(); ++k) {
                        StarDictArticleLink articleLink = articleLinks[k];
                        QString article = articleLink.getArticle();
                        if (request.option().replaceLineSeparator()) {
                            article = article.replace(QRegExp("[\\r\\n]"), request.option().lineSeparatorReplacement());
                        }
                        tsvStream << article;
                        if (k < articleLinks.size() - 1) {
                            tsvStream << request.option().multipleArticlesDelimiter();
                        }
                    }
                    if (j < starDicts.size() - 1) {
                        tsvStream << '\t';
                    }
                }
                tsvStream << '\n';
                emit progressed(i);
            }
            tsvFile.close();
        }

        // cleanup
        for (QVector<StarDict*>::iterator i = starDicts.begin(); i != starDicts.end(); ++i)
            delete *i;

        FlashcardsManagerWorkResult result;
        result.setMissCount(missCount);
        result.setSuccess(true);
        emit done(result);
    } catch (StarDictException) {
        FlashcardsManagerWorkResult result;
        result.setMissCount(0);
        result.setSuccess(false);
        emit done(result);
    }
}
