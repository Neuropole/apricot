import subprocess

def run_coverage():
    try:
        result = subprocess.run(
            ["pytest", "--cov=.", "--cov-report=term-missing"],
            capture_output=True,
            text=True
        )

        print("📊 Coverage Output:\n", result.stdout)

        return result.stdout

    except Exception as e:
        print("❌ Coverage failed:", e)
        return str(e)