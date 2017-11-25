#ifndef STARDICTEXCEPTION_H
#define STARDICTEXCEPTION_H

#include <QException>

namespace dict {
    class StarDictException;
    class StarDictInitializationFailedException;
    class StarDictInvalidDictFileException;
}

class dict::StarDictException : public QException {
public:
    void raise() const { throw *this; }
    StarDictException* clone() const
    {
        return new StarDictException(*this);
    }
};

class dict::StarDictInitializationFailedException : public QException {
public:
    void raise() const { throw *this; }
    StarDictInitializationFailedException* clone() const
    {
        return new StarDictInitializationFailedException(*this);
    }
};

class dict::StarDictInvalidDictFileException : public QException {
public:
    void raise() const { throw *this; }
    StarDictInvalidDictFileException* clone() const
    {
        return new StarDictInvalidDictFileException(*this);
    }
};

#endif // STARDICTEXCEPTION_H
