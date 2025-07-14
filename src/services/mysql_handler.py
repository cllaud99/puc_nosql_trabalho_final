import os
from typing import Optional
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


class MySQLClient:
    """
    Classe para manipulação de operações com MySQL utilizando SQLAlchemy e pandas.
    """

    def __init__(self, uri: Optional[str] = None) -> None:
        """
        Inicializa o cliente com a URI definida via parâmetro ou variável de ambiente.

        Args:
            uri (Optional[str]): URI de conexão MySQL. Se None, utiliza variável de ambiente.
        """
        self._adjust_environment_host()
        self.uri = uri or self._get_mysql_uri()
        self.engine = create_engine(self.uri)
        logger.debug(f"Engine SQLAlchemy criada com URI: {self.uri}")

    def _adjust_environment_host(self) -> None:
        """
        Ajusta dinamicamente o host do MySQL com base no ambiente (local ou Docker).
        """
        in_docker = os.getenv("IN_DOCKER", "false").lower() == "true"
        if in_docker:
            os.environ["MYSQL_HOST"] = os.getenv("MYSQL_HOST_DOCKER", "mysql")
            logger.debug("Executando em Docker. MYSQL_HOST ajustado para 'mysql'.")
        else:
            logger.debug("Executando localmente. MYSQL_HOST mantém valor padrão.")

    def _get_mysql_uri(self) -> str:
        """
        Retorna a URI do MySQL com base nas variáveis de ambiente.

        Returns:
            str: URI de conexão com MySQL.
        """
        user = os.getenv("MYSQL_USER", "root")
        password = os.getenv("MYSQL_PASSWORD", "root")
        host = os.getenv("MYSQL_HOST", "localhost")
        port = os.getenv("MYSQL_PORT", "3306")
        database = os.getenv("MYSQL_DATABASE", "pedidos")

        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

    def connect(self) -> None:
        """
        Testa a conexão com o banco executando um simples SELECT 1.
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.success("Conexão com MySQL bem-sucedida.")
        except SQLAlchemyError as e:
            logger.error(f"Erro ao testar conexão com MySQL: {e}")
            raise

    def df_to_table(self, df: pd.DataFrame, table_name: str, if_exists: str = "append") -> None:
        """
        Insere um DataFrame em uma tabela MySQL.

        Args:
            df (pd.DataFrame): DataFrame a ser inserido.
            table_name (str): Nome da tabela.
            if_exists (str): Comportamento se a tabela existir ('fail', 'replace', 'append').

        Raises:
            SQLAlchemyError: Em caso de erro na inserção.
        """
        try:
            df.to_sql(table_name, con=self.engine, if_exists=if_exists, index=False)
            logger.success(f"Tabela '{table_name}' criada/inserida com {len(df)} registros.")
        except SQLAlchemyError as e:
            logger.error(f"Erro ao inserir DataFrame na tabela '{table_name}': {e}")
            raise

    def read_table(self, table_name: str) -> pd.DataFrame:
        """
        Lê uma tabela do MySQL para um DataFrame.

        Args:
            table_name (str): Nome da tabela a ser lida.

        Returns:
            pd.DataFrame: Conteúdo da tabela como DataFrame.

        Raises:
            SQLAlchemyError: Em caso de erro na leitura.
        """
        try:
            df = pd.read_sql_table(table_name, con=self.engine)
            logger.info(f"Tabela '{table_name}' lida com sucesso. Total de registros: {len(df)}.")
            return df
        except SQLAlchemyError as e:
            logger.error(f"Erro ao ler a tabela '{table_name}': {e}")
            raise

    def create_all_tables(self) -> None:
        """
        Cria as tabelas no banco de dados relacional conforme o schema definido.
        """
        ddl = """
        CREATE TABLE IF NOT EXISTS clientes (
          id INT AUTO_INCREMENT PRIMARY KEY,
          nome VARCHAR(100),
          email VARCHAR(100),
          data_cadastro DATE
        );

        CREATE TABLE IF NOT EXISTS produtos (
          id INT AUTO_INCREMENT PRIMARY KEY,
          nome VARCHAR(100),
          preco DECIMAL(10,2)
        );

        CREATE TABLE IF NOT EXISTS pedidos (
          id INT AUTO_INCREMENT PRIMARY KEY,
          cliente_id INT,
          data_pedido DATETIME,
          FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        );

        CREATE TABLE IF NOT EXISTS itens_pedido (
          pedido_id INT,
          produto_id INT,
          quantidade INT,
          preco_unitario DECIMAL(10,2),
          PRIMARY KEY (pedido_id, produto_id),
          FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
          FOREIGN KEY (produto_id) REFERENCES produtos(id)
        );
        """

        try:
            with self.engine.begin() as conn:
                for stmt in ddl.strip().split(";"):
                    stmt = stmt.strip()
                    if stmt:
                        conn.execute(text(stmt))
            logger.success("Tabelas criadas com sucesso (ou já existiam).")
        except SQLAlchemyError as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            raise

    def drop_all_tables(self) -> None:
        """
        Remove todas as tabelas do banco de dados atual, desabilitando temporariamente
        as constraints de chave estrangeira para evitar conflitos.

        Raises:
            SQLAlchemyError: Em caso de erro ao remover as tabelas.
        """
        try:
            with self.engine.begin() as conn:
                logger.warning("Desabilitando FOREIGN_KEY_CHECKS para dropar todas as tabelas.")
                conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))

                result = conn.execute(text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = :schema;"
                ), {"schema": self.engine.url.database})

                tables = [row[0] for row in result]
                for table in tables:
                    conn.execute(text(f"DROP TABLE IF EXISTS `{table}`;"))
                    logger.warning(f"Tabela '{table}' removida.")

                conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
                logger.success("Todas as tabelas foram removidas com sucesso.")
        except SQLAlchemyError as e:
            logger.error(f"Erro ao dropar tabelas: {e}")
            raise


if __name__ == "__main__":
    mysql_client = MySQLClient()
    try:
        mysql_client.drop_all_tables()
        mysql_client.create_all_tables()

        df = pd.DataFrame([
            {"produto_id": 1, "cliente_id": 1, "avaliacao": 4.5, "comentario": "Muito bom", "data": "2025-07-10T12:00:00Z"}
        ])
        mysql_client.df_to_table(df, "avaliacoes")

        df_lido = mysql_client.read_table("avaliacoes")
        logger.info(f"Primeira linha da tabela:\n{df_lido.head(1)}")

    except Exception as e:
        logger.error(f"Erro no teste da classe MySQLClient: {e}")
