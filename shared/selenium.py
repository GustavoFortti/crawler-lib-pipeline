import time
import logging

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup

class Selenium():
    def __init__(self, driver_type: str, driver_path: str, headless: bool=False) -> None:
        """
        Inicializa a classe Selenium.
        :param driver_type: O tipo de driver a ser utilizado ("chrome" ou "firefox").
        :param driver_path: O caminho para o arquivo do driver.
        """
        if (driver_type == "chrome"):
            chromedriver_path = driver_path
            opcoes = webdriver.ChromeOptions()
            if (headless): opcoes.add_argument('--headless')
            self.driver = webdriver.Chrome(executable_path=chromedriver_path, options=opcoes)
        elif (driver_type == "firefox"):
            firefox_options = Options()
            # firefox_options.add_argument("--headless")
            self.driver = webdriver.Firefox(options=firefox_options)
        else:
            self.driver = None

        self.logger = logging.getLogger(__name__)

    def get_html(self, url: str) -> object:
        """
        Obtém o HTML de uma pagina.
        :param url: A URL da pagina.
        :return: O objeto BeautifulSoup contendo o HTML da pagina.
        """
        print(f"GET URL: {url}")

        soup = None
        html = None
        try:
            with self.driver as driver:
                driver.get(url)

                time.sleep(1)

                WebDriverWait(driver, 20)
                # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.property-card__labels-container')))
                html = driver.page_source

                if (html):
                    soup = BeautifulSoup(html, 'html.parser')
                    print("SUCCESS")
                else:
                    print("Failed to retrieve HTML content from the page")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

        return soup

    def quit(self) -> None:
        """
        Encerra a instância do driver.
        """
        self.driver.quit()