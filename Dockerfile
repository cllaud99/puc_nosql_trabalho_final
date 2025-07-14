# Base image
FROM python:3.11-slim

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    IN_DOCKER=true

# Diretório de trabalho
WORKDIR /app

# Instala dependências do sistema (netcat)
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

# Instala dependências do Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia a aplicação
COPY pyproject.toml uv.lock ./
COPY src ./src
COPY data ./data
COPY logs ./logs
COPY wait-for-it.sh ./wait-for-it.sh
RUN chmod +x ./wait-for-it.sh

# Comando padrão
CMD ["./wait-for-it.sh", "mysql", "3306", "--", "python", "src/main.py"]
