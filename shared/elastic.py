import os
from typing import Any, Dict, Union, List

from datetime import datetime
from elasticsearch import Elasticsearch, helpers

class Elastic():
    def __init__(self, env_config) -> None:
        """
        Inicializa a classe Elastic.
        Recupera as configurações de conexão com o Elasticsearch a partir de variáveis de ambiente.
        """
        job_name = env_config["job_name"]
        self.index_name = job_name

        self.host = os.getenv('ELASTIC_HOST')
        self.port = os.getenv('ELASTIC_PORT')
        self.username = os.getenv('ELASTIC_USER')
        self.password = os.getenv('ELASTIC_PASS')

        self.connection = None

        self.connect()

    def connect(self):
        try:
            self.es = Elasticsearch(
                hosts=[{'host': self.host, 'port': self.port}],
                http_auth=(self.username, self.password),
                scheme='https',
                verify_certs=False
            )
            self.test_connection()
        except (Exception) as e:
            print(f"Error ao conectar com Elasticsearch: {e}")

    def test_connection(self):
        """
        Testa a conexão com o Elasticsearch.
        Retorna True se a conexão for bem-sucedida, False caso contrário.
        """
        try:
            self.connection = self.es.ping()
            if (self.connection):
                print("Conctado ao Elasticsearch")
        except Exception as e:
            print(f"Erro ao testar a conexão com o Elasticsearch: {str(e)}")
            return False

    def create_document(self, document: dict) -> dict:
        """
        Cria um documento no Elasticsearch.
        :param index: O nome do indice.
        :param document: O documento a ser criado.
        :return: O resultado da operacao de criacao.
        """
        resultado = self.es.index(index=self.index_name, body=document)
        return resultado

    def update_document(self, id: str, updates: dict) -> dict:
        """
        Atualiza um documento existente no Elasticsearch.
        :param index: O nome do indice.
        :param id: O ID do documento.
        :param updates: As atualizacoes a serem aplicadas ao documento.
        :return: O resultado da operacao de atualizacao.
        """
        resultado = self.es.update(index=self.index_name, id=id, body={"doc": updates})
        return resultado

    def delete_document(self, id: str) -> dict:
        """
        Exclui um documento existente no Elasticsearch.
        :param index: O nome do indice.
        :param id: O ID do documento.
        :return: O resultado da operacao de exclusao.
        """
        resultado = self.es.delete(index=self.index_name, id=id)
        return resultado

    def check_existing_document(self, id: str) -> bool:
        """
        Verifica se o documento ja existe no Elasticsearch.
        :param index: O nome do indice.
        :param id: O ID do documento.
        :return: True se o documento existir, False caso contrario.
        """
        resultado = self.es.exists(index=self.index_name, id=id)
        return resultado
    
    def bulkload(self, documents):
        """
        Realiza o carregamento em massa de documentos no Elasticsearch.
        :param documents: Uma lista de documentos a serem indexados.
        """
        actions = [
            {
                "_index": self.index_name,
                "_source": document
            }
            for document in documents
        ]

        success, _ = helpers.bulk(self.es, actions)
        len_docs = len(documents)
        
        if success == len_docs:
            print("Carregamento de documentos concluído com sucesso")
        else:
            failed = len_docs - success
            print(f"Erro ao carregar documentos: {failed} documentos falharam")

    def find_all(self):
        search_query = {
            "query": {
                "match_all": {}
            }
        }

        # Execute the search request
        response = self.es.search(index=self.index_name, body=search_query)

        total_documents = response['hits']['total']['value']
        print(f"Total documents found: {total_documents}")

        # Check if any documents were found
        if total_documents > 0:
            # Extract the documents from the response
            documents = [hit['_source'] for hit in response['hits']['hits']]

            # Print the found documents
            for document in documents:
                print(document)
        else:
            print("No documents found in the index.")


    from typing import Any, Dict, Union

    def generate_empty_document(self, mapping: Dict[str, Union[str, Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Gera um documento Elasticsearch vazio com base no mapeamento fornecido.
        :param mapping: O mapeamento Elasticsearch para o documento.
        :return: O documento Elasticsearch vazio.
        """
        document = {}

        for field, field_type in mapping.items():
            if field_type == "object":
                document[field] = self.generate_empty_document(mapping[field]["properties"])
            elif field_type == "nested":
                document[field] = []
            elif field_type == "integer":
                document[field] = None
            elif field_type == "double":
                document[field] = None
            elif field_type in ["keyword", "text"]:
                document[field] = ""
            elif field_type == "boolean":
                document[field] = False
            elif field_type == "geo_point":
                document[field] = {"lat": "", "lon": ""}
            else:
                document[field] = None

        return document

    def fill_document(self, mapping: Dict[str, Union[str, Dict[str, Any]]], values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera um documento Elasticsearch vazio com base no mapeamento fornecido.
        :param mapping: O mapeamento Elasticsearch para o documento.
        :return: O documento Elasticsearch vazio.
        """
        document = {}

        for field, field_type in mapping.items():
            value = values.get(field)
            
            if field_type == "object":
                document[field] = self.fill_document(mapping[field]["properties"], value) if value else {}
            elif field_type == "nested":
                document[field] = [self.fill_document(mapping[field]["properties"], item) for item in value] if value else []
            elif field_type == "integer":
                document[field] = int(value) if isinstance(value, int) else None
            elif field_type == "double":
                document[field] = float(value) if isinstance(value, (int, float)) else None
            elif field_type in ["keyword", "text"]:
                document[field] = str(value) if isinstance(value, str) else ""
            elif field_type == "boolean":
                document[field] = bool(value) if isinstance(value, bool) else False
            elif field_type == "geo_point":
                if isinstance(value, dict) and "lat" in value and "lon" in value:
                    document[field] = {"lat": str(value["lat"]), "lon": str(value["lon"])}
                else:
                    document[field] = {"lat": "", "lon": ""}
            else:
                document[field] = None

        return document
