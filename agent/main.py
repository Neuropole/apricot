import subprocess
from agent.llm.groq_client import generate_review
from agent.github.commenter import post_comment
def get_pr_diff():
    try:
        diff = subprocess.check_output(
            ["git","diff","origin/main...HEAD"],
            text = True
        )
        return diff
    except Exception as e:
        print(f"Error getting PR diff: {e}")
        return ""
def main():
    print("Agent is started...")
    diff = get_pr_diff()
    if not diff.strip():
        print("No changes detected in the PR.")
        return
    print("Generating review based on the PR diff...")
    review = generate_review(diff)
    print("Review generated, posting to github...")
    # Here you would add code to post the review back to GitHub using their API
    post_comment(review)
    print("Review posted successfully.")
if __name__ == "__main__":
    main()
