"""Appium 驱动工厂

职责：
- 依据 capabilities 与服务器地址创建 `webdriver.Remote`
- 兼容不同版本的 appium-python-client：优先平台 Options，其次 AppiumOptions，最后回退 desired_capabilities
"""
from __future__ import annotations

from typing import Any, Dict, Optional
from importlib import import_module

from appium import webdriver


class DriverFactory:
    """Driver 工厂：统一管理创建与销毁，避免重复会话。"""

    def __init__(self, server_url: str, capabilities: Dict[str, Any]):
        self._server_url = server_url
        self._capabilities = capabilities
        self._driver: Optional[webdriver.Remote] = None

    def create(self) -> webdriver.Remote:
        """创建或返回已存在的 Appium Remote 实例。"""
        if self._driver is None:
            kwargs = self._build_remote_kwargs(self._capabilities)
            self._driver = webdriver.Remote(command_executor=self._server_url, **kwargs)
        return self._driver

    def quit(self) -> None:
        """关闭并清理驱动会话。"""
        if self._driver is not None:
            self._driver.quit()
            self._driver = None

    @staticmethod
    def _build_remote_kwargs(caps: Dict[str, Any]) -> Dict[str, Any]:
        """构建 Remote 初始化参数，包含 Options 或 desired_capabilities。"""
        platform = str(caps.get("platformName", "Android")).lower()

        if platform == "android":
            try:
                UiAutomator2Options = getattr(import_module("appium.options.android"), "UiAutomator2Options")
                return {"options": UiAutomator2Options().load_capabilities(caps)}
            except Exception:
                pass

        if platform == "ios":
            try:
                XCUITestOptions = getattr(import_module("appium.options.ios"), "XCUITestOptions")
                return {"options": XCUITestOptions().load_capabilities(caps)}
            except Exception:
                pass

        try:
            AppiumOptions = getattr(import_module("appium.options.common"), "AppiumOptions")
            return {"options": AppiumOptions().load_capabilities(caps)}
        except Exception:
            return {"desired_capabilities": caps}
