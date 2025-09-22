from __future__ import annotations

from src.core.logger import setup_logger


def test_logger_setup_singleton_like():
    logger1 = setup_logger("tests")
    logger2 = setup_logger("tests")
    assert logger1 is logger2
    logger1.info("logger ok")
