from agent.indexing.parser import get_code_files
from agent.indexing.chunker import chunk_code
from agent.indexing.embedder import get_embeddings
from agent.indexing.vector_store import store_embeddings, query_embeddings

import subprocess
from agent.llm.groq_client import generate_review
from agent.github.commenter import post_comment
def get_pr_diff():
    try:
        diff = subprocess.check_output(
            ["git", "diff", "HEAD~1", "HEAD"],
            text=True
        )
        return diff
    except Exception as e:
        print("Error getting diff:", e)
        return ""


def build_context():
    files = get_code_files()
    all_chunks = []

    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                code = f.read()
                chunks = chunk_code(code)
                all_chunks.extend(chunks)
        except:
            continue

    return all_chunks


def main():
    print("Agent started")

    # 1. Get diff
    diff = get_pr_diff()

    if not diff.strip():
        print("No changes found")
        return

    # 2. Build full codebase context
    print("Building context...")
    chunks = build_context()

    # 3. Convert to embeddings
    print("Generating embeddings...")
    embeddings = get_embeddings(chunks)

    # 4. Store embeddings
    print("Storing embeddings...")
    store_embeddings(chunks, embeddings)

    # 5. Convert diff → embedding
    print("Embedding diff...")
    query_embedding = get_embeddings([diff])[0]

    # 6. Retrieve relevant chunks
    print("Retrieving relevant context...")
    relevant_chunks = query_embeddings(query_embedding)

    # 7. Generate review (Member 2 work)
    print("Generating review...")
    review = generate_review(diff, context=relevant_chunks)

    # 8. Post comment (Member 3 work)
    print("Posting comment...")
    post_comment(review)

    print("Done")

if __name__ == "__main__":
    main()
