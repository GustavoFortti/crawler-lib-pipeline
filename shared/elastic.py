import os

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

        host = os.getenv('ELASTIC_HOST')
        port = os.getenv('ELASTIC_PORT')
        username = os.getenv('ELASTIC_USER')
        password = os.getenv('ELASTIC_PASS')

        # Criar uma instância do cliente Elasticsearch
        self.es = Elasticsearch(
            hosts=[{'host': host, 'port': port}],
            http_auth=(username, password),
            scheme='https',
            verify_certs=False
        )

        print(self.es.ping())
        # # self.find_all()

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
    
    def bulkload(self, data):
        """
        Realiza o carregamento em massa de documentos no Elasticsearch.
        :param data: Uma lista de documentos a serem indexados.
        """
        actions = [
            {
                "_index": self.index_name,
                "_source": document
            }
            for document in data
        ]

        # response = helpers.bulk(self.es, actions)

        # if response[0] > 0:
        #     print(f"Erro ao carregar documentos: {response[0]} documentos falharam")
        # else:
        #     print("Carregamento de documentos concluído com sucesso")

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