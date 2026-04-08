import chromadb

# safer collection creation
client = chromadb.Client()
collection = client.get_or_create_collection(name="codebase")


def store_embeddings(chunks, embeddings):
    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            embeddings=[embeddings[i]],
            ids=[str(i)]
        )


MIN_CHUNK_LENGTH = 30  # Phase 4 threshold


def query_embeddings(query_embedding, k=5):
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )

    docs = results.get("documents", [[]])

    # safety check
    if not docs or not docs[0]:
        print("No documents retrieved")
        return []

    docs = docs[0]

    # 🧹 CLEAN: remove empty / noisy chunks
    cleaned = [
        doc for doc in docs
        if doc and len(doc.strip()) > MIN_CHUNK_LENGTH
    ]

    # 🎯 PRIORITIZE: functions/classes
    filtered = [
        doc for doc in cleaned
        if "def " in doc or "class " in doc
    ]

    # fallback if nothing found
    if not filtered:
        filtered = cleaned

    # 🔁 REMOVE DUPLICATES
    unique_docs = list(dict.fromkeys(filtered))

    # 🧪 DEBUG LOGS
    print(f"Retrieved {len(unique_docs)} relevant chunks")

    for i, doc in enumerate(unique_docs[:2]):
        print(f"Chunk {i+1} preview:", doc[:100])

    return unique_docs[:k]