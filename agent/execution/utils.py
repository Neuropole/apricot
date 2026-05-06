def extract_errors(test_result):
    if test_result["success"]:
        return ""

    errors = test_result["stderr"]

    # trim huge logs (important for LLM token limits)
    return errors[-3000:]