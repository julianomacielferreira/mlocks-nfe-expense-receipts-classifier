## NFERC - Classificador de despesas a partir de Nota Fiscais Eletrônicas com IA generativa (LLM).

**NFERC - _Nota Fiscal Eletrônica Receipt Classifier_** é um sistema que automatiza a classificação de despesas a partir de
arquivos XML de NF-e (Notas Fiscais Eletrônicas) usando **IA generativa (LLMs - Large Language Models)**.
O **NFERC** lê o XML da NF-e, consulta o LLaMA 2 que sugere a _categoria_ com _justificativa_ para a despesa.

O projeto é implementado em Python e Vuejs, **rodando localmente com Docker e sem depender de cloud**. Todas as
dependências rodam em **ambiente de desenvolvimento**.

---

**Diferencial:** roda 100% em Docker na sua máquina com LLaMA 2 via **Ollama**.

![NFERC](mlocks-nferc-logo.png)

## Como inicializar o Projeto

Siga os seguintes passos para configurar e iniciar o projeto.

### Configuração do arquivo .ENV

Renomeie o arquivo [.env.example](https://github.com/julianomacielferreira/mlocks-nfe-expense-receipts-classifier/blob/main/.env.example) em `backend/.env.example` para **.env**

### Pré-requisitos

É necessário ter instalados o **[Docker](https://docs.docker.com/install/)** e **[Docker Compose](https://docs.docker.com/compose/install/)** em sua máquina.

### Subir o container docker

Execute os seguintes comandos para fazer o build, subir seus containers e fazer o download do modelo no ollama (LLM local):

```bash
$ docker-compose -f docker-compose.yml -f docker-compose.dev.yml build --no-cache
```

```bash
$ docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

```bash
$ docker exec -it mlocks-nferc-ollama ollama pull gemma2:2b
```

```bash
$ docker exec mlocks-nferc-ollama ollama pull nomic-embed-text
```

Para validar se o modelo foi baixado corretamente e interagir via _prompt_, execute o seguinte comando:

```bash
$ docker exec -it mlocks-nferc-ollama ollama run gemma2:2b
```

### Principais URLs

#### Backend: http://localhost:8000/

#### Frontend: http://localhost:5173/

#### Swagger docs da API: http://localhost:8000/docs

#### Ollama: http://localhost:11434

### Estrutura de arquivos do Projeto

```
.
├── api
│   ├── ai
│   │   ├── chunker
│   │   │   └── text_chunker.py
│   │   ├── classifiers
│   │   │   └── rag_classifier.py
│   │   ├── embeddings
│   │   │   └── provider.py
│   │   ├── generator
│   │   │   └── llm_client.py
│   │   ├── prompts
│   │   │   └── builder.py
│   │   └── retriever
│   │       └── vector_store.py
│   ├── database
│   │   └── session.py
│   ├── Dockerfile
│   ├── domain
│   │   ├── entities.py
│   │   └── schemas.py
│   ├── endpoints
│   │   └── controllers.py
│   ├── main.py
│   ├── repositories
│   │   └── classification_repo.py
│   ├── requirements.txt
│   └── util
│       ├── classification_service.py
│       └── xml_parser.py
├── docker-compose.dev.yml
├── docker-compose.yml
├── .env.example
├── frontend
│   └── index.html
├── .gitignore
├── LICENSE
├── nfe_classifier
│   ├── classifiers
│   │   ├── batch_classifier.py
│   │   ├── file_classifier.py
│   │   └── __init__.py
│   ├── config.py
│   ├── infrastructure
│   │   ├── csv_reporter.py
│   │   ├── file_repository.py
│   │   └── __init__.py
│   ├── __init__.py
│   ├── interfaces.py
│   ├── main.py
│   ├── models.py
│   ├── services
│   │   ├── api_client.py
│   │   ├── classifiers.py
│   │   ├── __init__.py
│   │   └── nfe_xml_extractor.py
│   └── utils
│       ├── execution_timer.py
│       └── __init__.py
├── nfe_files
├── README.md
└── scripts
    ├── init_db.py
    └── init_db.sql

21 directories, 42 files
```

### Classificador em lote de NFe

Dentro do projeto existe um sistema para classificação em batch `nfe_classifier/main.py`.

Para utilizá-lo, salve seus arquivos xml dentro do diretório `./nfe_files/` e use o comando abaixo
com o parâmetro `--workers {número-de-workers}` para controlar o paralelismo:

```bash
$ python3 nfe_classifier/main.py ./nfe_files/ --mode ollama --workers 2
```

A saída seria algo como:

```
Encontrados 16 XMLs
✅ [1/16] 342230134055015_v0400-procNFe.xml -> Veículos e Transportes
✅ [2/16] 42251144004468000120550010000013131485078828-procNFe.xml -> Manutenção e Reparos - Equipamentos de Oficina
✅ [3/16] 42250644004468000120550010000006461043157399-procNFe.xml -> Transporte
✅ [4/16] 42251144004468000120550010000012011178847429-procNFe.xml -> Transporte
✅ [5/16] 42260300718661000157550010012017901706151365.xml -> Materiais de Construção
✅ [6/16] 342220156142671_v0400-procNFe.xml -> Transporte
✅ [7/16] 42250644004468000120550010000006361865636646-procNFe.xml -> Manutenção de Equipamentos
✅ [8/16] 42220725124912000104550010000012211519672524-nfe.xml -> Transporte
✅ [9/16] NFe42251238181833000179550010000068791673229235-nfe.xml -> Manutenção de Equipamentos
✅ [10/16] 42250644004468000120550010000006471527213855-procNFe.xml -> Manutenção de Equipamentos
✅ [11/16] 42250444004468000120550010000003821370231918-procNFe.xml -> Manutenção de Equipamentos
✅ [12/16] 42250844004468000120550010000009321733053788-procNFe.xml -> Manutenção de Equipamentos
✅ [13/16] 42230625124912000104550010000014921343202807-nfe.xml -> Transporte
✅ [14/16] nfe6271606493106188290.xml -> Eletrônicos
✅ [15/16] 42250644004468000120550010000005861406912160-procNFe.xml -> Manutenção de Equipamentos
✅ [16/16] nota_500418-100.xml -> Materiais de Construção

CSV salvo em: nfe_files/resultado_classificacao_20260622_183336.csv
Tempo total: 254.80s
Média por arquivo: 15.92s
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

## License

Llama LLM - [Llama](https://developer.meta.com/ai/docs/overview/)

Qdrant - [High-Performance Vector Search](https://qdrant.tech/)

freeCodeCamp YouTube Channel - [Ollama Course – Build AI Apps Locally](https://www.youtube.com/watch?v=GWB9ApTPTv4)

FastAPI - This project is licensed under the terms of the [MIT license](https://fastapi.tiangolo.com/#license)

Vue.js - The Progressive JavaScript Framework is released under the [MIT license](https://opensource.org/licenses/MIT).