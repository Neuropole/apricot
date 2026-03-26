import os

def get_code_files(root_dir="."):
    code_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                code_files.append(os.path.join(root, file))
    return code_files