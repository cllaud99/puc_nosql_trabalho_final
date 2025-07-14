from typing import List, Dict

def mysql_total_pedidos_por_cliente_query() -> str:
    """
    Retorna a query SQL para obter o total de clientes cadastrados por ano no MySQL, limitado ao top 10.
    """
    return """
    SELECT 
        c.id AS cliente_id,
        c.nome,
        COUNT(p.id) AS total_pedidos
    FROM clientes c
    LEFT JOIN pedidos p ON p.cliente_id = c.id
    GROUP BY c.id, c.nome
    ORDER BY total_pedidos DESC
    LIMIT 10;
    """

def mongodb_total_pedidos_por_cliente_pipeline() -> list:
    return [
        {
            "$group": {
                "_id": "$cliente_id",
                "total_pedidos": {"$sum": 1}
            }
        },
        {
            "$lookup": {
                "from": "clients",
                "localField": "_id",
                "foreignField": "id",
                "as": "cliente_info"
            }
        },
        {
            "$unwind": "$cliente_info"
        },
        {
            "$project": {
                "cliente_id": "$_id",
                "nome": "$cliente_info.nome",
                "total_pedidos": 1,
                "_id": 0
            }
        },
        {
            "$sort": {"total_pedidos": -1}
        },
        {
            "$limit": 10
        }
    ]

def mysql_total_vendido_por_produto_query() -> str:
    """
    Retorna a query SQL para obter o total vendido (quantidade) por produto no MySQL, limitado ao top 10.
    """
    return """
    SELECT 
        pr.id AS produto_id,
        pr.nome,
        SUM(ip.quantidade) AS total_vendido
    FROM produtos pr
    LEFT JOIN itens_pedido ip ON ip.produto_id = pr.id
    GROUP BY pr.id, pr.nome
    ORDER BY total_vendido DESC
    LIMIT 10;
    """

def mongodb_total_vendido_por_produto_pipeline() -> List[Dict]:
    """
    Pipeline MongoDB para total vendido (quantidade) por produto, limitado ao top 10.
    """
    return [
        {"$unwind": "$itens"},
        {
            "$group": {
                "_id": "$itens.produto_id",
                "total_vendido": {"$sum": "$itens.quantidade"}
            }
        },
        {
            "$lookup": {
                "from": "products",
                "localField": "_id",
                "foreignField": "id",
                "as": "produto_info"
            }
        },
        {"$unwind": "$produto_info"},
        {
            "$project": {
                "produto_id": "$_id",
                "nome": "$produto_info.nome",
                "total_vendido": 1,
                "_id": 0
            }
        },
        {"$sort": {"total_vendido": -1}},
        {"$limit": 10}
    ]

def mysql_avg_gasto_por_cliente_query() -> str:
    """
    Query para calcular a média de gastos por cliente no MySQL, limitado ao top 10.
    """
    return """
    SELECT
        c.id AS cliente_id,
        c.nome,
        COALESCE(SUM(ip.quantidade * ip.preco_unitario), 0) / NULLIF(COUNT(DISTINCT p.id), 0) AS media_gasto
    FROM clientes c
    LEFT JOIN pedidos p ON p.cliente_id = c.id
    LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
    GROUP BY c.id, c.nome
    ORDER BY media_gasto DESC
    LIMIT 10;
    """

def mongodb_avg_gasto_por_cliente_pipeline() -> list:
    """
    Pipeline para calcular a média de gastos por pedido por cliente na coleção carts do MongoDB, limitado ao top 10.
    """
    return [
        {"$unwind": "$itens"},
        {
            "$group": {
                "_id": {"cliente_id": "$cliente_id", "pedido_id": "$_id"},
                "total_pedido": {
                    "$sum": {"$multiply": ["$itens.quantidade", "$itens.preco_unitario"]}
                }
            }
        },
        {
            "$group": {
                "_id": "$_id.cliente_id",
                "total_gasto": {"$sum": "$total_pedido"},
                "total_pedidos": {"$sum": 1}
            }
        },
        {
            "$lookup": {
                "from": "clients",
                "localField": "_id",
                "foreignField": "id",
                "as": "cliente_info"
            }
        },
        {"$unwind": "$cliente_info"},
        {
            "$project": {
                "cliente_id": "$_id",
                "nome": "$cliente_info.nome",
                "media_gasto": {
                    "$cond": [
                        {"$eq": ["$total_pedidos", 0]},
                        0,
                        {"$divide": ["$total_gasto", "$total_pedidos"]}
                    ]
                },
                "_id": 0
            }
        },
        {"$sort": {"media_gasto": -1}},
        {"$limit": 10}
    ]
