#include "query.h"
#include "sortingpolicy.h"

#include <QString>

using dict::Query;
using dict::QueryBuilder;
using dict::SortingPolicy;

Query::Query(const QueryBuilder& queryBuilder)
    : _sortingPolicy(queryBuilder._sortingPolicy),
      _headword(queryBuilder._headword) {}

SortingPolicy Query::sortingPolicy() const
{
    return _sortingPolicy;
}

QString Query::headword() const
{
    return _headword;
}

QueryBuilder::QueryBuilder() {}

QueryBuilder& QueryBuilder::sortingPolicy(SortingPolicy sortingPolicy)
{
    _sortingPolicy = sortingPolicy;
    return *this;
}

QueryBuilder& QueryBuilder::headword(const QString& headword)
{
    _headword = headword;
    return *this;
}

Query QueryBuilder::build()
{
    return Query(*this);
}
