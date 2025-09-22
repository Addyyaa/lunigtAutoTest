"""示例 Page 对象

演示 Page Object 使用方式与元素操作（以 Settings OK 按钮为例）。
"""

from __future__ import annotations

from selenium.webdriver.common.by import By

from .base_page import BasePage
from src.core.logger import setup_logger


class SamplePage(BasePage):
    """示例页面。"""

    BTN_OK = (By.ID, "android:id/button1")

    def tap_ok(self):
        """点击 OK 按钮。"""
        setup_logger().info("点击 OK 按钮")
