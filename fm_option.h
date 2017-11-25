#ifndef FM_OPTION_H
#define FM_OPTION_H

#include <QString>

class FlashcardsManagerOption {
public:
    FlashcardsManagerOption()
        : _replaceLineSeparator(true),
          _lineSeparatorReplacement("<br />"),
          _multipleArticlesDelimiter("<br /><br />") {}

    bool replaceLineSeparator() const
    {
        return _replaceLineSeparator;
    }

    const QString& lineSeparatorReplacement() const
    {
        return _lineSeparatorReplacement;
    }

    const QString& multipleArticlesDelimiter() const
    {
        return _multipleArticlesDelimiter;
    }

    void setReplaceLineSeparator(bool replaceLineSeparator)
    {
        _replaceLineSeparator = replaceLineSeparator;
    }

    void setLineSeparatorReplacement(const QString& lineSeparatorReplacement)
    {
        _lineSeparatorReplacement = lineSeparatorReplacement;
    }

    void setMultipleArticlesDelimiter(const QString& multipleArticlesDelimiter)
    {
        _multipleArticlesDelimiter = multipleArticlesDelimiter;
    }
private:
    bool _replaceLineSeparator;
    QString _lineSeparatorReplacement;
    QString _multipleArticlesDelimiter;
};

#endif // FM_OPTION_H
