import time
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service


from bs4 import BeautifulSoup

class Selenium():
    def __init__(self, driver_type: str, driver_path: str, headless: bool=False) -> None:
        """
        Inicializa a classe Selenium.
        :param driver_type: O tipo de driver a ser utilizado ("chrome" ou "firefox").
        :param driver_path: O caminho para o arquivo do driver.
        """
        if (driver_type == "chrome"):
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--remote-debugging-port=3000')

            service = Service(executable_path=driver_path)

            self.driver = webdriver.Chrome(service=service, options=options)

        elif (driver_type == "firefox"):
            # firefox_options = Options()
            # firefox_options.add_argument("--headless")
            # self.driver = webdriver.Firefox(options=firefox_options)
            pass
        else:
            self.driver = None

        self.logger = logging.getLogger(__name__)

    def run(self):
        time.sleep(1)
        WebDriverWait(self.driver, 20)
        return self.driver

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