import logging
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)


def log_click(selenium_client, by, value):
    element = selenium_client.find_element(by, value)
    logger.info("Click element '{}'".format(element.tag_name))
    selenium_client.execute_script("arguments[0].click();", element)


def log_write(selenium_client, by, value, text):
    element = selenium_client.find_element(by, value)
    logger.info("Write element '{}' text: {}".format(element.tag_name, text))
    element.send_keys(text)


def select_value(selenium_client, by, value, select_value):
    log_click(selenium_client, by, value)
    Select(selenium_client.find_element(by, value)).select_by_value(select_value)


def log_wait(selenium_client, by, value, time=60):
    WebDriverWait(selenium_client, time).until(
        EC.presence_of_element_located((by, value))
    )


class image_has_been_loaded(object):
    """An expectation for checking that an image has been loaded (successfully or not).

  locator - used to find the element
  returns the WebElement once it has been loaded
  """

    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        element = driver.find_element(*self.locator)
        if driver.execute_script("return arguments[0].complete;", element):
            return element
        else:
            return False
