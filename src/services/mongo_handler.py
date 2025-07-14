import os
from typing import Optional, List, Dict, Any
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

class MongoDBClient:
    """
    Classe para encapsular operações básicas de conexão e manipulação
    de dados no MongoDB.
    """

    def __init__(self, uri: Optional[str] = None) -> None:
        """
        Inicializa a classe definindo a URI de conexão.

        Args:
            uri (Optional[str]): URI do MongoDB. Se None, busca no ambiente.
        """
        self.uri = uri or self._get_mongo_uri()
        self.client: Optional[MongoClient] = None
        self.db = None

    def _get_mongo_uri(self) -> str:
        """
        Recupera a URI de conexão com base na variável de ambiente IN_DOCKER.

        Retorna:
            str: URI do MongoDB.
        """
        in_docker = os.getenv("IN_DOCKER", "false").lower()
        if in_docker == "true":
            return os.getenv("MONGO_URI_DOCKER", "mongodb://mongo:27017")
        return os.getenv("MONGO_URI_LOCAL", "mongodb://localhost:27017")

    def connect(self, db_name: str) -> None:
        """
        Estabelece conexão com o MongoDB e seleciona o banco de dados.

        Args:
            db_name (str): Nome do banco de dados a ser usado.

        Raises:
            ConnectionFailure: Se a conexão falhar.
        """
        try:
            self.client = MongoClient(self.uri)
            self.client.admin.command('ping')  # Verifica conexão
            self.db = self.client[db_name]
            logger.success(f"Conectado ao MongoDB: {self.uri}, DB: {db_name}")
        except ConnectionFailure as e:
            logger.error(f"Falha na conexão com MongoDB: {e}")
            raise

    def insert_many(self, collection_name: str, documents: List[Dict[str, Any]]) -> None:
        """
        Insere múltiplos documentos em uma coleção.

        Args:
            collection_name (str): Nome da coleção.
            documents (List[Dict[str, Any]]): Lista de documentos para inserir.

        Raises:
            PyMongoError: Em caso de falha na inserção.
        """
        try:
            collection = self.db[collection_name]
            result = collection.insert_many(documents)
            logger.success(f"{len(result.inserted_ids)} documentos inseridos em '{collection_name}'")
        except PyMongoError as e:
            logger.error(f"Erro ao inserir documentos em '{collection_name}': {e}")
            raise

    def find(self, collection_name: str, query: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
        """
        Realiza consulta na coleção com filtro opcional.

        Args:
            collection_name (str): Nome da coleção.
            query (Dict[str, Any], opcional): Filtro da consulta. Default é {} (todos).

        Returns:
            List[Dict[str, Any]]: Lista de documentos encontrados.

        Raises:
            PyMongoError: Em caso de falha na consulta.
        """
        try:
            collection = self.db[collection_name]
            results = list(collection.find(query))
            logger.info(f"{len(results)} documentos encontrados em '{collection_name}' com query {query}")
            return results
        except PyMongoError as e:
            logger.error(f"Erro na consulta em '{collection_name}': {e}")
            raise

    def clear_collections(self, collections: List[str]) -> None:
        """
        Remove todos os documentos das coleções especificadas.

        Args:
            collections (List[str]): Lista com os nomes das coleções a serem esvaziadas.

        Raises:
            PyMongoError: Em caso de falha na limpeza.
        """
        for name in collections:
            try:
                result = self.db[name].delete_many({})
                logger.warning(f"Removidos {result.deleted_count} documentos da coleção '{name}'.")
            except PyMongoError as e:
                logger.error(f"Erro ao limpar a coleção '{name}': {e}")
                raise


    def to_dataframe(self, collection_name: str, query: Dict[str, Any] = {}) -> pd.DataFrame:
        """
        Converte os documentos de uma coleção MongoDB para um DataFrame do pandas.

        Args:
            collection_name (str): Nome da coleção a ser consultada.
            query (Dict[str, Any], opcional): Filtro da consulta. Default é {} (todos os documentos).

        Returns:
            pd.DataFrame: DataFrame contendo os documentos da coleção.

        Raises:
            PyMongoError: Em caso de erro na leitura da coleção.
        """
        try:
            logger.info(f"Convertendo documentos da coleção '{collection_name}' para DataFrame...")
            documents = self.find(collection_name, query)
            df = pd.DataFrame(documents)

            if "_id" in df.columns:
                df.drop(columns=["_id"], inplace=True)

            logger.success(f"DataFrame criado com {len(df)} registros da coleção '{collection_name}'.")
            return df

        except PyMongoError as e:
            logger.error(f"Erro ao converter coleção '{collection_name}' para DataFrame: {e}")
            raise

if __name__ == "__main__":
    mongo_client = MongoDBClient()
    try:
        mongo_client.connect("pedidos")
        logger.info("Teste: conexão e inserção simples")
        sample_docs = [
            {"produto_id": 1, "cliente_id": 1, "avaliacao": 4.5, "comentario": "Ótimo produto", "data": "2025-07-10T12:00:00Z"}
        ]
        mongo_client.insert_many("avaliacoes", sample_docs)
        docs = mongo_client.find("avaliacoes", {"produto_id": 1})
        logger.info(f"Documentos recuperados: {docs}")
    except Exception as e:
        logger.error(f"Erro no teste da classe MongoDBClient: {e}")
