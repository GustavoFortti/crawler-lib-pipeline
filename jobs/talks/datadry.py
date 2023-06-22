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

        # properties = JOB_CONFIG["bulkload"]["elastic"]["mapping"]['mappings']['properties']
        # self.empty_document = self._generate_empty_document(properties)
        
    def start(self):
        """
        Realiza o processo de limpeza dos dados.
        """
        documents = self.fs.read_file(JOB_CONFIG['bulkload']["elastic"]["file-format"])
        for document in documents.values():
            pass

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
