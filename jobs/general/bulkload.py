import time
import json
import importlib

from shared.postgress import PostgreSQL
from shared.elastic import Elastic
from shared.filesystem import FileSystem

class BulkLoad():
    def __init__(self, env_config: dict) -> None:
        """
        Inicializa a classe BulkLoad.
        :param env_config: Um dicionário contendo as configurações do ambiente.
        """
        self.job_name = env_config["job_name"]
        job_confg_path = f"jobs.{self.job_name}.config"
        self.job_config = importlib.import_module(job_confg_path).JOB_CONFIG

        self.es = Elastic(env_config, self.job_config)
        # self.ps = PostgreSQL(env_config)
        self.fs = FileSystem(env_config)

    def start(self) -> None:
        """
        Executa o processo de carga em massa.
        Chama a função específica para o formato de arquivo configurado no job.
        """
        file_format = self.job_config["bulkload"]["elastic"]["file-format"]

        save_options = {
            "json": self._load_json_to_elasticsearch
        }

        save_documents = save_options.get(file_format)
        save_documents()

    def _load_json_to_elasticsearch(self) -> None:
        """
        Carrega um arquivo JSON no Elasticsearch.
        O arquivo é lido e os documentos são indexados em massa no Elasticsearch.
        """

        documents = self.fs.read_file(type_file="json", file_name=f"{self.job_name}_dry")
        
        self.es.bulkload(list(documents.values()))

def run(env_config: dict) -> None:
    start_time = time.time()

    if (env_config["env"] in ["dev", "exp"]):
        bulkload = BulkLoad(env_config)
        bulkload.start()
    elif (env_config["env"] in ["prd"]):
        prd(env_config)
    else:
        print("Definir ambiente de execucao")
        
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Tempo de execucao: {execution_time} segundos")

def prd(env_config: dict) -> None:
    try:
        BulkLoad(env_config)
    except Exception as e:
        print(f"Ocorreu um erro durante a execucao da funcao job: {str(e)}")
