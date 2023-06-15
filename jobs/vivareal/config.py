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

JOB_CONFIG = {
    "default": {
        "name": "vivareal",
        "domain": "https://www.vivareal.com.br",
        "index": {"key": "__index__", "range": []}
    },
    "sets": [{
        "id": 1,
        "subject": "venda-sp-sorocaba",
        "href": "/venda/sp/sorocaba/#onde=Brasil,S%C3%A3o%20Paulo,sorocaba,,,,,,BR%3ESao%20Paulo%3ENULL%3Esorocaba,,,&tipos=apartamento_residencial,casa_residencial",
    }],
    "bulkload": {
        "file-format": "json"
    }
}