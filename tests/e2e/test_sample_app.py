from __future__ import annotations
import os
import pytest
import time

from src.core import logger
from src.page_objects.sample_page import SamplePage
from src.core.logger import setup_logger
from selenium.webdriver.common.by import By
from tests.unit.image_tools import capture_element_image
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import numpy as np
import json
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.extensions.android.nativekey import AndroidKey

from appium.webdriver import Remote


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


@pytest.mark.e2e
@pytest.mark.parametrize("date_str,lunar_phase", LUNAR_CASES)
@pytest.mark.parametrize("kill_app", ["com.android.settings", "com.ost.lunight"], indirect=True)
def test_lunar_phase(appium_driver: Remote, sample_page, wait_for_element, date_str, lunar_phase, kill_app):
    logger.info(f"测试日期: {date_str}, 月相: {lunar_phase}")
    year, month, day = date_str.split("-")

    # 将日期作为系统时间
    appium_driver.execute_script("mobile: startActivity", {"component": "com.android.settings/.Settings"})
    el_setting_search = page.find((AppiumBy.ACCESSIBILITY_ID, "搜索设置"))
    el_setting_search.click()
    el_setting_search_input = page.find((AppiumBy.ID, "com.android.settings.intelligence:id/search_src_text"))
    el_setting_search_input.send_keys("设置时间")
    el_setting_time_locator = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("设置时间")')
    el = wait_for_element(el_setting_time_locator)
    el.click()
    el_time_settings = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("设置日期")')
    el = wait_for_element(el_time_settings)
    el.click()
    # 展开年份下拉菜单（只点一次，避免收起）
    el_year_dropdown_locator = (AppiumBy.ID, "com.android.settings:id/sesl_date_picker_calendar_header_text")
    el_header = wait_for_element(el_year_dropdown_locator, allow_scroll=False, require_enabled=True)
    el_header.click()

    # 直接滚动并点击目标年份/月份/日期，避免键码输入兼容问题
    # 年份
    for ytext in (f"{year}年", year):
        try:
            el_year = wait_for_element(
                (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{ytext}")'),
                allow_scroll=True,
                require_enabled=True,
                prepare_for_click=False,
            )
            el_year.click()
            break
        except Exception:
            continue

    # 月份（部分 ROM 为“9月”或“09月”）
    for mtext in (f"{int(month)}月", f"{month}月"):
        try:
            el_month = wait_for_element(
                (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{mtext}")'),
                allow_scroll=True,
                require_enabled=True,
                prepare_for_click=False,
            )
            el_month.click()
            break
        except Exception:
            continue

    # 日期（部分 ROM 为“1”或“01”）
    for dtext in (str(int(day)), day):
        try:
            el_day = wait_for_element(
                (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{dtext}")'),
                allow_scroll=True,
                require_enabled=True,
            )
            el_day.click()
            break
        except Exception:
            continue

    # 完成
    el_done_locator = (AppiumBy.ID, "android:id/button1")
    el_done = wait_for_element(el_done_locator)
    el_done.click()
