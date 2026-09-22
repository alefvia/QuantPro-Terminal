from pathlib import Path

import pytest

from packages.data_engine.rithmic_runtime import RithmicRuntimeConfig


def test_runtime_config_requires_secrets(monkeypatch):
    for name in (
        "RITHMIC_API_USER",
        "RITHMIC_API_PASSWORD",
        "RITHMIC_WSS_URL",
        "RITHMIC_KIT_DIR",
    ):
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(RuntimeError, match="RITHMIC_API_USER"):
        RithmicRuntimeConfig.from_env()


def test_runtime_config_never_accepts_plain_ws(monkeypatch):
    monkeypatch.setenv("RITHMIC_API_USER", "u")
    monkeypatch.setenv("RITHMIC_API_PASSWORD", "p")
    monkeypatch.setenv("RITHMIC_WSS_URL", "ws://example.invalid")
    monkeypatch.setenv("RITHMIC_KIT_DIR", "/tmp/proto")
    with pytest.raises(RuntimeError, match="wss://"):
        RithmicRuntimeConfig.from_env()


def test_runtime_config_reads_secure_environment(monkeypatch):
    monkeypatch.setenv("RITHMIC_API_USER", "u")
    monkeypatch.setenv("RITHMIC_API_PASSWORD", "p")
    monkeypatch.setenv("RITHMIC_WSS_URL", "wss://example.invalid")
    monkeypatch.setenv("RITHMIC_KIT_DIR", "/tmp/proto")
    cfg = RithmicRuntimeConfig.from_env()
    assert cfg.system_name == "Rithmic Test"
    assert cfg.root_symbol == "MNQ"
    assert cfg.kit_dir == Path("/tmp/proto")
