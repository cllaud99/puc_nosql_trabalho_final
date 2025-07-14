import os
import sys
import time
from typing import List, Dict
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

from services.data_generator import generate_clients, generate_carts, generate_reviews, generate_products
from services.mongo_handler import MongoDBClient
from services.mysql_handler import MySQLClient
from etl.transform_to_relational import (
    extract_clients,
    extract_products,
    generate_pedidos_from_carts,
    generate_itens_pedido_from_carts
)
from loguru import logger
from analysis.benchmark import run_benchmark

BENCHMARK_PATH = "data/csv/benchmarks"
BENCHMARK_FILE = os.path.join(BENCHMARK_PATH, "benchmark_results.csv")
os.makedirs(BENCHMARK_PATH, exist_ok=True)

mongodb = MongoDBClient()
mysqldb = MySQLClient()

def clear_benchmark_folder() -> None:
    files = os.listdir(BENCHMARK_PATH)
    for f in files:
        file_path = os.path.join(BENCHMARK_PATH, f)
        if os.path.isfile(file_path):
            os.remove(file_path)
    logger.info(f"Pasta '{BENCHMARK_PATH}' limpa antes da execução.")

def append_benchmark_result(query: str, banco: str, tempo: float) -> None:
    """
    Adiciona uma linha de benchmark no arquivo CSV de resultados,
    criando o arquivo se não existir.
    """
    df_new = pd.DataFrame([{"query": query, "banco": banco, "tempo": tempo}])
    
    if not os.path.exists(BENCHMARK_FILE):
        df_new.to_csv(BENCHMARK_FILE, index=False)
    else:
        df_existing = pd.read_csv(BENCHMARK_FILE)
        df_result = pd.concat([df_existing, df_new], ignore_index=True)
        df_result.to_csv(BENCHMARK_FILE, index=False)
    logger.info(f"Benchmark salvo: {query}, {banco}, {tempo:.4f}s")


def write_and_benchmark_mysql(df: pd.DataFrame, table_name: str) -> None:
    start_time = time.perf_counter()
    mysqldb.df_to_table(df, table_name)
    elapsed = time.perf_counter() - start_time
    append_benchmark_result(query=f"write_{table_name}", banco="MySQL", tempo=elapsed)
    logger.success(f"Dados escritos na tabela '{table_name}' em {elapsed:.4f} segundos.")


def write_and_benchmark_mongo(collection_name: str, data: List[Dict]) -> None:
    start_time = time.perf_counter()
    mongodb.insert_many(collection_name, data)
    elapsed = time.perf_counter() - start_time
    append_benchmark_result(query=f"write_{collection_name}", banco="MongoDB", tempo=elapsed)
    logger.success(f"Dados inseridos na coleção '{collection_name}' em {elapsed:.4f} segundos.")


def run_pipeline() -> None:
    logger.info("🚀 Iniciando pipeline de geração e carga de dados...")

    # 1. Geração dos dados
    logger.info("Gerando dados de clientes, produtos, avaliações e carrinhos...")
    clients: List[Dict] = generate_clients(5000)
    client_ids: List[int] = [client["id"] for client in clients]
    products: List[Dict] = generate_products(100)
    reviews = generate_reviews(2000, client_ids)
    carts = generate_carts(1000, client_ids, products)
    logger.success("✅ Dados gerados com sucesso!")

    # 2. Inserção no MongoDB com benchmark
    mongodb.connect("ecommerce")
    mongodb.clear_collections(["clients", "products", "reviews", "carts"])

    write_and_benchmark_mongo("clients", clients)
    write_and_benchmark_mongo("products", products)
    write_and_benchmark_mongo("reviews", reviews)
    write_and_benchmark_mongo("carts", carts)

    # 3. Extração dos dados do MongoDB para DataFrames
    df_clients = mongodb.to_dataframe("clients")
    df_products = mongodb.to_dataframe("products")
    df_reviews = mongodb.to_dataframe("reviews")
    df_carts = mongodb.to_dataframe("carts")

    logger.info(f"📦 {len(df_clients)} clientes carregados do MongoDB")
    logger.info(f"📦 {len(df_products)} produtos carregados do MongoDB")
    logger.info(f"📦 {len(df_reviews)} avaliações carregadas do MongoDB")
    logger.info(f"🛒 {len(df_carts)} carrinhos carregados do MongoDB")

    # 4. Transformações para o modelo relacional
    df_clients_transformed = extract_clients(df_clients)
    df_products_transformed = extract_products(df_products)
    df_pedidos = generate_pedidos_from_carts(df_carts)
    df_itens_pedido = generate_itens_pedido_from_carts(df_carts)

    logger.info("🧪 Transformações concluídas!")

    # 5. Carga no MySQL com benchmark
    mysqldb.connect()
    mysqldb.drop_all_tables()
    mysqldb.create_all_tables()

    write_and_benchmark_mysql(df_clients_transformed, "clientes")
    write_and_benchmark_mysql(df_products_transformed, "produtos")
    write_and_benchmark_mysql(df_pedidos, "pedidos")
    write_and_benchmark_mysql(df_itens_pedido, "itens_pedido")

    logger.success("🎉 Pipeline finalizada com sucesso!")


if __name__ == "__main__":
    clear_benchmark_folder()
    run_pipeline()
    run_benchmark()
