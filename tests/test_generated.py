def test_empty_diff():
    assert generate_tests(diff="") == ""

def test_empty_context():
    assert generate_tests(diff="diff --git a/app.py b/app.py", context=[]) == ""

def test_intent_extraction_failure():
    assert generate_tests(diff="diff --git a/app.py b/app.py", intent={"error": "intent extraction failed"}) == ""

def test_commit_tests_failure():
    try:
        commit_tests()
        assert False
    except Exception as e:
        assert str(e) != ""

def test_generate_review_with_intent():
    diff = "diff --git a/app.py b/app.py"
    context = ["def safe_divide(a, b):"]
    intent = {"purpose": "generate tests", "properties": ["a", "b"], "edge_cases": ["a=0", "b=0"]}
    assert generate_tests(diff, context, intent) != ""