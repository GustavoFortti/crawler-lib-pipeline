import time
import logging

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

class Selenium():
    def __init__(self, driver_type, driver_path) -> None:
        
        if (driver_type == "chrome"):
            caminho_chromedriver = driver_path
            opcoes = webdriver.ChromeOptions()
            # opcoes.add_argument('--headless')
            self.driver = webdriver.Chrome(executable_path=caminho_chromedriver, options=opcoes)
        elif (driver_type == "firefox"):
            firefox_options = Options()
            # firefox_options.add_argument("--headless")
            self.driver = webdriver.Firefox(options=firefox_options)
        else:
            self.driver = None

        self.logger = logging.getLogger(__name__)

    def get_html(self, url: str) -> object:
        print(f"GET URL: {url}")

        soup = None
        html = None
        with self.driver as driver:
            driver.get(url)

            time.sleep(2)

            try:
                wait = WebDriverWait(driver, 20)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.property-card__labels-container')))
                html = driver.page_source

                if (html):
                    soup = BeautifulSoup(html, 'html.parser')
                    print("SUCCESS")
                else:
                    print("Failed to retrieve HTML content from the page")
            except Exception as e:
                print(f"An error occurred: {str(e)}")

        return soup
    
    def get_url_soup(self, url: str) -> object:
        html = self.get_html(url)
        soup = BeautifulSoup(html, 'html.parser')

        return soup

    def quit(self):
        self.driver.quit()