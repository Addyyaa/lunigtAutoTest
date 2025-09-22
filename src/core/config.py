"""配置加载模块

职责：
- 统一加载运行所需配置（平台、Appium 服务器、capabilities 文件路径、设备 profile）
- 支持环境变量与 .env 覆盖，遵循 SRP，避免硬编码
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppiumConfig:
    """Appium 运行所需核心配置。"""

    platform_name: str
    appium_server_url: str
    capabilities_path: Path
    device_profile: str


class ConfigLoader:
    """加载与提供测试运行所需配置。

    优先级：环境变量 > .env > 默认值/资源文件
    """

    def __init__(self) -> None:
        load_dotenv()  # 加载 .env
        self.project_root = Path(__file__).resolve().parents[2]
        self.resources_dir = self.project_root / "resources"
        self.cap_dir = self.resources_dir / "capabilities"

        self._config = AppiumConfig(
            platform_name=os.getenv("PLATFORM_NAME", "Android"),
            appium_server_url=os.getenv("APPIUM_SERVER_URL", "http://127.0.0.1:4723"),
            capabilities_path=self._resolve_capabilities_path(),
            device_profile=os.getenv("DEVICE_PROFILE", "default"),
        )

    def _resolve_capabilities_path(self) -> Path:
        """根据平台推断默认的 capabilities 文件路径。"""
        filename = "android.json" if os.getenv("PLATFORM_NAME", "Android").lower() == "android" else "ios.json"
        return self.cap_dir / filename

    @property
    def values(self) -> AppiumConfig:
        """返回不可变配置快照。"""
        return self._config

    def load_capabilities(self) -> Dict[str, Any]:
        """读取 capabilities 文件，并按 `device_profile` 选择具体配置。"""
        path = self._config.capabilities_path
        if not path.exists():
            raise FileNotFoundError(f"未找到 capabilities 文件: {path}")
        with path.open("r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)
        profile = data.get(self._config.device_profile) or data.get("default")
        if not isinstance(profile, dict):
            raise ValueError("capabilities 配置格式不正确，缺少 default 或指定 profile")
        return profile


def get_config() -> ConfigLoader:
    """获取配置加载器实例。"""
    return ConfigLoader()
