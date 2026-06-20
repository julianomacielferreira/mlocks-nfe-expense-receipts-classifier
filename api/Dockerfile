# Usa Python 3.11 slim (~120MB)
FROM python:3.11-slim

# Define diretório de trabalho dentro do container
WORKDIR /app

# Instala dependências de sistema necessárias para compilar psycopg2
# gcc = compilador C
# libpq-dev = headers do PostgreSQL
# --no-install-recommends = não instala pacotes extras desnecessários
# rm -rf = limpa cache do apt para manter imagem pequena
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Copia SÓ o requirements primeiro (otimização de cache Docker)
COPY requirements.txt .

# Instala libs Python sem cache pip
RUN pip install --no-cache-dir -r requirements.txt

# Agora copia o resto do código
COPY . .

# Expõe porta
EXPOSE 8000

# Comando de inicialização
# --reload = recarrega automaticamente quando você salva arquivo
# --host 0.0.0.0 = aceita conexões de fora do container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app"]