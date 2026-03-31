import os
import subprocess

def commit_tests():
    try:
        branch = os.getenv("GITHUB_HEAD_REF")  # PR branch

        subprocess.run(["git", "config", "user.name", "github-actions"], check=True)
        subprocess.run(["git", "config", "user.email", "actions@github.com"], check=True)

        subprocess.run(["git", "add", "tests/"], check=True)
        subprocess.run(["git", "commit", "-m", "Add AI-generated tests"], check=True)

        subprocess.run(["git", "push", "origin", f"HEAD:{branch}"], check=True)

        print("Tests pushed to PR branch")

    except Exception as e:
        print("Commit Failed", e)