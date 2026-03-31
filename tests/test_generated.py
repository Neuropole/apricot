import pytest
import os
from agent.github.committer import commit_tests
from agent.main import get_pr_diff

def test_commit_tests():
    commit_tests()

def test_get_pr_diff_empty():
    with pytest.raises(subprocess.CalledProcessError):
        get_pr_diff()

def test_commit_tests_exception():
    try:
        commit_tests()
    except Exception as e:
        assert str(e)

def test_get_pr_diff_no_diff():
    diff = get_pr_diff()
    assert diff.strip() == ""

def test_commit_tests_push():
    subprocess.run(["git", "config", "user.name", "github-actions"], check=True)
    subprocess.run(["git", "config", "user.email", "actions@github.com"], check=True)
    commit_tests()