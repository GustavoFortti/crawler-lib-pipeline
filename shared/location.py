import re
import requests
import time
import statistics
from typing import Tuple

from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from shared.selenium import Selenium
from shared.filesystem import FileSystem
from utils.dry_string import fix_if_string

class FindLocation():
    def __init__(self, env_config: dict) -> None:
        """
        Inicializa a classe FindLocation.
        :param env_config: A configuração do ambiente.
        """
        self.env_config = env_config
        self.driver_type = self.env_config["driver"]
        self.driver_path = self.env_config['driver_path']

        self.fs = FileSystem(env_config)

    def set_address(self, address: dict) -> None:
        """
        Define o endereço a ser pesquisado.
        :param address: O dicionário contendo as informações do endereço.
        """
        self.address = address

    def get_cep(self) -> Tuple[str, bool]:
        """
        Obtém o CEP do endereço.
        :return: O CEP encontrado.
        """
        print("Buscando cep...")
        cep, has_precision  = self.search_cep_by_csv(self.address)

        if (not cep):
            cep, has_precision = self.serach_cep_google()

        return cep, has_precision
    
    def search_cep_by_csv(self, address: dict) -> Tuple[str, bool]:
        """
        Busca o CEP em um arquivo CSV local.
        :param address: O dicionário contendo as informações do endereço.
        :return: O CEP encontrado.
        """
        try:
            self.df = self.fs.read_file(type_file="csv", file_name="cep-sp")

            condition = ((self.df['bairro'].apply(fix_if_string) == fix_if_string(address["neighborhood"])) &
                        (self.df['cidade'].apply(fix_if_string) == fix_if_string(address["city"])) &
                        (self.df['estado'].apply(fix_if_string) == fix_if_string(address["state"])))

            df_cep = self.df.loc[condition]

            if (address["street"]):
                condition = (df_cep['logradouro'].apply(fix_if_string) == fix_if_string(address["street"]))
                df_cep = df_cep.loc[condition]

            cep = df_cep["cep"].values

            len_cep = len(cep)
            if (len_cep > 1):
                median = int(len_cep / 2)
                return str(cep[median]), False 
            else:
                return str(cep[0]), True
        except:
            return None

    def serach_cep_google(self) -> int:
        """
        Realiza a busca do CEP pelo Google.
        :return: O CEP encontrado.
        """
        return None, None
    
    def get_latitude_longitude(self, cep: str) -> Tuple[str, str]:
        """
        Obtém a latitude e longitude do CEP fornecido.
        :param cep: O CEP.
        :return: A latitude e longitude.
        """
        latitude, longitude = self.search_latitude_longitude_by_qualocep(cep)
        return latitude, longitude

    def search_latitude_longitude_by_qualocep(self, cep: str) -> Tuple[str, str]:
        """
        Realiza a busca da latitude e longitude pelo site QualoCep.
        :param cep: O CEP.
        :return: A latitude e longitude encontradas.
        """
        print("Buscando localização...")
        driver = Selenium(self.driver_type, self.driver_path, True)

        url = f"https://www.qualocep.com/busca-cep/{cep}"
        soup = driver.get_html(url)
        texto = soup.find('h4').text

        pattern = r'Latitude:\s*([-+]?\d+\.\d+)\s*/\s*Longitude:\s*([-+]?\d+\.\d+)'
        matches = re.search(pattern, texto)
        latitude = str(matches.group(1))
        longitude = str(matches.group(2))

        return latitude, longitude

    def get_nearest_():
        pass