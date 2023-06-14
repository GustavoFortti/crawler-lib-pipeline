import os
import json

class FileSystem():
    def __init__(self, config_env: dict) -> None:
        uri = config_env["uri"]
        name = config_env["job_name"]

        self.data_path = f"{uri}/{name}"

    def save(self, data: dict, type_file: str) -> None:
        
        choices = {
            "json": self.save_json,
        }
        
        choices.get(type_file)(data)

    def save_json(self, data: dict) -> None:
        data_path = f"{self.data_path}.json"

        if not os.path.exists(data_path):
            with open(data_path, "w") as arquivo:
                arquivo.write(json.dumps({}))

        with open(data_path, "r") as f:
            json_data = json.load(f)
        
        duplicate = any(data["id"] == id for id in json_data.keys())
        if not duplicate:
            json_data[data["id"]] = data

            with open(data_path, "w") as arquivo:
                json.dump(json_data, arquivo, ensure_ascii=False)