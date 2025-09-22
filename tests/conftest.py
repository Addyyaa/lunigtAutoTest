"""Pytest 全局夹具与钩子

- 提供配置、日志、capabilities 与 Appium Driver 夹具
- 用例失败时自动附加截图与 page_source 到 Allure
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Generator

import allure
import pytest
from appium.webdriver.webdriver import WebDriver
import time
from src.core.config import get_config
from src.core.driver_factory import DriverFactory
from src.core.logger import setup_logger
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture(scope="session")
def config():
    """提供配置加载器实例。"""
    return get_config()


@pytest.fixture(scope="session")
def logger():
    """提供全局 logger。"""
    return setup_logger("tests")


@pytest.fixture(scope="session")
def capabilities(config):  # type: ignore[no-untyped-def]
    """读取并返回当前设备 profile 的 capabilities。"""
    return config.load_capabilities()


@pytest.fixture(scope="session")
def appium_driver(config, capabilities, logger) -> Generator[WebDriver, None, None]:  # type: ignore[no-untyped-def]
    """创建并在会话结束时释放 Appium 驱动。"""
    factory = DriverFactory(config.values.appium_server_url, capabilities)
    driver = factory.create()
    logger.info("Appium 会话已创建")
    yield driver
    logger.info("开始关闭 Appium 会话")
    factory.quit()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item):  # type: ignore[no-untyped-def]
    """在测试阶段结束时收集执行结果，用于失败后附件处理。"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture(autouse=True)
def attach_on_failure(request, logger):  # type: ignore[no-untyped-def]
    """用例失败时自动附加截图与 page_source 到 Allure。

    注意：仅当测试显式依赖 appium_driver 时才尝试截图，避免为非 e2e 用例创建会话。
    """
    yield
    failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else False
    if not failed:
        return
    if "appium_driver" not in getattr(request, "fixturenames", ()):  # 非 e2e 用例，无需截图
        return
    try:
        driver = request.getfixturevalue("appium_driver")
        screenshot = driver.get_screenshot_as_png()
        allure.attach(screenshot, name="screenshot", attachment_type=allure.attachment_type.PNG)
        source = driver.page_source
        allure.attach(source, name="page_source", attachment_type=allure.attachment_type.XML)
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("失败附件采集异常: %s", exc)


@pytest.fixture(scope="session")
def load_json(request):
    data_file = Path(request.param).resolve()
    with open(data_file, "r") as f:
        return json.load(f)


@pytest.fixture
def wait_for_element(appium_driver):
    """等待元素真实可见、在视口内且位置稳定，并做好点击前准备后返回元素（不点击）。"""

    def _ensure_native_context():
        try:
            if getattr(appium_driver, "current_context", "NATIVE_APP") != "NATIVE_APP":
                appium_driver.switch_to.context("NATIVE_APP")
        except Exception:
            pass

    def _center_in_view(el, locator, attempts=5):
        try:
            win = appium_driver.get_window_size()
            safe_top = int(win["height"] * 0.2)
            safe_bottom = int(win["height"] * 0.8)
            for _ in range(attempts):
                rect = el.rect
                cy = rect["y"] + rect["height"] // 2
                if safe_top <= cy <= safe_bottom:
                    return
                direction = "down" if cy < safe_top else "up"
                appium_driver.execute_script(
                    "mobile: scrollGesture",
                    {
                        "left": int(win["width"] * 0.1),
                        "top": int(win["height"] * 0.2),
                        "width": int(win["width"] * 0.8),
                        "height": int(win["height"] * 0.6),
                        "direction": direction,
                        "percent": 0.7,
                    },
                )
                # 重新获取，避免 stale
                el = appium_driver.find_element(*locator)
        except Exception:
            pass

    def _hide_keyboard_if_shown():
        try:
            appium_driver.hide_keyboard()
        except Exception:
            pass

    def _wait(
        locator,
        timeout=15,
        poll=0.3,
        allow_scroll=True,
        stable_time=0.35,
        require_enabled=True,
        prepare_for_click=True,
    ):
        ignored = (NoSuchElementException, StaleElementReferenceException)
        _ensure_native_context()

        def _ready(drv):
            try:
                el = drv.find_element(*locator)
                if not el.is_displayed():
                    return False
                if require_enabled and not el.is_enabled():
                    return False
                rect = el.rect
                size = drv.get_window_size()
                in_screen = 0 <= rect["x"] < size["width"] and 0 <= rect["y"] < size["height"]
                if not in_screen:
                    return False
                pos1 = el.location
                time.sleep(stable_time)
                pos2 = el.location
                if pos1 != pos2:
                    return False
                return el
            except ignored:
                return False

        try:
            el = WebDriverWait(appium_driver, timeout, poll_frequency=poll, ignored_exceptions=ignored).until(_ready)
        except Exception:
            if not allow_scroll:
                raise
            # 滚动一次再尝试
            try:
                win = appium_driver.get_window_size()
                appium_driver.execute_script(
                    "mobile: scrollGesture",
                    {
                        "left": int(win["width"] * 0.1),
                        "top": int(win["height"] * 0.2),
                        "width": int(win["width"] * 0.8),
                        "height": int(win["height"] * 0.6),
                        "direction": "down",
                        "percent": 0.8,
                    },
                )
            except Exception:
                pass
            el = WebDriverWait(appium_driver, timeout, poll_frequency=poll, ignored_exceptions=ignored).until(_ready)

        # 点击前准备：置于安全区域、收起键盘、再次稳定检测
        if prepare_for_click:
            try:
                _center_in_view(el, locator)
                _hide_keyboard_if_shown()
                # 再次稳定校验
                pos1 = el.location
                time.sleep(stable_time)
                pos2 = el.location
                if pos1 != pos2:
                    # 若仍在动画，额外等待一次
                    time.sleep(stable_time)
            except Exception:
                pass

        return el

    return _wait

    """杀死指定的应用包名（用于参数化测试）"""
    app_package = request.param
    logger.info(f"杀死应用: {app_package}")
    
    try:
        # 方法1：使用 Appium 的 terminate_app
        if appium_driver.is_app_installed(app_package):
            appium_driver.terminate_app(app_package)
            logger.info(f"成功杀死应用: {app_package}")
        else:
            logger.warning(f"应用未安装，跳过杀死操作: {app_package}")
    except Exception as e:
        # 方法2：备用 - 使用 ADB 命令
        try:
            logger.warning(f"Appium 杀死应用失败，尝试 ADB 命令: {e}")
            appium_driver.execute_script("mobile: shell", {"command": f"am force-stop {app_package}"})
            logger.info(f"通过 ADB 成功杀死应用: {app_package}")
        except Exception as adb_e:
            logger.error(f"ADB 杀死应用也失败: {adb_e}")
            # 不抛出异常，避免影响测试继续执行


@pytest.fixture(scope="function")
def kill_apps_before_test(appium_driver: WebDriver, logger):
    """测试前后都杀死指定的应用列表（初始化和清理操作）"""
    apps_to_kill = ["com.android.settings", "com.ost.lunight"]
    
    def _kill_apps_and_go_home(stage_name):
        """杀死应用并返回桌面的通用方法"""
        logger.info(f"{stage_name}：杀死应用列表 {apps_to_kill}")
        
        for app_package in apps_to_kill:
            try:
                # 方法1：使用 Appium 的 terminate_app
                if appium_driver.is_app_installed(app_package):
                    appium_driver.terminate_app(app_package)
                    logger.info(f"成功杀死应用: {app_package}")
                else:
                    logger.warning(f"应用未安装，跳过杀死操作: {app_package}")
            except Exception as e:
                # 方法2：备用 - 使用 ADB 命令
                try:
                    logger.warning(f"Appium 杀死应用失败，尝试 ADB 命令: {e}")
                    appium_driver.execute_script("mobile: shell", {"command": f"am force-stop {app_package}"})
                    logger.info(f"通过 ADB 成功杀死应用: {app_package}")
                except Exception as adb_e:
                    logger.error(f"ADB 杀死应用也失败: {adb_e}")
                    # 不抛出异常，避免影响测试继续执行
        
        logger.info(f"{stage_name} 应用清理完成")
        
        # 可选：杀死应用后返回桌面，避免停留在被杀死的应用界面
        try:
            logger.info("按下 Home 键返回桌面")
            appium_driver.press_keycode(3)  # Android Home 键
        except Exception as e:
            logger.warning(f"返回桌面失败: {e}")
    
    # 测试前执行
    _kill_apps_and_go_home("测试前初始化")
    
    # yield 让测试执行
    yield
    
    # 测试后执行
    _kill_apps_and_go_home("测试后清理")


# 可选：如果需要更灵活的控制，可以使用独立的 fixture
@pytest.fixture(scope="function")
def kill_apps_before(appium_driver: WebDriver, logger):
    """仅在测试前杀死应用"""
    apps_to_kill = ["com.android.settings", "com.ost.lunight"]
    logger.info(f"测试前杀死应用: {apps_to_kill}")
    # ... 杀死应用的逻辑 ...


@pytest.fixture(scope="function")  
def kill_apps_after(appium_driver: WebDriver, logger, request):
    """仅在测试后杀死应用"""
    yield  # 先让测试执行
    apps_to_kill = ["com.android.settings", "com.ost.lunight"]
    logger.info(f"测试后杀死应用: {apps_to_kill}")
    # ... 杀死应用的逻辑 ...
