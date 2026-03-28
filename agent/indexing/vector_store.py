import chromadb

client = chromadb.Client()
collection = client.create_collection(name="codebase")

def store_embeddings(chunks, embeddings):
    for i, chunk in enumerate(chunks):
        collection.add(
            documents=[chunk],
            embeddings=[embeddings[i]],
            ids=[str(i)]
        )

def query_embeddings(query_embedding, k=5):
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )

    docs = results.get("documents", [[]])[0]

    # remove empty / tiny chunks
    cleaned = [doc for doc in docs if doc and len(doc.strip()) > 20]

    # 🔥 prioritize useful code (functions/classes)
    filtered = []
    for doc in cleaned:
        if "def " in doc or "class " in doc:
            filtered.append(doc)

    print(f"Retrieved {len(filtered)} relevant chunks")

    return filtered[:k]