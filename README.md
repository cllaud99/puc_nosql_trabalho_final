# Trabalho Final – Integração e Benchmark de Bancos Relacionais e NoSQL  
**Curso:** Engenharia de Dados – PUC Minas

---

## 1. Introdução

Este trabalho final tem como objetivo principal compreender e aplicar os conceitos que diferenciam bancos de dados relacionais (RDBMS) e não relacionais (NoSQL), implementando um cenário prático integrado entre **MySQL** e **MongoDB**. Através deste projeto, avaliamos as vantagens, desvantagens, e o desempenho de cada modelo em diferentes operações, além de realizar a carga e análise dos dados entre ambos os sistemas.

---

## 2. Objetivos

- Entender as principais características dos modelos relacionais e NoSQL.
- Implementar um sistema de pedidos multicanal utilizando MySQL e MongoDB.
- Realizar a exportação e integração dos dados entre MongoDB e MySQL via Python.
- Avaliar desempenho das operações em ambos os bancos.
- Analisar aspectos de consistência eventual versus transacional.

---

## 3. Fundamentação Teórica

| Característica               | MySQL                          | MongoDB                         |
|-----------------------------|--------------------------------|--------------------------------|
| Modelo de dados             | Tabelas, colunas               | Documentos JSON/BSON            |
| Esquema                    | Estrito                        | Flexível                       |
| Suporte a transações       | Completo (ACID)                | Parcial (a nível de documento) |
| Escalabilidade             | Vertical                      | Horizontal                     |

O MySQL é amplamente utilizado para dados estruturados e operações transacionais críticas, enquanto o MongoDB oferece flexibilidade e escalabilidade para dados semi-estruturados, facilitando o desenvolvimento ágil e processamento de grandes volumes.

---

## 4. Metodologia

### 4.1 Cenário Proposto

Implementação de um sistema de pedidos multicanal onde:

- **MySQL** armazena dados estruturados: clientes, produtos, pedidos e itens dos pedidos.
- **MongoDB** gerencia dados semi-estruturados: avaliações, carrinho em tempo real, histórico e preferências dos clientes.

### 4.2 Modelagem

**MySQL (Relacional):**

```sql
CREATE TABLE clientes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100),
  email VARCHAR(100),
  data_cadastro DATE
);

CREATE TABLE produtos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100),
  preco DECIMAL(10,2)
);

CREATE TABLE pedidos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  cliente_id INT,
  data_pedido DATETIME,
  FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

CREATE TABLE itens_pedido (
  pedido_id INT,
  produto_id INT,
  quantidade INT,
  preco_unitario DECIMAL(10,2),
  PRIMARY KEY (pedido_id, produto_id),
  FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
  FOREIGN KEY (produto_id) REFERENCES produtos(id)
);
