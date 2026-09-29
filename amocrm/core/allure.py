"""Allure utilities."""

import allure


def attach_screenshot(name: str = "screenshot", page_or_driver=None):
    """Прикрепить скриншот к отчёту."""
    try:
        if page_or_driver is None:
            return

        # Playwright или Selenium
        if hasattr(page_or_driver, "screenshot"):
            # Playwright page
            screenshot_bytes = page_or_driver.screenshot()
            allure.attach(screenshot_bytes, name=name, attachment_type=allure.AttachmentType.PNG)
        elif hasattr(page_or_driver, "get_screenshot_as_png"):
            # Selenium driver
            screenshot_bytes = page_or_driver.get_screenshot_as_png()
            allure.attach(screenshot_bytes, name=name, attachment_type=allure.AttachmentType.PNG)
    except Exception:
        pass


def attach_log(name: str, content: str):
    """Прикрепить текстовый лог."""
    allure.attach(content, name=name, attachment_type=allure.AttachmentType.TEXT)


def attach_json(name: str, data: dict):
    """Прикрепить JSON."""
    import json

    allure.attach(json.dumps(data, indent=2), name=name, attachment_type=allure.AttachmentType.JSON)


def add_description(description: str):
    """Добавить описание теста."""
    allure.dynamic.description(description)


def add_story(story: str):
    """Добавить историю (Allure label)."""
    allure.dynamic.story(story)


def add_feature(feature: str):
    """Добавить фичу (Allure label)."""
    allure.dynamic.feature(feature)


def add_severity(severity: str):
    """Добавить severity (blocker, critical, normal, minor, trivial)."""
    allure.dynamic.severity(severity)
