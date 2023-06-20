import time
import re
import json
from copy import deepcopy

from shared.filesystem import FileSystem
from shared.location import FindLocation
from shared.cryptography import create_hash_sha256

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

        properties = JOB_CONFIG["bulkload"]["mapping"]['mappings']['properties']
        self.empty_document = self._generate_empty_document(properties)
        
    def start(self):
        """
        Realiza o processo de limpeza dos dados.
        """
        documents = self.fs.read_file(JOB_CONFIG['bulkload']["file-format"])
        for document in documents.values():
            new_document = deepcopy(self.empty_document)
            new_document = self._restructure_data(document, new_document)
            new_document = self._set_location(document, new_document)
            new_document["hash"] = create_hash_sha256(str(new_document))

            self.fs.save(new_document, "json", f"{self.name}_dry")

    def _set_location(self, document: dict, new_document: dict) -> dict:
        """
        Define a localização (cep. numero. latitude e longitude) do imovel.
        :param document: O dicionário de dados.
        :return: O dicionário de dados atualizado.
        """
        endereco = document["endereco"]
    
        matches = re.findall(r"^(.*?),?\s*(\d+)?\s*[-,]?\s*([\w\s]+)?,?\s*(\w+)?\s*[-,]?\s*(\w+)?$", endereco)
        
        rua = matches[0][0].strip() if matches[0][0] else None
        numero = matches[0][1].strip() if matches[0][1] else None
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

        new_document["imovel"]["endereco"]["cep"] = cep
        new_document["imovel"]["endereco"]["numero"] = numero
        new_document["imovel"]["endereco"]["location"] = {}
        new_document["imovel"]["endereco"]["location"]["lat"] = latitude
        new_document["imovel"]["endereco"]["location"]["lon"] = longitude
        new_document["imovel"]["endereco"]["has_precision"] = has_precision

        return new_document

    def _restructure_data(self, document: dict, new_document: dict) -> dict:
        """
        Restrutura o dicionário de dados para um formato desejado.
        :param document: O dicionário de dados.
        :return: O dicionário de dados reestruturado.
        """
        new_document = deepcopy(new_document)
        
        new_document["titulo"] = document["titulo"]
        new_document["codigo"] = document["codigo"]
        new_document["descricao"] = document["descricao"]
        new_document["id"] = document["id"]

        # Extrair a área do imóvel
        pattern_area = r"(\d+)(\D+)"
        match = re.match(pattern_area, document['area'])
        new_document["imovel"]["area"] = str(match.group(1)) if match else None
        new_document["imovel"]["unidade"] = "metros quadrados" if match else None

        # Extrair o preço do imóvel
        pattern_preco = r"R\$\s*(\d[\d.,]*)"
        match = re.search(pattern_preco, document['preco'])
        new_document["imovel"]["preco"] = str(match.group(1)) if match else None
        new_document["imovel"]["moeda"] = "BRL" if match else None

        # Mover valores de 'valor_condominio' e 'valor_iptu' para dentro de 'imovel'
        new_document["imovel"]["valor_condominio"] = document['valor_condominio']
        new_document["imovel"]["valor_iptu"] = document['valor_iptu']

        # Extrair o número de quartos do imóvel
        pattern_quartos = r"(\d+)"
        match = re.search(pattern_quartos, document['quartos'])
        new_document["imovel"]["caracteristicas"]["quartos"] = int(match.group(1)) if match else None

        # Extrair o número de banheiros do imóvel
        pattern_banheiros = r"(\d+)\s*(?:banheiro|banheiros)"
        match = re.search(pattern_banheiros, document["banheiros"])
        new_document["imovel"]["caracteristicas"]["banheiros"] = int(match.group(1)) if match else None

        # Extrair o número de suítes do imóvel
        pattern_suites = r"(\d+)\s*(?:suíte|suítes)"
        match = re.search(pattern_suites, document["banheiros"])
        new_document["imovel"]["caracteristicas"]["suites"] = int(match.group(1)) if match else None

        # Extrair o número de vagas de garagem do imóvel
        pattern_vagas = r"(\d+)"
        match = re.search(pattern_vagas, document["vagas"])
        new_document["imovel"]["caracteristicas"]["vagas"] =  int(match.group(1)) if match else None

        # Mover valores de 'caracteristicas_adicionais' para dentro de 'caracteristicas'
        new_document["imovel"]["caracteristicas"]["caracteristicas_adicionais"] = document["caracteristicas_adicionais"]

        return new_document
    
    def _generate_empty_document(self, properties: dict) -> dict:
        """
        Gera um documento Elasticsearch vazio com base no mapeamento fornecido.
        :param properties: O mapeamento Elasticsearch para o documento.
        :return: O documento Elasticsearch vazio.
        """
        document = {}

        for key in properties:
            value = properties[key]
            if (key == "properties"):
                return self._generate_empty_document(value)
            if (isinstance(value, dict) & (not (list(value.keys())[0] == "type"))):
                document[key] = self._generate_empty_document(value)
            else:
                document[key] = None

        return document

def run(env_config: dict) -> None:
    start_time = time.time()

    if (env_config["env"] in ["dev", "exp"]):
        datadry = DataDry(env_config)
        datadry.start()
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
