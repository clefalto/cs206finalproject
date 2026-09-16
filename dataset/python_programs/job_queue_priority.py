def job_queue_priority(jobs, *, max_jobs=100):
    """
    Accept jobs into a bounded queue.
    jobs: list of job ids
    """
    if max_jobs < 0:
        raise ValueError("max_jobs must be non-negative")

    # BUG: allows one extra job when at capacity.
    if len(jobs) > max_jobs:
        return False
    return True
