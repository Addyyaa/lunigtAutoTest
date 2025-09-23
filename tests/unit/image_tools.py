"""捕获元素截图"""

from selenium.webdriver.remote.webelement import WebElement
import cv2
import numpy as np
from typing import Any, Union
from pathlib import Path
import logging


def capture_element_image(element: WebElement):
    """捕获元素截图"""
    screenshot = element.screenshot_as_png

    # 获取元素位置和大小
    location = element.location
    size = element.size
    left = location["x"]
    top = location["y"]
    right = left + size["width"]
    bottom = top + size["height"]

    np_array = np.frombuffer(screenshot, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    cv2.imshow("PNG Image from File", image)
    if image is not None:
        cropped_image = image[top:bottom, left:right]
        return cropped_image

    return None


def test_element_image_match_cv(pic_data: np.ndarray[Any, np.dtype[np.uint8]], expected_img: Union[str, Path]):
    """
    @param pic_data: 元素截图
    @param expected_img: 预期图片
    @return: 匹配度
    """
    logger = logging.getLogger("tests")
    if isinstance(expected_img, str):
        expected_img = Path(expected_img)
    if isinstance(pic_data, (bytes, bytearray)):
        array = np.frombuffer(pic_data, np.uint8)
        element_data = cv2.imdecode(array, cv2.IMREAD_GRAYSCALE)
    # 2. 模板匹配
    expected_img = cv2.imread(expected_img, cv2.IMREAD_GRAYSCALE)
    result = cv2.matchTemplate(element_data, expected_img, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    logger.info(f"图片匹配度为{max_val}")
    assert max_val > 0.8, f"图片匹配失败，匹配度为{max_val}"


if __name__ == "__main__":
    actual_img = cv2.imread("tests\e2e\screenshots\screenshot.png", cv2.IMREAD_GRAYSCALE)
    test_element_image_match_cv(actual_img, "src\image_to_match\\new moon.png")
