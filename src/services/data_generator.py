from faker import Faker
from random import randint, uniform, sample
from typing import List, Tuple
from loguru import logger
import json
import os
import uuid

fake = Faker("pt_BR")

NUM_REVIEWS = 20_000
NUM_CARTS = 100_000
NUM_PRODUCTS = 100
NUM_CLIENTS = 5_000

def generate_clients(n: int) -> List[dict]:
    logger.info(f"Gerando {n} clientes...")
    return [
        {
            "id": i,
            "nome": fake.name(),
            "email": fake.email(),
            "data_cadastro": fake.date_between(start_date="-2y", end_date="today").isoformat(),
        }
        for i in range(1, n + 1)
    ]

def generate_products(n: int) -> List[dict]:
    logger.info(f"Gerando {n} produtos...")
    return [
        {
            "id": i,
            "nome": fake.word().capitalize(),
            "preco": round(uniform(10.0, 500.0), 2)
        }
        for i in range(1, n + 1)
    ]

def generate_reviews(n: int, client_ids: List[int]) -> List[dict]:
    logger.info(f"Gerando {n} avaliações de produtos...")
    return [
        {
            "produto_id": randint(1, NUM_PRODUCTS),
            "cliente_id": fake.random_element(elements=client_ids),
            "avaliacao": round(uniform(1.0, 5.0), 1),
            "comentario": fake.sentence(nb_words=6),
            "data": fake.date_time_between(start_date="-1y", end_date="now").isoformat()
        }
        for _ in range(n)
    ]

def generate_carts(n: int, client_ids: List[int], products: List[dict]) -> List[dict]:
    logger.info(f"Gerando {n} carrinhos de compras...")
    product_price_map = {p["id"]: p["preco"] for p in products}
    carts = []
    for _ in range(n):
        num_items = randint(1, 5)
        produtos_ids = sample(range(1, NUM_PRODUCTS + 1), num_items)
        itens = []
        for pid in produtos_ids:
            quantidade = randint(1, 3)
            preco_unitario = product_price_map[pid]
            itens.append({
                "produto_id": pid,
                "quantidade": quantidade,
                "preco_unitario": preco_unitario
            })
        cart = {
            # Usando UUID para garantir id único do pedido
            "pedido_id": str(uuid.uuid4()),
            "cliente_id": fake.random_element(elements=client_ids),
            "itens": itens,
            "ultima_atualizacao": fake.date_time_between(start_date="-1y", end_date="now").isoformat()
        }
        carts.append(cart)
    return carts

def save_json(data: List[dict], path: str) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.success(f"Arquivo salvo com sucesso: {path}")
    except Exception as e:
        logger.error(f"Erro ao salvar o arquivo {path}: {e}")

def generate_and_save_data(output_dir: str) -> Tuple[str, str, str, str]:
    logger.info("Iniciando geração de dados...")

    os.makedirs(output_dir, exist_ok=True)

    clients = generate_clients(NUM_CLIENTS)
    client_ids = [client["id"] for client in clients]

    products = generate_products(NUM_PRODUCTS)
    reviews = generate_reviews(NUM_REVIEWS, client_ids)
    carts = generate_carts(NUM_CARTS, client_ids, products)

    clients_path = os.path.join(output_dir, "clientes.json")
    products_path = os.path.join(output_dir, "produtos.json")
    reviews_path = os.path.join(output_dir, "avaliacoes.json")
    carts_path = os.path.join(output_dir, "carrinhos.json")

    save_json(clients, clients_path)
    save_json(products, products_path)
    save_json(reviews, reviews_path)
    save_json(carts, carts_path)

    return clients_path, products_path, reviews_path, carts_path


if __name__ == "__main__":
    final_output_dir = os.path.abspath("data/json/generated_data")
    generate_and_save_data(final_output_dir)
