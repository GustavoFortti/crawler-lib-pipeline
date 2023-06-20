import os
from copy import deepcopy
from typing import Tuple, Dict, Any
from datetime import datetime

from elasticsearch import Elasticsearch, helpers

class Elastic():
    def __init__(self, env_config, job_config) -> None:
        """
        Inicializa a classe Elastic.
        Recupera as configurações de conexão com o Elasticsearch a partir de variáveis de ambiente.
        """
        job_name = env_config["job_name"]
        self.index_name = job_name
        self.job_config = job_config

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

        if (not self.es.indices.exists(index=self.index_name)):
            mapping = self.job_config["bulkload"]["mapping"]
            response = self.es.indices.create(index=self.index_name, body=mapping)

            if (not response["acknowledged"]):
                print("Erro ao criar o indice")
                return

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
    