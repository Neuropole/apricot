import subprocess

def run_tests():
    try:
        result = subprocess.run(
            ["pytest", "tests/"],
            capture_output=True,
            text=True
        )

        stdout = result.stdout
        stderr = result.stderr
        exit_code = result.returncode

        print("🧪 Pytest STDOUT:\n", stdout)
        print("❌ Pytest STDERR:\n", stderr)
        print(f"Exit Code: {exit_code}")

        return {
            "success": exit_code == 0,
            "stdout": stdout,
            "stderr": stderr
        }

    except Exception as e:
        print("❌ Test execution failed:", e)
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e)
        }