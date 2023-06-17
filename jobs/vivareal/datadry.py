import time
import re
import json
import requests
import unidecode
from copy import deepcopy

from shared.selenium import Selenium
from shared.filesystem import FileSystem
from shared.cryptography import create_hash_sha256, encode_url_base64
from utils.dry_string import remove_special_characters
from fake_useragent import UserAgent

from shared.location import get_info_address

from jobs.vivareal.config import JOB_CONFIG

class DataDry():
    def __init__(self, env_config: dict) -> None:
        self.env_config = env_config
        self.driver_type = self.env_config["driver"]
        self.driver_path = self.env_config['driver_path']

        self.index = JOB_CONFIG['default']["name"]

        self.fs = FileSystem(env_config)

    def dry(self):
        
        documents = self.fs.read_to_dry(JOB_CONFIG['bulkload']["file-format"])
        documents = self.restructure_data(documents)

        # print(json.dumps(documents, indent=4, ensure_ascii=False))


        [print(self.set_location(documents[key]["imovel"]["endereco"])) for key in documents]
        # data = self.set_location(documents[key]["imovel"]["endereco"]))

        # hash = create_hash_sha256(str(item_page))
        # item_page["hash"] = hash

    def restructure_data(self, data: dict) -> dict:
        for key in data.keys():
            row = data[key]

            del row['image_urls']
            del row['url']

            row["imovel"] = {}
            row["imovel"]["caracteristicas"] = {}

            # Move a endereco para imóvel
            row["imovel"]["endereco"] = row["endereco"]
            del row['endereco']

            # Extrair a área do imóvel
            pattern_area = r"(\d+)(\D+)"
            match = re.match(pattern_area, row['area'])
            row["imovel"]["area"] = str(match.group(1)) if match else None
            row["imovel"]["unidade"] = "metros quadrados" if match else None
            del row['area']

            # Extrair o preço do imóvel
            pattern_preco = r"R\$\s*(\d[\d.,]*)"
            match = re.search(pattern_preco, row['preco'])
            row["imovel"]["preco"] = str(match.group(1)) if match else None
            row["imovel"]["moeda"] = "BRL" if match else None
            del row['preco']

            # Mover valores de 'valor_condominio' e 'valor_iptu' para dentro de 'imovel'
            row["imovel"]["valor_condominio"] = row['valor_condominio']
            row["imovel"]["valor_iptu"] = row['valor_iptu']
            del row['valor_condominio']
            del row['valor_iptu']

            # Extrair o número de quartos do imóvel
            pattern_quartos = r"(\d+)"
            match = re.search(pattern_quartos, row['quartos'])
            row["imovel"]["caracteristicas"]["quartos"] = int(match.group(1)) if match else None
            del row['quartos']

            # Extrair o número de banheiros do imóvel
            pattern_banheiros = r"(\d+)\s*(?:banheiro|banheiros)"
            match = re.search(pattern_banheiros, row["banheiros"])
            row["imovel"]["caracteristicas"]["banheiros"] = int(match.group(1)) if match else None

            # Extrair o número de suítes do imóvel
            pattern_suites = r"(\d+)\s*(?:suíte|suítes)"
            match = re.search(pattern_suites, row["banheiros"])
            row["imovel"]["caracteristicas"]["suites"] = int(match.group(1)) if match else None
            del row['banheiros']

            # Extrair o número de vagas de garagem do imóvel
            pattern_vagas = r"(\d+)"
            match = re.search(pattern_vagas, row["vagas"])
            row["imovel"]["caracteristicas"]["vagas"] =  int(match.group(1)) if match else None
            del row['vagas']

            # Mover valores de 'caracteristicas_adicionais' para dentro de 'caracteristicas'
            row["imovel"]["caracteristicas"]["caracteristicas_adicionais"] = row["caracteristicas_adicionais"]
            del row['caracteristicas_adicionais']

        return data
        
    def set_location(self, endereco: dict):
        latitude, longitude, cep, numero = get_info_address(endereco)

        return latitude, longitude, cep, numero

def run(env_config: dict) -> None:
    start_time = time.time()

    if (env_config["env"] in ["dev", "exp"]):
        datadry = DataDry(env_config)
        datadry.dry()
    elif (env_config["env"] in ["prd"]):
        prd(env_config)
    else:
        print("Definir ambiente de execucao")
        
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Tempo de execucao: {execution_time} segundos")

def prd(env_config: dict) -> None:
    try:
        DataDry(env_config)
    except Exception as e:
        print(f"Ocorreu um erro durante a execucao da funcao job: {str(e)}")
