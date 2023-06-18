import os
import json
import pandas

class FileSystem():
    def __init__(self, env_config: dict) -> None:
        """
        Inicializa a classe FileSystem.
        :param env_config: Dicionario contendo as configuracoes do ambiente.
        """
        uri = env_config["uri"]
        job_name = env_config["job_name"]

        self.sys_path = f"{uri}/data-pipeline"
        self.file_path = f"{self.sys_path}/{job_name}"

    def save(self, data: dict, type_file: str, file_name: str=None) -> None:
        """
        Salva os dados em um arquivo.
        :param data: Os dados a serem salvos.
        :param type_file: O tipo de arquivo (ex: "json").
        """
        if (file_name):
            self.file_path = f"{self.sys_path}/{file_name}"

        choices = {
            "json": self._save_json,
        }
        
        choices.get(type_file)(data)

    def _save_json(self, data: dict) -> None:
        """
        Salva os dados em um arquivo JSON.
        :param data: Os dados a serem salvos.
        """
        file_path = f"{self.file_path}.json"

        if not os.path.exists(file_path):
            with open(file_path, "w") as file:
                file.write(json.dumps({}))

        with open(file_path, "r") as f:
            json_data = json.load(f)
        
        duplicate = any(data["id"] == id for id in json_data.keys())
        if not duplicate:
            json_data[data["id"]] = data

            with open(file_path, "w") as file:
                json.dump(json_data, file, ensure_ascii=False)

    def read_file(self, type_file: str, file_name: str=None) -> dict:
        """
        Lê o conteúdo de um arquivo relacionado index do job.
        :param type_file: O tipo de arquivo a ser lido.
        :param file_name: O nome de arquivo a ser lido.
        :return: O conteúdo do arquivo lido.
        """

        if (file_name):
            self.file_path = f"{self.sys_path}/{file_name}"

        choices = {
            "json": self._read_json,
            "csv": self._read_with_pandas
        }
        
        data = choices.get(type_file)()

        return data

    def _read_with_pandas(self) -> object:
        """
        Lê o conteúdo de um arquivo CSV com o pandas.
        :return: O conteúdo do arquivo CSV lido.
        """
        df = pandas.read_csv(f"{self.file_path}.csv")

        return df

    def _read_json(self) -> dict:
        """
        Lê o conteúdo de um arquivo JSON.
        :return: O conteúdo do arquivo JSON lido.
        """
        file_path = f"{self.file_path}.json"

        with open(file_path, "r") as f:
            json_data = json.load(f)
        
        return json_data