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
        "file-format": "json",
        "mapping": {
            "mappings": {
                "properties": {
                    "titulo": { "type": "text" },
                    "codigo": { "type": "keyword" },
                    "descricao": { "type": "text" },
                    "id": { "type": "keyword" },
                    "imovel": {
                        "properties": {
                            "caracteristicas": {
                                "properties": {
                                    "quartos": { "type": "text" },
                                    "banheiros": { "type": "text" },
                                    "suites": { "type": "text" },
                                    "vagas": { "type": "text" },
                                    "caracteristicas_adicionais": { "type": "keyword" }
                                }
                            },
                            "endereco": {
                                "properties": {
                                    "cep": { "type": "keyword" },
                                    "numero": { "type": "keyword" },
                                    "location": { "type": "geo_point" },
                                    "has_precision": { "type": "boolean" }
                                }
                            },
                            "area": { "type": "text" },
                            "unidade": { "type": "keyword" },
                            "preco": { "type": "text" },
                            "moeda": { "type": "keyword" },
                            "valor_condominio": { "type": "text" },
                            "valor_iptu": { "type": "text" }
                        }
                    },
                    "hash": { "type": "keyword" }
                }
            },
            "settings": {
                "analysis": {
                    "analyzer": {
                        "my_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "my_stemmer"
                        ]
                        }
                    },
                    "filter": {
                        "my_stemmer": {
                            "type": "stemmer",
                            "name": "portuguese"
                        }
                    }
                }
            }
        }
    }
}