import logging
from random import choice
import time
from io import BytesIO
from os import environ
import phonenumbers
from phonenumbers.phonenumberutil import region_code_for_country_code
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from smscode import ManualSmsReceiver
from python_anticaptcha import AnticaptchaClient, ImageToTextTask
from selenium.common.exceptions import TimeoutException
from selenium_utils import (
    log_click,
    log_write,
    select_value,
    image_has_been_loaded,
    log_wait,
)

api_key = environ["KEY"]
DOMAINS = ["hotmail.com", "outlook.com"]

logger = logging.getLogger(__name__)

alert_script = 'return Array.from(document.getElementsByClassName("alert-error")).filter(function (el) { return el.style.display != "none"; })'


def sign_up(captcha_client, selenium_client, sms_receiver, data):
    selenium_client.get("https://outlook.live.com/owa/")
    open_form(selenium_client)
    domain = choice(DOMAINS)
    step_username(selenium_client, data["username"], domain)
    step_password(selenium_client, data["password"])
    step_name(selenium_client, data["first_name"], data["last_name"])
    step_personal(selenium_client, data["country"], data["birth_date"])
    step_captcha(selenium_client, captcha_client)
    if check_for_sms_verification(selenium_client):
        step_phone_verification(selenium_client, sms_receiver)
    # Finish registration
    log_wait(selenium_client, By.CLASS_NAME, "ms-CommandBar")
    return {
        "email": "{}@{}".format(data["username"], domain),
        "password": data["password"],
    }


def check_for_sms_verification(selenium_client):
    try:
        log_wait(selenium_client, By.CLASS_NAME, "forSmsHip")
        return True
    except TimeoutException:
        return False


def open_form(selenium_client):
    log_wait(selenium_client, By.CLASS_NAME, "sign-in-link")
    log_click(selenium_client, By.CLASS_NAME, "sign-in-link")
    log_wait(selenium_client, By.ID, "signup")
    log_click(selenium_client, By.ID, "signup")
    logger.info("Started wizard")


def step_username(selenium_client, username, domain):
    # Wizard - step 1
    log_write(selenium_client, By.NAME, "MemberName", username)
    log_click(selenium_client, By.ID, "LiveDomainBoxList")
    select_value(selenium_client, By.ID, "LiveDomainBoxList", domain)
    log_click(selenium_client, By.ID, "iSignupAction")
    logger.info("Submitted wizard for step 1")


def step_password(selenium_client, password):
    # Wizard - step 2
    log_wait(selenium_client, By.NAME, "Password")
    log_write(selenium_client, By.NAME, "Password", password)
    log_click(selenium_client, By.ID, "iSignupAction")
    logger.info("Submitted wizard for step 2")


def step_name(selenium_client, first_name, last_name):
    # Wizard - step 3
    log_wait(selenium_client, By.NAME, "FirstName")
    log_write(selenium_client, By.NAME, "FirstName", first_name)
    log_wait(selenium_client, By.ID, "LastName")
    log_write(selenium_client, By.ID, "LastName", last_name)
    log_click(selenium_client, By.ID, "iSignupAction")
    logger.info("Submitted wizard for step 3")


def step_personal(selenium_client, country, birth_date):
    # Wizard - step 4
    log_wait(selenium_client, By.NAME, "Country")
    select_value(selenium_client, By.NAME, "Country", country)
    select_value(selenium_client, By.NAME, "BirthMonth", str(birth_date.month))
    select_value(selenium_client, By.NAME, "BirthDay", str(birth_date.day))
    select_value(selenium_client, By.NAME, "BirthYear", str(birth_date.year))
    log_click(selenium_client, By.ID, "iSignupAction")
    logger.info("Submitted wizard for step 3")


def step_captcha(selenium_client, captcha_client):
    # Wizard - step 5
    visual_xpath = "//img[@alt='Visual Challenge']"
    locator = (By.XPATH, visual_xpath)
    log_wait(selenium_client, *locator)
    WebDriverWait(selenium_client, 60).until(EC.presence_of_element_located(locator))
    WebDriverWait(selenium_client, 60).until(image_has_been_loaded(locator))
    image = selenium_client.find_element(By.XPATH, visual_xpath).screenshot_as_png
    captcha_text = solve_captcha(captcha_client, image)
    selenium_client.find_element_by_xpath(
        "//label[@id='wlspispHipInstructionContainer']/..//input[@type='text']"
    ).send_keys(captcha_text)
    log_click(selenium_client, By.ID, "iSignupAction")
    validate_error(selenium_client, "Captcha error")
    logger.info("Submitted wizard for step 5")


def validate_error(selenium_client, label):
    time.sleep(1)
    elements = selenium_client.execute_script(alert_script)
    if len(elements) > 0:
        raise Exception("{}: {}".format(label, elements[0].text))


def solve_captcha(captcha_client, image):
    logger.info("Submitted task to Anticaptcha")
    task = ImageToTextTask(BytesIO(image))
    job = captcha_client.createTask(task)
    job.join()
    captcha_text = job.get_captcha_text()
    return captcha_text


def step_phone_verification(selenium_client, sms_receiver):
    # Wizard - step 6 - phone verification (optional)
    logger.info("Submitted wizard for step 4")
    phone = phonenumbers.parse(sms_receiver.get_phone_number())
    country = region_code_for_country_code(phone.country_code)
    select_value(
        selenium_client,
        By.XPATH,
        "//div[@id='wlspispHipChallengeContainer']//select",
        country,
    )
    log_write(
        selenium_client,
        By.XPATH,
        "//div[@id='wlspispHipChallengeContainer']//input",
        phone.national_number,
    )
    log_click(
        selenium_client,
        By.XPATH,
        "//div[@id='wlspispHipControlButtonsContainer']//a[@title='Send SMS code']",
    )
    validate_error(selenium_client, "Code error")
    text = sms_receiver.get_latest_sms(phone)
    code = text.split(":")[1].strip()
    log_write(
        selenium_client,
        By.XPATH,
        "//label[@id='wlspispHipSolutionContainer']//input",
        code,
    )
    log_click(selenium_client, By.ID, "iSignupAction")


def main():
    from selenium.webdriver import Chrome
    from provider import Faker, Provider

    logging.basicConfig(level=environ.get("LOGLEVEL", "INFO"))
    captcha_client = AnticaptchaClient(environ["KEY"])
    selenium_client = Chrome()
    smscode = ManualSmsReceiver()
    fake = Faker()
    fake.add_provider(Provider)
    sign_up(
        captcha_client=captcha_client,
        selenium_client=selenium_client,
        sms_receiver=smscode,
        data={
            "username": fake.username(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "country": "RU",
            "birth_date": fake.birth_date(),
            "password": fake.password(),
        },
    )


if __name__ == "__main__":
    main()
