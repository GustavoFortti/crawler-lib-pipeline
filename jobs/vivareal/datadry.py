import time
import re
import json
from copy import deepcopy

from shared.filesystem import FileSystem
from shared.location import FindLocation
from shared.cryptography import create_hash_sha256, encode_url_base64
from utils.dry_string import remove_special_characters

from jobs.vivareal.config import JOB_CONFIG

class DataDry():
    def __init__(self, env_config: dict) -> None:
        """
        Inicializa a classe DataDry.
        :param env_config: A configuração do ambiente.
        """
        self.env_config = env_config

        self.name = JOB_CONFIG['default']["name"]
        self.fs = FileSystem(env_config)

    def dry(self):
        """
        Realiza o processo de limpeza dos dados.
        """
        documents = self.fs.read_file(JOB_CONFIG['bulkload']["file-format"])
        for document in documents.values():
            document = self.restructure_data(document)
            document = self.set_location_for_data(document)
            document["hash"] = create_hash_sha256(str(document))

            self.fs.save(document, "json", f"{self.name}_dry")

    def set_location_for_data(self, document: dict) -> dict:
        """
        Define a localização para cada entrada de dados.
        :param document: O dicionário de dados.
        :return: O dicionário de dados atualizado.
        """
        document = deepcopy(document)
        endereco = document["imovel"]["endereco"]
    
        matches = re.findall(r"^(.*?),?\s*(\d+)?\s*[-,]?\s*([\w\s]+)?,?\s*(\w+)?\s*[-,]?\s*(\w+)?$", endereco)
        
        numero = matches[0][1].strip() if matches[0][1] else None
        rua = matches[0][0].strip() if matches[0][0] else None
        bairro = matches[0][2].strip() if matches[0][2] else None
        cidade = matches[0][3].strip() if matches[0][3] else None
        estado = matches[0][4].strip() if matches[0][4] else None

        address = {
            "street": rua,
            "neighborhood": bairro,
            "city": cidade,
            "state": estado,
        }

        fl = FindLocation(self.env_config)
        fl.set_address(address)

        cep, has_precision = fl.get_cep()
        latitude, longitude = fl.get_latitude_longitude(cep)

        document["imovel"]["endereco"] = {}
        document["imovel"]["endereco"]["cep"] = cep
        document["imovel"]["endereco"]["numero"] = numero
        document["imovel"]["endereco"]["latitude"] = latitude
        document["imovel"]["endereco"]["longitude"] = longitude
        document["imovel"]["endereco"]["has_precision"] = has_precision

        return document

    def restructure_data(self, document: dict) -> dict:
        """
        Restrutura o dicionário de dados para um formato desejado.
        :param document: O dicionário de dados.
        :return: O dicionário de dados reestruturado.
        """
        document = deepcopy(document)
        del document['image_urls']
        del document['url']

        document["imovel"] = {}
        document["imovel"]["caracteristicas"] = {}

        # Move a endereco para imóvel
        document["imovel"]["endereco"] = document["endereco"]
        del document['endereco']

        # Extrair a área do imóvel
        pattern_area = r"(\d+)(\D+)"
        match = re.match(pattern_area, document['area'])
        document["imovel"]["area"] = str(match.group(1)) if match else None
        document["imovel"]["unidade"] = "metros quadrados" if match else None
        del document['area']

        # Extrair o preço do imóvel
        pattern_preco = r"R\$\s*(\d[\d.,]*)"
        match = re.search(pattern_preco, document['preco'])
        document["imovel"]["preco"] = str(match.group(1)) if match else None
        document["imovel"]["moeda"] = "BRL" if match else None
        del document['preco']

        # Mover valores de 'valor_condominio' e 'valor_iptu' para dentro de 'imovel'
        document["imovel"]["valor_condominio"] = document['valor_condominio']
        document["imovel"]["valor_iptu"] = document['valor_iptu']
        del document['valor_condominio']
        del document['valor_iptu']

        # Extrair o número de quartos do imóvel
        pattern_quartos = r"(\d+)"
        match = re.search(pattern_quartos, document['quartos'])
        document["imovel"]["caracteristicas"]["quartos"] = int(match.group(1)) if match else None
        del document['quartos']

        # Extrair o número de banheiros do imóvel
        pattern_banheiros = r"(\d+)\s*(?:banheiro|banheiros)"
        match = re.search(pattern_banheiros, document["banheiros"])
        document["imovel"]["caracteristicas"]["banheiros"] = int(match.group(1)) if match else None

        # Extrair o número de suítes do imóvel
        pattern_suites = r"(\d+)\s*(?:suíte|suítes)"
        match = re.search(pattern_suites, document["banheiros"])
        document["imovel"]["caracteristicas"]["suites"] = int(match.group(1)) if match else None
        del document['banheiros']

        # Extrair o número de vagas de garagem do imóvel
        pattern_vagas = r"(\d+)"
        match = re.search(pattern_vagas, document["vagas"])
        document["imovel"]["caracteristicas"]["vagas"] =  int(match.group(1)) if match else None
        del document['vagas']

        # Mover valores de 'caracteristicas_adicionais' para dentro de 'caracteristicas'
        document["imovel"]["caracteristicas"]["caracteristicas_adicionais"] = document["caracteristicas_adicionais"]
        del document['caracteristicas_adicionais']

        return document

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
