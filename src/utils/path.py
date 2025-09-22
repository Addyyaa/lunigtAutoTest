from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resources_dir() -> Path:
    return project_root() / "resources"


def capabilities_dir() -> Path:
    return resources_dir() / "capabilities"
