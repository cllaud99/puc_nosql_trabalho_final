import os
import sys
from typing import List, Dict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

import time
import pandas as pd
from loguru import logger
from sqlalchemy import text
from services.mysql_handler import MySQLClient
from services.mongo_handler import MongoDBClient
from analysis.comparison_queries import (
    mysql_total_pedidos_por_cliente_query,
    mongodb_total_pedidos_por_cliente_pipeline,
    mysql_total_vendido_por_produto_query,
    mongodb_total_vendido_por_produto_pipeline,
    mysql_avg_gasto_por_cliente_query,
    mongodb_avg_gasto_por_cliente_pipeline
)

BENCHMARK_PATH = "data/csv/benchmarks"
BENCHMARK_FILE = os.path.join(BENCHMARK_PATH, "benchmark_results.csv")
os.makedirs(BENCHMARK_PATH, exist_ok=True)

def benchmark_mysql_query(client: MySQLClient, query: str, label: str) -> float:
    start = time.perf_counter()
    with client.engine.connect() as conn:
        df = pd.read_sql(text(query), conn)
    duration = time.perf_counter() - start
    df.to_csv(f"{BENCHMARK_PATH}/mysql_{label}.csv", index=False)
    logger.success(f"MySQL '{label}' executada em {duration:.4f} segundos.")
    return duration

def benchmark_mongodb_query(client: MongoDBClient, pipeline: List[Dict], collection: str, label: str) -> float:
    start = time.perf_counter()
    cursor = client.db[collection].aggregate(pipeline)
    data = list(cursor)
    duration = time.perf_counter() - start
    pd.DataFrame(data).to_csv(f"{BENCHMARK_PATH}/mongodb_{label}.csv", index=False)
    logger.success(f"MongoDB '{label}' executada em {duration:.4f} segundos.")
    return duration

def run_benchmark():
    logger.info("🔍 Iniciando benchmarks de performance...")

    mysql = MySQLClient()
    mongodb = MongoDBClient()
    mongodb.connect("ecommerce")

    resultados = []

    # Benchmark 1: Total pedidos por cliente
    resultados.append({
        "query": "total_pedidos_por_cliente",
        "banco": "MySQL",
        "tempo": benchmark_mysql_query(mysql, mysql_total_pedidos_por_cliente_query(), "total_pedidos_por_cliente")
    })
    resultados.append({
        "query": "total_pedidos_por_cliente",
        "banco": "MongoDB",
        "tempo": benchmark_mongodb_query(mongodb, mongodb_total_pedidos_por_cliente_pipeline(), "carts", "total_pedidos_por_cliente")
    })

    # Benchmark 2: Total vendido por produto
    resultados.append({
        "query": "total_vendido_por_produto",
        "banco": "MySQL",
        "tempo": benchmark_mysql_query(mysql, mysql_total_vendido_por_produto_query(), "total_vendido_por_produto")
    })
    resultados.append({
        "query": "total_vendido_por_produto",
        "banco": "MongoDB",
        "tempo": benchmark_mongodb_query(mongodb, mongodb_total_vendido_por_produto_pipeline(), "carts", "total_vendido_por_produto")
    })

    # Benchmark 3: Média de gasto por cliente
    resultados.append({
        "query": "avg_gasto_por_cliente",
        "banco": "MySQL",
        "tempo": benchmark_mysql_query(mysql, mysql_avg_gasto_por_cliente_query(), "avg_gasto_por_cliente")
    })
    resultados.append({
        "query": "avg_gasto_por_cliente",
        "banco": "MongoDB",
        "tempo": benchmark_mongodb_query(mongodb, mongodb_avg_gasto_por_cliente_pipeline(), "carts", "avg_gasto_por_cliente")
    })

    # Append ou cria o CSV sem apagar o existente
    df_new = pd.DataFrame(resultados)
    if os.path.exists(BENCHMARK_FILE):
        df_existing = pd.read_csv(BENCHMARK_FILE)
        df_concat = pd.concat([df_existing, df_new], ignore_index=True)
        df_concat.to_csv(BENCHMARK_FILE, index=False)
    else:
        df_new.to_csv(BENCHMARK_FILE, index=False)

    logger.success("✅ Benchmarks concluídos e salvos com sucesso.")

if __name__ == "__main__":
    run_benchmark()
