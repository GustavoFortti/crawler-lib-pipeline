import time
import logging

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

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
            firefox_options.add_argument("--headless")
            self.driver = webdriver.Firefox(options=firefox_options)
        else:
            self.driver = None

        self.logger = logging.getLogger(__name__)

    def get_html(self, url: str) -> object:
        self.logger.info(f"GET URL: {url}")

        html = None
        with self.driver as driver:
            driver.get(url)
            try:
                wait = WebDriverWait(driver, 10)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.property-card__labels-container')))
                html = driver.page_source
                if html is not None:
                    soup = BeautifulSoup(html, 'html.parser')
                    self.logger.info("SUCCESS")
                else:
                    self.logger.error("Failed to retrieve HTML content from the page")
            except TimeoutException:
                self.logger.error("Timeout occurred while waiting for element")
            except Exception as e:
                self.logger.error(f"An error occurred: {str(e)}")

        return soup
    
    def get_url_soup(self, url: str) -> object:
        html = self.get_html(url)
        soup = BeautifulSoup(html, 'html.parser')

        return soup

    def quit(self):
        self.driver.quit()