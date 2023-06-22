"""
Arquivo de configuração do job.

Este arquivo contém as configurações para execução do job de extração de dados.

- "default": Configurações padrão do job.
    - "name": Nome do job.
    - "domain": Domínio do site.
    - "index": Configurações do índice do site.

- "sets": Conjuntos de configurações do job.
    - "id": Identificador do conjunto.
    - "subject": Assunto do conjunto.
    - "href": URL de onde os dados serão extraídos.

- "bulkload": Configurações do carregamento em massa.
    - "file-format": Formato do arquivo utilizado para o carregamento em massa (json).

"""

import os
import json

job_name = "talks"
pwd =  os.getcwd()
local = f"{pwd}/project/jobs/{job_name}/"
with open(f"{local}/mapping.json", "r") as f:
    mapping = json.load(f)
        
JOB_CONFIG = {
    "sys": {
        "local": local
    },
    "default": {
        "name": job_name,
    },
    "bulkload": {
        "elastic": {
            "file-format": "json",
            "mapping": mapping
        },
        "postgres": {}
    }
}
