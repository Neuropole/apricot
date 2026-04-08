def test_infer_intent_empty_diff():
    assert infer_intent("") == {"purpose": "", "properties": [], "edge_cases": [], "error": ""}

def test_infer_intent_short_diff():
    diff = "diff --git a/file.py b/file.py"
    intent = infer_intent(diff)
    assert "purpose" in intent
    assert "properties" in intent
    assert "edge_cases" in intent

def test_infer_intent_long_diff():
    diff = "diff --git a/file.py b/file.py" * 10000
    intent = infer_intent(diff)
    assert "purpose" in intent
    assert "properties" in intent
    assert "edge_cases" in intent

def test_generate_tests_no_context_no_intent():
    diff = "diff --git a/file.py b/file.py"
    tests = generate_tests(diff)
    assert tests.strip() != ""

def test_generate_tests_with_context_and_intent():
    diff = "diff --git a/file.py b/file.py"
    context = ["context1", "context2"]
    intent = {"purpose": "test", "properties": ["prop1", "prop2"], "edge_cases": ["case1", "case2"]}
    tests = generate_tests(diff, context, intent)
    assert tests.strip() != ""