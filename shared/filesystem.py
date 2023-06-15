import os
import json

class FileSystem():
    def __init__(self, env_config: dict) -> None:
        """
        Inicializa a classe FileSystem.
        :param env_config: Dicionario contendo as configuracoes do ambiente.
        """
        uri = env_config["uri"]
        job_name = env_config["job_name"]

        self.file_path = f"{uri}/{job_name}"

    def save(self, data: dict, type_file: str) -> None:
        """
        Salva os dados em um arquivo.
        :param data: Os dados a serem salvos.
        :param type_file: O tipo de arquivo (ex: "json").
        """
        choices = {
            "json": self.save_json,
        }
        
        choices.get(type_file)(data)

    def save_json(self, data: dict) -> None:
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