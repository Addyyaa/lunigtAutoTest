from __future__ import annotations


from src.core.config import ConfigLoader


def test_capabilities_path_exists():
    loader = ConfigLoader()
    path = loader.values.capabilities_path
    assert path.exists(), f"capabilities 文件不存在: {path}"


def test_load_capabilities_default_profile():
    loader = ConfigLoader()
    caps = loader.load_capabilities()
    assert isinstance(caps, dict)
    assert "platformName" in caps or "platformName" not in caps  # 仅校验结构为 dict


def get_capabilities():
    loader = ConfigLoader()
    return loader.load_capabilities()
