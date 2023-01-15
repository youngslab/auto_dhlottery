
# web driver
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# web element
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

# wait elements
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# alert
from selenium.webdriver.common.alert import Alert

# multi-dispatch
from plum import dispatch  # mulitple dispatch
from typing import Tuple, Union, List

# pyautogui
import pyautogui
import pyperclip


import time

# Support enum
from enum import Enum


_default_timeout = 60


class ImageElement:
    def __init__(self, center):
        self.center = center
        pass


def wait(func, *, timeout=_default_timeout, interval=0.5):
    start = time.time()
    curr = 0
    retry = 0
    while True:
        curr = time.time() - start
        retry = retry + 1
        res = func()
        if res != None and res != 0:
            return res

        if curr > timeout:
            print(
                f"Timeout! wait_until takes {curr}. timeout={timeout}, interval={interval}, retry={retry}")
            break

        # every 500ms
        time.sleep(interval)

    return res


def get_clickable(driver: WebDriver, by: str, path: str, timeout: int = _default_timeout) -> Union[WebElement, None]:
    try:
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, path)))
    except Exception as e:
        return None


@dispatch
def get_element(driver: WebDriver, by: str, path: str, timeout: int = _default_timeout) -> Union[WebElement, None]:
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, path)))
    except Exception as e:
        return None


@dispatch
def get_element(img: str, *, timeout: int = _default_timeout, grayscale: bool = True, confidence: float = .9) -> Union[ImageElement, None]:
    def find_image(): return pyautogui.locateCenterOnScreen(
        img, grayscale=grayscale, confidence=confidence)
    center = wait(lambda: find_image(), timeout=timeout)
    if not center:
        return None
    return ImageElement(center)


def get_elements(driver: WebDriver, by: str, path: str, timeout: int = _default_timeout) -> List[WebElement]:
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((by, path)))
    except Exception as e:
        return []


def get_alert(driver: WebDriver, timeout: int = _default_timeout):
    try:
        WebDriverWait(driver, timeout).until(
            EC.alert_is_present(), "Can not find an alert window")
        return driver.switch_to.alert
    except Exception as e:
        return None


def get_window_handle(driver: WebDriver, title: str):
    current = driver.current_window_handle
    result = None
    handles = driver.window_handles
    handles.remove(current)
    for handle in handles:
        driver.switch_to.window(handle)
        if driver.title.find(title) >= 0:
            result = handle
            break
    driver.switch_to.window(current)
    return result


@dispatch
def click(driver: WebDriver, element: WebElement):
    if not driver or not element:
        return False
    try:
        element.click()
    except:
        driver.execute_script("arguments[0].click();", element)
    return True


@dispatch
def click(element: ImageElement):
    if not element:
        return False

    if not element.center:
        return False

    pyautogui.click(element.center)
    return True


@dispatch
def type(element: WebElement, text: str):
    element.clear()
    if element.get_attribute('value'):
        return False
    element.send_keys(text)
    return True


def select(element: WebElement, text: str):
    select = Select(element)
    select.select_by_visible_text(text)
    return True


class Frame:
    def __init__(self, driver, element: WebElement, timeout=_default_timeout):
        self.driver = driver
        self.frame = element

    def __enter__(self):
        self.driver.switch_to.frame(self.frame)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.switch_to.parent_frame()


class Window:
    def __init__(self, driver: WebDriver, handle):
        self.driver = driver
        self.prev_window_handle = driver.current_window_handle
        self.next_window_handle = handle

    def __enter__(self):
        self.driver.switch_to.window(self.next_window_handle)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.switch_to.window(self.prev_window_handle)


class Automatic:

    def create_edge_driver(*, headless=False):
        options = webdriver.EdgeOptions()
        options.add_argument('log-level=3')
        if headless:
            options.add_argument('headless')
            options.add_argument('disable-gpu')
        service = Service(EdgeChromiumDriverManager().install())
        return webdriver.Edge(options=options, service=service)

    class DriverType(Enum):
        Edge = 1
        Chrome = 2

    def create(t: DriverType, *, headless=False):
        if t == Automatic.DriverType.Edge:
            drv = Automatic.create_edge_driver(headless=headless)
        else:
            # TODO: Not implemented yet
            raise Exception("Not implemented yet.")
        return Automatic(drv)

    def __init__(self, driver: WebDriver, *, timeout=60):
        self.driver = driver
        self.timeout = timeout

    def go(self, url: str):
        return self.driver.get(url)

    @dispatch
    def get_element(self, by: str, path: str, *, timeout: int = _default_timeout) -> Union[WebElement, None]:
        return get_element(self.driver, by, path, timeout)

    @dispatch
    def get_element(self, img: str, *, timeout: int = _default_timeout, grayscale: bool = True, confidence: float = .9) -> Union[ImageElement, None]:
        return get_element(img, timeout=timeout, grayscale=grayscale, confidence=confidence)

    @dispatch
    def get_elements(self, by: str, path: str, *, timeout: int = _default_timeout) -> List[WebElement]:
        return get_elements(self.driver, by, path, timeout)

    def get_clickable(self, by: str, path: str, *, timeout: int = _default_timeout) -> Union[WebElement, None]:
        return get_clickable(self.driver, by, path, timeout)

    def select(self, element: WebElement, text: str):
        return select(element, text)

    # TYPE

    @dispatch
    def type(self, element: WebElement, text: str):
        return type(element, text)

    @dispatch
    def type(self, by: str, path: str, text: str, *, timeout=_default_timeout):
        elem = self.get_clickable(by, path, timeout=timeout)
        if not elem:
            return False
        return type(elem, text)

    # CLICK

    @dispatch
    def click(self, element: WebElement):
        return click(self.driver, element)

    @dispatch
    def click(self, by: str, path: str, *, timeout=_default_timeout):
        elem = self.get_clickable(by, path, timeout=timeout)
        if not elem:
            print("Error element not found")
            return False
        return click(self.driver, elem)

    @dispatch
    def click(self, element: ImageElement):
        return click(element)

    @dispatch
    def click(self, img: str):
        elem = self.get_element(img)
        if not elem:
            return False
        return click(elem)

    @dispatch
    def get_frame(self, element: WebElement):
        if not element:
            return None
        return Frame(self.driver, element)

    # Window APIs
    def get_window_handle(self, title: str, timeout=_default_timeout):
        return wait(lambda: get_window_handle(self.driver, title), timeout=timeout)

    @dispatch
    def get_window(self, handle: str):
        if not handle:
            return None
        return Window(self.driver, handle)

    def get_alert(self, timeout=_default_timeout):

        return get_alert(self.driver, timeout=timeout)

    def accept_alert(self, *, timeout=_default_timeout):
        alert = self.get_alert(timeout=timeout)
        if not alert:
            return False
        alert.accept()
        return True

    def accept_alert_with_text(self, expeted: str, timeout=_default_timeout):
        alert = self.get_alert(timeout=timeout)
        if not alert:
            return False
        if alert.text.find(expeted) < 0:
            return False
        alert.accept()
        return True

    def activate(self, title: str):
        return activate(title)

    def execute_script(self, script, *args):
        return self.driver.execute_script(script, *args)
