from typing import List
import pandas as pd


def extract_clients(clients_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extrai e prepara o DataFrame de clientes para o modelo relacional.

    Args:
        clients_df (pd.DataFrame): DataFrame com dados da coleção clients do MongoDB.

    Returns:
        pd.DataFrame: DataFrame com colunas id, nome, email, data_cadastro.
    """
    # Assume que o clients_df já está com as colunas corretas
    return clients_df[['id', 'nome', 'email', 'data_cadastro']].copy()


def extract_products(products_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extrai e prepara o DataFrame de produtos para o modelo relacional.

    Args:
        products_df (pd.DataFrame): DataFrame com dados da coleção products do MongoDB.

    Returns:
        pd.DataFrame: DataFrame com colunas id, nome, preco.
    """
    return products_df[['id', 'nome', 'preco']].copy()


def generate_pedidos_from_carts(carts_df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera DataFrame de pedidos a partir da coleção de carrinhos.

    Args:
        carts_df (pd.DataFrame): DataFrame com os carrinhos do MongoDB.

    Returns:
        pd.DataFrame: DataFrame com colunas id, cliente_id, data_pedido.
    """
    pedidos = carts_df[['cliente_id', 'ultima_atualizacao']].copy()
    pedidos.rename(columns={'ultima_atualizacao': 'data_pedido'}, inplace=True)
    pedidos['id'] = range(1, len(pedidos) + 1)  # gera IDs sequenciais para pedidos
    return pedidos[['id', 'cliente_id', 'data_pedido']]


def generate_itens_pedido_from_carts(
    carts_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Gera DataFrame de itens do pedido a partir dos carrinhos.

    Args:
        carts_df (pd.DataFrame): DataFrame com os carrinhos do MongoDB.

    Returns:
        pd.DataFrame: DataFrame com colunas pedido_id, produto_id, quantidade, preco_unitario.
        **ATENÇÃO**: Como o preço unitário não está na coleção carts, deve ser incorporado posteriormente ou buscado do catálogo de produtos.
    """
    registros: List[dict] = []

    for idx, row in carts_df.iterrows():
        pedido_id = idx + 1  # corresponde ao id gerado no pedido
        for item in row['itens']:
            registros.append({
                'pedido_id': pedido_id,
                'produto_id': item['produto_id'],
                'quantidade': item['quantidade'],
                'preco_unitario': item['preco_unitario']
            })

    return pd.DataFrame(registros)
