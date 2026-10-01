import math


def paginate_query(
    query,
    page: int,
    limit: int
):

    total = query.count()

    offset = (
        page - 1
    ) * limit

    items = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )

    total_pages = (
        math.ceil(total / limit)
        if total > 0
        else 0
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }