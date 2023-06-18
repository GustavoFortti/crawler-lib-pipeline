import os
import psycopg2
import subprocess

class PostgreSQL:
    def __init__(self, env_config):
        self.job_name = env_config["job_name"]

        self.host = os.getenv('POSTGRES_HOST')
        self.port = os.getenv('POSTGRES_PORT')
        self.database = self.job_name
        self.username = os.getenv('POSTGRES_USER')
        self.password = os.getenv('POSTGRES_PASS')
        self.connection = None

        self.connect()

    def connect(self):
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password,
                
            )
            cursor_obj = self.connection.cursor()
            cursor_obj.execute("SELECT 1")
            print("Conctado ao PostgreSQL")
        except (Exception, psycopg2.Error) as error:
            print(f"Error ao conectar com PostgreSQL: {error}")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Disconnected from PostgreSQL")

    def execute_query(self, query):
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                return result
            except (Exception, psycopg2.Error) as error:
                print(f"Error executing query: {error}")
        else:
            print("Not connected to PostgreSQL. Please connect first.")

# # Exemplo de uso:
# connection = PostgreSQLConnection(env_config)
# connection.connect()

# # Executar uma consulta
# query = "SELECT * FROM my_table"
# result = connection.execute_query(query)
# print(result)

# # Desconectar
# connection.disconnect()
