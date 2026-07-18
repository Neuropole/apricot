import importlib
import sys

def test_config_model_value():
    cfg = importlib.import_module("agent.config")
    assert cfg.MODEL == "openai/gpt-oss-20b"

def test_config_model_type():
    cfg = importlib.import_module("agent.config")
    assert isinstance(cfg.MODEL, str)

def test_config_model_non_empty():
    cfg = importlib.import_module("agent.config")
    assert cfg.MODEL != ""

def test_config_module_loaded():
    assert "agent.config" in sys.modules

def test_config_model_not_none():
    cfg = importlib.import_module("agent.config")
    assert cfg.MODEL is not None