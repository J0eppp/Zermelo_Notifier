from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


class Browser:
    def __init__(self):
        # self.driver = webdriver.Firefox(
        #     firefox_binary=FirefoxBinary("./geckodriver"))
        self.driver = webdriver.Chrome()
