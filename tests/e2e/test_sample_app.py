from __future__ import annotations
import os
import pytest
import time

from src.core import logger
from src.page_objects.sample_page import SamplePage
from src.core.logger import setup_logger
from selenium.webdriver.common.by import By
from tests.unit.image_tools import capture_element_image, test_element_image_match_cv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
import json
from appium.webdriver.common.appiumby import AppiumBy

from appium.webdriver import Remote
from selenium.common.exceptions import WebDriverException


import cv2
import pdb

page = None
logger = setup_logger()


@pytest.fixture(scope="module")
def sample_page(appium_driver):
    global page
    page = SamplePage(appium_driver)
    yield page
    page = None


@pytest.mark.e2e
@pytest.mark.skip(reason="示例占位：请在有对应 UI 时去除跳过并完善断言")
def test_sample_ok_button(appium_driver):
    # 占位步骤：当目标 App 有 OK 按钮时，可直接点击并断言
    page.tap_ok()


@pytest.mark.e2e
def test_sample2(appium_driver, sample_page):
    logger.info("test_sample2")
    page.tap_ok()


@pytest.mark.e2e
def test_capabilities(config):
    capabilities = config.load_capabilities()


@pytest.mark.e2e
def test_get_element_presence(appium_driver):
    el_home = '//android.widget.Image[@text="home-active"]'
    try:
        home_element = WebDriverWait(appium_driver, 4, poll_frequency=0.5).until(
            EC.presence_of_element_located((By.XPATH, el_home))
        )
        if home_element is not None:
            home_element.click()
        else:
            logger.info("Home element is not present")
            pytest.fail("首页tab不存在，无法进入首页")

    except:
        logger.info("Home element is not present")
    el = page.find((By.XPATH, "(//android.view.View[@resource-id])[1]"))
    base_dir = os.path.dirname(os.path.abspath(__file__))
    screenshot_dir = os.path.join(base_dir, "screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshot_dir, "screenshot.png")
    png_data = el.screenshot_as_png
    with open(screenshot_path, "wb") as f:
        f.write(png_data)
    image = cv2.imread(screenshot_path)

    cv2.imshow("PNG Image from File", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    pdb.set_trace()
    image = capture_element_image(el)
    if image is not None:
        cv2.imshow("PNG Image from File", image)
        pdb.set_trace()
    else:
        logger.info("图片不存在")


data_file = os.path.join(os.path.dirname(__file__), "..", "src", "test_data", "data.json")


def get_lunar_phase_data(json_data):
    return json_data["lunar phase"]


def _load_lunar_cases():
    data_file = os.path.join(os.path.dirname(__file__), "..", "..", "src", "test_data", "data.json")
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    cases = []
    for item in data["lunar phase"]:
        for date_str, lunar_phase in item.items():
            cases.append((date_str, lunar_phase))
    return cases


LUNAR_CASES = _load_lunar_cases()


def cold_launch(appium_driver: Remote, package: str, activity: str):
    # 1) 强杀，确保进程退出
    try:
        appium_driver.terminate_app(package)
    except Exception:
        try:
            appium_driver.execute_script("mobile: shell", {"command": "am", "args": ["force-stop", package]})
        except Exception:
            pass

    # 2) 冷启动：用 component + MAIN/LAUNCHER + NEW_TASK|CLEAR_TASK
    try:
        appium_driver.execute_script(
            "mobile: startActivity",
            {
                "component": f"{package}/{activity}",
                "intentAction": "android.intent.action.MAIN",
                "intentCategory": "android.intent.category.LAUNCHER",
                "intentFlags": 0x10000000 | 0x00008000,  # FLAG_ACTIVITY_NEW_TASK | FLAG_ACTIVITY_CLEAR_TASK
            },
        )
    except WebDriverException:
        # 3) 兜底：直接调用 ADB am start -S
        appium_driver.execute_script(
            "mobile: shell",
            {"command": "am", "args": ["start", "-S", "-W", "-n", f"{package}/{activity}"]},
        )


def get_lunar_app_moon_image(appium_driver: Remote, lunar_phase: str, save_path: bool = False):
    logger.info("开始截取图片（冷启动）")
    cold_launch(appium_driver, "com.ost.lunight", "io.dcloud.PandoraEntry")
    appium_driver.wait_activity("io.dcloud.PandoraEntry", timeout=10, interval=1)

    def middle_click():
        logger.info("点击屏幕中间区域")
        size = appium_driver.get_window_size()
        width = size["width"]
        height = size["height"]
        appium_driver.tap([(width * 0.1, height * 0.1)], 1)

    middle_click()
    time.sleep(0.5)
    el = page.find((By.XPATH, "(//android.view.View[@resource-id])[1]"))
    base_dir = os.path.dirname(os.path.abspath(__file__))
    screenshot_dir = os.path.join(base_dir, "..", "..", "src", "image_to_match")
    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshot_dir, f"{lunar_phase}.png")
    if save_path:
        with open(screenshot_path, "wb") as f:
            f.write(el.screenshot_as_png)
            logger.info(f"保存图片到{screenshot_path}")
    else:
        return el.screenshot_as_png


@pytest.mark.e2e
@pytest.mark.parametrize("date_str,lunar_phase", LUNAR_CASES)
def test_lunar_phase(appium_driver: Remote, sample_page, wait_for_element, date_str, lunar_phase):
    logger.info(f"测试日期: {date_str}, 月相: {lunar_phase}")
    year, month, day = date_str.split("-")
    appium_driver.execute_script("mobile: startActivity", {"component": "com.android.settings/.Settings"})
    time.sleep(1)
    el_setting_time_locator = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("设置日期").instance(0)')
    try:
        el = WebDriverWait(appium_driver, 10, poll_frequency=0.5).until(
            EC.presence_of_element_located(el_setting_time_locator)
        )
        if el is not None:
            logger.info("设置日期已存在，无需进行搜索")
            el.click()

    except Exception as e:
        logger.info(f"设置日期不存在: {e}")

        el_setting_search = page.find((AppiumBy.ACCESSIBILITY_ID, "搜索设置"))
        el_setting_search.click()
        logger.info("点击搜索设置")
        el_setting_search_input = page.find((AppiumBy.ID, "com.android.settings.intelligence:id/search_src_text"))
        el_setting_search_input.send_keys("设置时间")
        logger.info("输入设置时间")
        el_setting_time_locator = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("设置时间").instance(0)')
        el = wait_for_element(el_setting_time_locator)
        el.click()
        logger.info("点击设置时间")
        el_time_settings = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("设置日期")')
        el = wait_for_element(el_time_settings)
        time.sleep(1)
        el.click()
    # 将日期作为系统时间

    logger.info("点击设置日期")
    # 展开年份下拉菜单（只点一次，避免收起）
    el_year_dropdown_locator = (AppiumBy.ID, "com.android.settings:id/sesl_date_picker_calendar_header_text")
    el_header = wait_for_element(el_year_dropdown_locator, allow_scroll=False, require_enabled=True)
    el_header.click()
    # 点击年份进入手动输入年份
    el_year_click = (AppiumBy.ANDROID_UIAUTOMATOR, r'new UiSelector().textMatches("\d{4}(.*?)年")')
    el = wait_for_element(el_year_click)
    el.click()
    el.clear()
    logger.info("点击年份进入手动输入年份")
    # 使用 UiAutomator2 的 type 方法输入年份
    logger.info(f"通过 UiAutomator2 type 方法输入年份: {year}")
    # 先找到输入框并点击确保焦点
    el_year_input = (AppiumBy.ANDROID_UIAUTOMATOR, r'new UiSelector().textMatches("(\d{4}.*?年|, 年)")')
    el = wait_for_element(el_year_input)
    el.click()
    time.sleep(0.3)  # 等待焦点稳定

    # 使用 UiAutomator2 的原生输入
    appium_driver.execute_script("mobile: type", {"text": str(year)})
    logger.info(f"UiAutomator2 type 输入年份成功: {year}")
    time.sleep(0.5)  # 等待输入完成

    # 通用的日期输入函数
    def input_date_field(field_name, field_value, field_pattern):
        """通用的日期字段输入函数"""
        try:
            logger.info(f"开始输入{field_name}: {field_value}")
            el_field = (AppiumBy.ANDROID_UIAUTOMATOR, field_pattern)
            el = wait_for_element(el_field, timeout=5)
            el.click()
            logger.info(f"点击{field_name}输入框")
            time.sleep(0.3)
            el.clear()
            logger.info(f"清空{field_name}")
            appium_driver.execute_script("mobile: type", {"text": str(field_value)})
            logger.info(f"UiAutomator2 type 输入{field_name}成功: {field_value}")
            time.sleep(0.5)
        except Exception as e:
            logger.warning(f"{field_name}输入失败: {e}")

    # 输入月份
    month_int = int(month)  # 去掉前导零，如 "09" -> 9
    input_date_field("月份", month_int, r'new UiSelector().textMatches("(\d{2},\s+月|, 月)")')

    # 输入日期
    day_int = int(day)  # 去掉前导零，如 "01" -> 1
    input_date_field("日期", day_int, r'new UiSelector().textMatches("(\d{1,2},\s+日|, 日)")')

    # 最后统一点击完成
    try:
        el_done = (AppiumBy.ID, "android:id/button1")
        el = wait_for_element(el_done)
        el.click()
        logger.info(f"日期设置完成: {year}-{month}-{day}")
    except Exception as e:
        logger.error(f"点击完成按钮失败: {e}")
        # 尝试其他可能的完成按钮
        try:
            el_done_alt = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("完成")')
            el = wait_for_element(el_done_alt, timeout=3)
            el.click()
            logger.info("通过备用方式点击完成")
        except Exception as e:
            logger.error(f"所有完成按钮都无法点击: {e}")

    # 调用截取图片函数
    lunar_bytes = get_lunar_app_moon_image(appium_driver, lunar_phase, save_path=False)
    expected_img = os.path.join(os.path.dirname(__file__), "..", "..", "src", "image_to_match", f"{lunar_phase}.png")
    logger.info(f"对比月相: {lunar_phase}")
    try:
        test_element_image_match_cv(lunar_bytes, expected_img)
    except Exception as e:
        logger.error(f"月相对比失败: {e}")
        pytest.fail(f"月相对比失败: {e}")
