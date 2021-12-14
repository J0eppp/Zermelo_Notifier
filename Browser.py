from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException
from time import sleep


class Browser:
    def __init__(self):
        self.driver = webdriver.Chrome()

    def login_get_token(self, schoolname: str, username: str, password: str, single_sign_on: bool) -> str:
        print("Getting token...")
        self.get_portal(schoolname)
        self.login_portal(username, password, single_sign_on)
        return self.get_token()

    def get_portal(self, schoolname: str):
        self.driver.get(f"https://{schoolname}.zportal.nl")

    def login_portal(self, username: str, password: str, single_sign_on: bool):
        username_input = None
        password_input = None
        login_button = None
        if single_sign_on == False:
            username_input = self.driver.find_element_by_id("username")
            password_input = self.driver.find_element_by_id("password")
            login_button = self.driver.find_elements(
                By.XPATH, "/html/body/div/div/form/input[9]")
        else:
            self.driver.find_element(
                By.XPATH, "/html/body/div/div/div/a").click()
            username_input = self.driver.find_element_by_id("UserName")
            password_input = self.driver.find_element_by_id("Password")
            login_button = self.driver.find_element_by_name("login")

        username_input.send_keys(username)
        password_input.send_keys(password)
        login_button.click()

    def get_token(self) -> str:
        # Click on the portal button
        self.driver.find_element_by_id("choicePortal").click()

        # Click "Koppelingen"
        # This can take a long time, use a proper wait, wait maximum 30 seconds before throwing an error
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="isc_H"]'))).click()

        # Click "Koppel externe applicatie"
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="isc_7F"]'))).click()

        # Get the token
        token = self.driver.find_element(
            By.XPATH, '//*[@id="isc_88"]/table/tbody/tr/td').text
        if "laden" in token:
            # Token isn't loaded yet, sleep 2 seconds
            sleep(2)
            # Get the token again
            token = self.driver.find_element(
                By.XPATH, '//*[@id="isc_88"]/table/tbody/tr/td').text

        return token

    def close(self):
        self.driver.quit()
