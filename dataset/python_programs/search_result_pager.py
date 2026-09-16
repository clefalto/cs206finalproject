def search_result_pager(results, page, *, page_size=10):
    """
    Return page of results.
    """
    if page < 1:
        raise ValueError("page must be >= 1")
    if page_size <= 0:
        raise ValueError("page_size must be positive")

    start = (page - 1) * page_size
    end = start + page_size

    # BUG: end is inclusive; should be exclusive.
    return results[start:end + 1]
