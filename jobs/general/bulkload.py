import time
import json
import importlib

from shared.elastic import Elastic

class BulkLoad():
    def __init__(self, env_config: dict) -> None:
        """
        Inicializa a classe BulkLoad.
        :param env_config: Um dicionário contendo as configurações do ambiente.
        """
        uri = env_config["uri"]
        job_name = env_config["job_name"]

        self.file_path = f"{uri}/{job_name}"

        self.es = Elastic(env_config)

        job_confg_path = f"jobs.{job_name}.config"
        self.job_config = importlib.import_module(job_confg_path).JOB_CONFIG

    def run(self) -> None:
        """
        Executa o processo de carga em massa.
        Chama a função específica para o formato de arquivo configurado no job.
        """
        file_format = self.job_config["bulkload"]['file-format']

        save_options = {
            "json": self.load_json_to_elasticsearch
        }

        save_data = save_options.get(file_format)
        save_data()

    def load_json_to_elasticsearch(self) -> None:
        """
        Carrega um arquivo JSON no Elasticsearch.
        O arquivo é lido e os documentos são indexados em massa no Elasticsearch.
        """
        file_path = f"{self.file_path}.json"

        with open(file_path, "r") as file:
            data = json.load(file)
            
            self.es.bulkload(data.values())

def run(env_config: dict) -> None:
    start_time = time.time()

    if (env_config["env"] in ["dev", "exp"]):
        bulkload = BulkLoad(env_config)
        bulkload.run()
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
