# Análise Comparativa: MySQL vs. MongoDB

Este projeto implementa um pipeline de dados para comparar o desempenho de um banco de dados relacional (MySQL) e um NoSQL (MongoDB) em um cenário de e-commerce. O processo é totalmente containerizado com Docker para garantir a facilidade de execução e a reprodutibilidade.

## 🚀 Sobre o Projeto

O objetivo é demonstrar na prática as vantagens e desvantagens de cada modelo de banco de dados. O pipeline realiza as seguintes etapas:

1.  **Geração de Dados**: Cria dados sintéticos de clientes, produtos, avaliações e carrinhos de compra.
2.  **Carga no MongoDB**: Insere os dados gerados no MongoDB.
3.  **ETL para MySQL**: Extrai os dados do MongoDB, transforma-os para o modelo relacional e os carrega no MySQL.
4.  **Benchmark**: Executa uma série de consultas de escrita e leitura em ambos os bancos para medir e comparar o tempo de execução.

## 🛠️ Pré-requisitos

Para executar este projeto, você precisará ter instalado:

* [Docker](https://www.docker.com/get-started)
* [Docker Compose](https://docs.docker.com/compose/install/)

## ▶️ Como Executar

Siga os passos abaixo para rodar a aplicação em seu ambiente local.

### 1. Clone o Repositório

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd <NOME_DA_PASTA_DO_PROJETO>
```

### 2. Crie o Arquivo de Ambiente

O projeto utiliza um arquivo `.env` para configurar as variáveis de ambiente. Crie um arquivo chamado `.env` na raiz do projeto com o seguinte conteúdo:

```env
# Indica se está rodando em container Docker
IN_DOCKER=true

# MySQL LOCAL
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=pedidos
# MySQL DOCKER
MYSQL_HOST_DOCKER=mysql

# MongoDB para local
MONGO_URI_LOCAL=mongodb://localhost:27017
# MongoDB para Docker
MONGO_URI_DOCKER=mongodb://mongo:27017
```

### 3. Suba os Contêineres com Docker Compose

Este é o comando principal. Ele irá construir as imagens, criar os contêineres para a aplicação, o MySQL e o MongoDB, e iniciar todo o pipeline.

```bash
docker-compose up --build
```

O script `main.py` será executado automaticamente assim que os serviços dos bancos de dados estiverem prontos.

## 📊 O que Acontece Durante a Execução?

Ao executar o `docker-compose up`, você verá os logs no seu terminal:

1.  Os serviços do MySQL e MongoDB serão iniciados.
2.  O script `wait-for-it.sh` irá aguardar o MySQL ficar disponível.
3.  O script Python `src/main.py` começará a ser executado.
4.  Logs da `loguru` indicarão cada passo do pipeline: geração de dados, carga no MongoDB, transformações e carga no MySQL.
5.  Ao final, as consultas de benchmark serão executadas.

## ✅ Verificando os Resultados

Após a execução bem-sucedida, os resultados dos benchmarks serão salvos na pasta `data/csv/benchmarks/`. Você pode inspecionar os seguintes arquivos:

* `benchmark_results.csv`: Contém os tempos de todas as operações de escrita e leitura.
* Arquivos `.csv` individuais para cada consulta comparativa (ex: `mysql_total_pedidos_por_cliente.csv`).

Para parar e remover os contêineres, pressione `Ctrl + C` no terminal onde o docker-compose está rodando e depois execute:

```bash
docker-compose down