## NFERC - Classificador de despesas a partir de Nota Fiscais Eletrônicas com IA generativa (LLM).  $${\color{red}[in \space progress]}$$

**NFERC - _Nota Fiscal Eletrônica Receipt Classifier_** é um sistema que automatiza a classificação de despesas a partir de
arquivos XML de NF-e (Notas Fiscais Eletrônicas) usando IA generativa (LLMs - Large Language Models).
O **NFERC** lê o XML da NF-e, consulta o LLaMA 2 que sugere a _categoria_ com _justificativa_ para a despesa.

O projeto é implementado em Python e Vuejs, **rodando localmente com Docker e sem depender de cloud**. Todas as
dependências rodam em ambiente de desenvolvimento.

Em resumo, o sistema faz o seguinte processo:

> **Python extrai XML → FastAPI envia para LLaMA 2 → LLaMA 2 sugere categoria com justificativa → Python grava no
PostgreSQL com status "sugerido" → Usuário valida aprovando ou rejeitando a despesa no frontend Vuejs**

---

**Diferencial:** roda 100% em Docker na sua máquina com LLaMA 2 via **Ollama**.

## Arquitetura

```
                     Docker Network
────────────────────────────────────────────────────────────

              +----------------------+
              |      Frontend        |
              |      nginx           |
              +----------+-----------+
                         |
                         |
              +----------v-----------+
              |     FastAPI API      |
              |  Uvicorn             |
              |  Health Checks       |
              +----------+-----------+
                         |
        +----------------+----------------+
        |                                 |
+-------v--------+                +-------v--------+
| PostgreSQL     |                | Ollama         |
| Healthcheck    |                | Healthcheck    |
| Persistent Vol |                | Persistent Vol |
+----------------+                +----------------+

```

## Como inicializar o Sistema

@TODO

```bash
# 1. subir tudo
$ docker-compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache
```

```bash
# 1. subir tudo
$ docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Como instalar o modelo no ollama
```bash
# 2. baixar modelo local (só primeira vez)
$ docker exec -it mlocks-nferc-ollama ollama pull gemma2:2b
```

### Pré-requisitos

@TODO

### Principais URLs

#### Backend: http://localhost:8000/

#### Frontend: http://localhost:5173/

#### Swagger docs da API: http://localhost:8000/docs

#### Ollama: http://localhost:11434

### Estrutura de arquivos do Projeto

```
.
├── api
│   ├── Dockerfile
│   ├── main.py
│   ├── nfe_classifier
│   │   ├── classifiers
│   │   │   ├── classify_batch.py
│   │   │   ├── classify_file.py
│   │   │   └── __init__.py
│   │   ├── config.py
│   │   ├── infrastructure
│   │   │   ├── csv_reporter.py
│   │   │   ├── file_repository.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── interfaces.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── services
│   │   │   ├── api_client.py
│   │   │   ├── classifiers.py
│   │   │   ├── __init__.py
│   │   │   └── nfe_xml_extractor.py
│   │   └── utils
│   │       ├── execution_timer.py
│   │       └── __init__.py
│   └── requirements.txt
├── docker-compose.dev.yml
├── docker-compose.yml
├── .env.example
├── frontend
│   └── index.html
├── .gitignore
├── LICENSE
├── nfe_files
├── README.md
└── scripts
    ├── init_db.py
    └── init_db.sql

9 directories, 29 files
```

### Importador de NFe nfe_importer.py

@TODO

```bash
$ python3 api/nfe_classifier/main.py ./nfe_files/ --mode ollama --workers 5
```

A saída seria algo como:

```
Encontrados 6 XMLs
✅ [1/6] nfe6271606493106188290.xml -> Eletrônicos
✅ [2/6] nota_500418-100.xml -> Despesas com Serviços
✅ [3/6] NFe42251238181833000179550010000068791673229235-nfe.xml -> Equipamento de Oficina
✅ [4/6] 42260300718661000157550010012017901706151365.xml -> Material de construção
✅ [5/6] 42250644004468000120550010000006461043157399-procNFe.xml -> Manutenção e Reparo de Equipamentos
✅ [6/6] 42251144004468000120550010000012011178847429-procNFe.xml -> Roupas e Acessórios
```

### Modelos do Ollama e como utilizá-los

@TODO

## Banco de Dados

@TODO

## Testes

@TODO

## Endpoints

@TODO

## Referências

@TODO

## Licença

FastAPI - This project is licensed under the terms of the [MIT license](https://fastapi.tiangolo.com/#license)

Vue.js - The Progressive JavaScript Framework is released under the [MIT license](https://opensource.org/licenses/MIT).