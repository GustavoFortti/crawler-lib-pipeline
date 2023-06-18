import time
import re
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

        self.index = JOB_CONFIG['default']["name"]
        self.fs = FileSystem(env_config)

    def dry(self):
        """
        Realiza o processo de limpeza dos dados.
        """
        documents = self.fs.read_file(JOB_CONFIG['bulkload']["file-format"])
        documents = self.restructure_data(documents)
        documents = self.set_location_for_data(documents)

        # print(json.dumps(documents, indent=4, ensure_ascii=False))
        # hash = create_hash_sha256(str(item_page))
        # item_page["hash"] = hash

    def set_location_for_data(self, data: dict) -> dict:
        """
        Define a localização para cada entrada de dados.
        :param data: O dicionário de dados.
        :return: O dicionário de dados atualizado.
        """
        data = deepcopy(data)
        for key in data.keys():
            row = data[key]

            endereco = row["imovel"]["endereco"]
        
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

            cep = fl.get_cep()
            latitude, longitude = fl.get_latitude_longitude(cep)

            row["imovel"]["endereco"] = {}
            row["imovel"]["endereco"]["cep"] = cep
            row["imovel"]["endereco"]["numero"] = numero
            row["imovel"]["endereco"]["latitude"] = latitude
            row["imovel"]["endereco"]["longitude"] = longitude

        return data

    def restructure_data(self, data: dict) -> dict:
        """
        Restrutura o dicionário de dados para um formato desejado.
        :param data: O dicionário de dados.
        :return: O dicionário de dados reestruturado.
        """
        data = deepcopy(data)
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
