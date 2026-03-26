def chunk_code(code: str, chunk_size=300):
    chunks = []
    for i in range(0, len(code), chunk_size):
        chunks.append(code[i:i+chunk_size])
    return chunks