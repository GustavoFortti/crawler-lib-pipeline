import os

from datetime import datetime
from elasticsearch import Elasticsearch

doc = {
    'author': 'kimchy',
    'text': 'Elasticsearch: cool. bonsai cool.',
    'timestamp': datetime.now(),
}

class Elastic():
    def __init__(self) -> None:
        host = os.getenv('ELASTIC_HOST')
        port = os.getenv('ELASTIC_PORT')
        username = os.getenv('ELASTIC_USER')
        password = os.getenv('ELASTIC_PASS')

        self.es = Elasticsearch(
            [{'host': host, 'port': int(port), 'scheme': 'https'}],
            basic_auth=(username, password),
            verify_certs=False,
        )

        # print(self.es.ping())
        self.find_all()

    def find_all(self):
        search_query = {
            "query": {
                "match_all": {}
            }
        }

        # Execute the search request
        response = self.es.search(index="vivareal", body=search_query)

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

    def create_document(self, index: str, document: dict) -> dict:
        """
        Cria um documento no Elasticsearch.
        :param index: O nome do indice.
        :param document: O documento a ser criado.
        :return: O resultado da operacao de criacao.
        """
        resultado = self.es.index(index=index, body=document)
        return resultado

    def update_document(self, index: str, id: str, updates: dict) -> dict:
        """
        Atualiza um documento existente no Elasticsearch.
        :param index: O nome do indice.
        :param id: O ID do documento.
        :param updates: As atualizacões a serem aplicadas ao documento.
        :return: O resultado da operacao de atualizacao.
        """
        resultado = self.es.update(index=index, id=id, body={"doc": updates})
        return resultado

    def delete_document(self, index: str, id: str) -> dict:
        """
        Exclui um documento existente no Elasticsearch.
        :param index: O nome do indice.
        :param id: O ID do documento.
        :return: O resultado da operacao de exclusao.
        """
        resultado = self.es.delete(index=index, id=id)
        return resultado

    def check_existing_document(self, index: str, id: str) -> bool:
        """
        Verifica se o documento já existe no Elasticsearch.
        :param index: O nome do indice.
        :param id: O ID do documento.
        :return: True se o documento existir, False caso contrário.
        """
        resultado = self.es.exists(index=index, id=id)
        return resultado