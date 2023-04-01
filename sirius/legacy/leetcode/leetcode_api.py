from cmath import e
from typing import Tuple
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import visibility_of_element_located as visible
from selenium.webdriver.support.expected_conditions import element_to_be_clickable as clickable
from selenium.webdriver.support.expected_conditions import invisibility_of_element_located as invisible
from typing import Union
import os
import asyncio

class LeetCode:

    URL = "https://leetcode.com/accounts/login/"
    USERNAME_LOC = "//input[@id='id_login']"
    PASSWORD_LOC = "//input[@id='id_password']"
    LOGIN_LOC = "//button[@id='signin_btn']"
    PROBLEM_SET_LOC = "//div/a[contains(text(), 'Problems')]"
    QUESTION_LOC = "//*[@id='__next']/div/div/div[1]/div[1]/div[6]/div[2]/div/div/div[2]/div[1]/div[2]/div/div/div/div/a"
    LOADING_LOC = "//div[@id='initial-loading']"


    def __init__(self, username: Union[None, str], password: Union[None, str]) -> None:
        self.username = username
        self.password = password
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.screenshot_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/screenshot/image.png'


    async def get_question(self) -> Union[Tuple[str, str], Tuple[None, None]]:
        """
        Get Question from Leetcode and return screenshot path and url

        :return: screenshot path, question url
        """
        try:
            # Initialize driver
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.set_window_size(width=1920, height=1080)
            driver.maximize_window()
            wait = WebDriverWait(driver, 10)
            driver.get(self.URL)
            await asyncio.sleep(1)
            # Login
            wait.until(invisible(("xpath", self.LOADING_LOC)))
            username_element: WebElement = wait.until(visible(("xpath", self.USERNAME_LOC)))
            password_element: WebElement = wait.until(visible(("xpath", self.PASSWORD_LOC)))
            login_element: WebElement = wait.until(visible(("xpath", self.LOGIN_LOC)))
            wait.until(invisible(("xpath", self.LOADING_LOC)))
            username_element.send_keys(self.username)
            password_element.send_keys(self.password)
            login_element.click()
            await asyncio.sleep(3)
            # Get Question
            wait.until(invisible(("xpath", self.LOADING_LOC)))
            problem_element: WebElement = wait.until(clickable(("xpath", self.PROBLEM_SET_LOC)))
            problem_element.click()
            questioin_element: WebElement = wait.until(clickable(("xpath", self.QUESTION_LOC)))
            wait.until(invisible(("xpath", self.LOADING_LOC)))
            questioin_element.click()
            await asyncio.sleep(3)
            # Screenshot
            wait.until(invisible(("xpath", self.LOADING_LOC)))
            driver.get_screenshot_as_file(self.screenshot_path)
            url = driver.current_url
            driver.quit()
            return (self.screenshot_path, url)
        except:
            driver.quit()
            return (None, None)

    def clean(self):
        os.remove(self.screenshot_path)
