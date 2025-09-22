"""基础 Page 封装

提供常用查找、点击、输入与显式等待，减少用例重复代码。
"""

from __future__ import annotations

from typing import Any, Tuple

from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    """页面对象基类。"""

    def __init__(self, driver: WebDriver, timeout: int = 15):
        self.driver = driver
        self.timeout = timeout

    def find(self, locator: Tuple[str, str]) -> WebElement:
        """等待元素出现并返回。"""
        return WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located(locator))

    def click(self, locator: Tuple[str, str]):
        """等待元素可点击并执行点击。"""
        element = WebDriverWait(self.driver, self.timeout).until(EC.element_to_be_clickable(locator))
        element.click()
        return element

    def type(self, locator: Tuple[str, str], text: str):
        """清空并输入文本。"""
        element = self.find(locator)
        element.clear()
        element.send_keys(text)
        return element

    def wait_visible(self, locator: Tuple[str, str]):
        """等待元素可见。"""
        return WebDriverWait(self.driver, self.timeout).until(EC.visibility_of_element_located(locator))
