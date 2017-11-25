#ifndef QUERY_H
#define QUERY_H

#include "sortingpolicy.h"

#include <QString>

namespace dict {
    class Query;
    class QueryBuilder;
}

class dict::Query {
public:
    Query(const QueryBuilder&);
    SortingPolicy sortingPolicy() const;
    QString headword() const;
private:
    SortingPolicy _sortingPolicy;
    QString _headword;
};

class dict::QueryBuilder {
public:
    friend class Query;
    QueryBuilder();
    QueryBuilder& sortingPolicy(SortingPolicy);
    QueryBuilder& headword(const QString&);
    Query build();
private:
    SortingPolicy _sortingPolicy;
    QString _headword;
};

#endif // QUERY_H
