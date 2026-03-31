import subprocess
def commit_tests():
    try:
        # configue git (required in github actions)
        subprocess.run(['git','config',"--global","user.name","github-actions"],check=True)
        subprocess.run(["git","config","--global","user.email","github-actions@github.com"],
                        check=True
                        )

        # add the generated test file
        subprocess.run(["git","add","tests/test_generated.py"],check=True)
        # commit the changes
        subprocess.run(["git","commit","-m","Add AI-generated tests"],check=True)
        # push
        subprocess.run(["git","push"],check=True)
        print("Tests committed and pushed successfully.")
    except Exception as e:
        print(f"Commit Failed {e}")
