import pytest
from your_module import store_embeddings, query_embeddings

def test_store_embeddings():
    chunks = ["chunk1", "chunk2"]
    embeddings = [[1, 2], [3, 4]]
    store_embeddings(chunks, embeddings)

def test_query_embeddings():
    query_embedding = [1, 2]
    results = query_embeddings(query_embedding)
    assert isinstance(results, list)

def test_query_embeddings_empty():
    collection = client.get_or_create_collection(name="empty")
    query_embedding = [1, 2]
    results = collection.query(query_embeddings=[query_embedding], n_results=5)
    assert results.get("documents", []) == [[]]

def test_query_embeddings_min_length():
    query_embedding = [1, 2]
    chunks = ["a" * 29, "b" * 31]
    embeddings = [[1, 2], [3, 4]]
    store_embeddings(chunks, embeddings)
    results = query_embeddings(query_embedding)
    assert len(results) == 1

def test_query_embeddings_k():
    query_embedding = [1, 2]
    chunks = ["a" * 31, "b" * 31, "c" * 31]
    embeddings = [[1, 2], [3, 4], [5, 6]]
    store_embeddings(chunks, embeddings)
    results = query_embeddings(query_embedding, k=2)
    assert len(results) == 2
