from agent.indexing.parser import get_code_files
from agent.indexing.chunker import chunk_code
from agent.indexing.embedder import get_embeddings
from agent.indexing.vector_store import store_embeddings, query_embeddings
from agent.llm.test_generator import generate_tests
from agent.github.committer import commit_tests
import subprocess , os
from agent.llm.groq_client import generate_review
from agent.llm.groq_client import infer_intent
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

    # 5. Convert diff to embedding
    print("Embedding diff...")
    query_embedding = get_embeddings([diff])[0]

    # 6. Retrieve relevant chunks
    print("Retrieving relevant context...")
    relevant_chunks = query_embeddings(query_embedding)

    # 7. Infer intent
    print("Inferring intent...")
    if not intent or "error" in intent:
        print("Intent extraction failed, using fallback")
        intent = {"purpose": "", "properties": [], "edge_cases": []}

    print("Intent extracted:")
    print(intent)

    # 8. Generate review 
    print("Generating review...")
    review = generate_review(diff, context=relevant_chunks)

    # 9. Generate tests
    print("Generating tests...")
    tests = generate_tests(diff, context=relevant_chunks, intent=intent)
    print("Generated tests with intent:")
    print(tests)
    os.makedirs("tests", exist_ok=True)
    with open("tests/test_generated.py", "w", encoding="utf-8") as f:
        f.write(tests) # Save generated tests to a file for potential commit
    print("Generated tests saved to tests/test_generated.py")

    # 10. Combine output
    formatted_tests = f"""```bash
    pytest tests/test_generated.py
    {tests}
    ```"""

    final_output = f"""{review}

    ---

    ### Suggested Tests
    {formatted_tests}
    """

    print("\n FINAL OUTPUT:\n")
    print(final_output)

    # 11. Post comment
    print("Posting comment...")
    post_comment(final_output)

    # 12. Commit tests 
    print("Committing tests...")
    try:
        commit_tests()
    except Exception as e:
        print(f"Commit failed: {e}")

    print("Done")

if __name__ == "__main__":
    main()
