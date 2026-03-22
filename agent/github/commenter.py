import os
from github import Github
def format_comment(comment: str) -> str:
    return f"""
**Automated Code Review Comment:**
{comment}
"""
def post_comment(comment: str):
    token = os.getenv("GITHUB_TOKEN")
    repo_name = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("PR_NUMBER")

    if not all([token, repo_name, pr_number]):
        raise Exception("Missing GitHub environment variables. Please set GITHUB_TOKEN, GITHUB_REPOSITORY, and PR_NUMBER.")
    g = Github(token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(int(pr_number))
    pr.create_issue_comment(format_comment(comment))

if __name__ == "__main__":
    post_comment("This is a test comment from the GitHub commenter module.")