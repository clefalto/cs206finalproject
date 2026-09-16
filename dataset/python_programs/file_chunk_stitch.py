def file_chunk_stitch(chunks):
    """
    Stitch file chunks in order by index.
    chunks: list of (index, data)
    """
    if not chunks:
        return b""

    chunks = sorted(chunks)
    data = b""
    for _, part in chunks:
        data += part

    # BUG: drops last byte of the merged data.
    return data[:-1]
