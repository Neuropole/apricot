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
    return results["documents"][0]