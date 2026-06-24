## NFERC - Classificador de despesas a partir de Nota Fiscais Eletrônicas com IA generativa (LLM).

**NFERC - _Nota Fiscal Eletrônica Receipt Classifier_** é um sistema que automatiza a classificação de despesas a partir
de
arquivos XML de NF-e (Notas Fiscais Eletrônicas) usando **IA generativa (LLMs - Large Language Models)**.
O **NFERC** lê o XML da NF-e, consulta o LLaMA 2 que sugere a _categoria_ com _justificativa_ para a despesa.

O projeto é implementado em Python e Vuejs, **rodando localmente com Docker e sem depender de cloud**. Todas as
dependências rodam em **ambiente de desenvolvimento**.

---

**Diferencial:** roda 100% em Docker na sua máquina com LLaMA 2 via **Ollama**.

![NFERC](mlocks-nferc-logo.png)

## Como inicializar o Projeto

Siga os passos abaixo para configurar e executar o ambiente completo da aplicação utilizando Docker.

### Pré-requisitos

Antes de iniciar, certifique-se de possuir os seguintes softwares instalados em sua máquina:

- _Docker 24+_
- _Docker Compose v2+_
- _Git_

Opcionalmente, para executar scripts Python localmente (fora do Docker):

- _Python 3.11+_
- _pip_

### Clonando o repositório

```bash
$ git clone https://github.com/julianomacielferreira/mlocks-nfe-expense-receipts-classifier.git
```

```bash
$ cd mlocks-nfe-expense-receipts-classifier
```

### Configuração do arquivo `.env`

O projeto utiliza variáveis de ambiente para configuração dos serviços.

Renomeie o arquivo [.env.example](https://github.com/julianomacielferreira/mlocks-nfe-expense-receipts-classifier/blob/main/.env.example) em `.env.example` para `.env`.

```bash
$ cp .env.example .env
```

ou, se preferir:

```bash
$ mv .env.example .env
```

Em seguida, ajuste as variáveis conforme necessário no arquivo `.env`.

Exemplo:

```
ENV=development
MODE=ollama
PROJECT_ID=mlocks-nferc
API_PORT=8000
POSTGRES_DB=mlocks_nferc_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=qwerty
POSTGRES_PORT=5432
DATABASE_URL=postgresql://postgres:qwerty@database:5432/mlocks_nferc_db
OLLAMA_PORT=11434
OLLAMA_URL=http://ollama:11434
LLM_MODEL=gemma2:2b
QDRANT_URL=http://qdrant:
FRONTEND_PORT=5173
LOG_LEVEL=INFO
```

### Construindo os containers

Execute os seguintes comandos para fazer o build, subir seus containers e fazer o download do modelo no ollama (LLM
local):

```bash
$ docker-compose build --no-cache
```

```bash
$ docker-compose up
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

### Verificando os containers

Confira se todos os serviços estão em execução:

```bash
$ docker ps
```

## Baixando outros modelos da IA

Na primeira execução é necessário instalar o modelo utilizado pelo Ollama.

Exemplo:

```bash
$ docker exec -it mlocks-nferc-ollama ollama pull llama3.1:8b
```

ou

```bash
$ docker exec -it mlocks-nferc-ollama ollama pull gemma2:2b
```

Você pode utilizar qualquer modelo compatível configurando posteriormente a variável correspondente no arquivo
`api/.env`.

```
LLM_MODEL=gemma2:2b
```

### Verificando a API

Acesse: http://localhost:8000/health

Resposta esperada:

```json
{
  "status": "UP",
  "architecture": "Layered RAG"
}
```

### Acessando a aplicação

Após a inicialização, os serviços estarão disponíveis em:

| Serviço  | URL                        |
|----------|----------------------------|
| Frontend | http://localhost:8080      |
| API      | http://localhost:8000      |
| Swagger  | http://localhost:8000/docs |
| Ollama   | http://localhost:11434     |

## Encerrando a aplicação

```bash
$ docker-compose down
```

Para remover os volumes persistentes:

```bash
docker-compose down -v
```

### Estrutura dos containers

O ambiente é composto pelos seguintes serviços:

| Serviço          | Responsabilidade                |
| ---------------- | ------------------------------- |
| Frontend (Nginx) | Interface Web                   |
| FastAPI          | API REST e orquestração da IA   |
| PostgreSQL       | Persistência das classificações |
| Ollama           | Inferência dos modelos LLM      |
| Qdrant           | Banco vetorial para RAG         |

### Desenvolvimento

Durante o desenvolvimento, o backend é iniciado utilizando Hot Reload do Uvicorn.

Qualquer alteração no código Python será automaticamente recarregada, sem necessidade de reconstruir os containers.

Caso novas dependências sejam adicionadas ao `api/requirements.txt`, execute novamente:

```bash
$ docker-compose build api
```

### Estrutura de arquivos do Projeto

O projeto segue uma arquitetura em camadas: API → RAG → LLM → Qdrant → PostgreSQL

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
├── docker-compose.yml
├── .env.example
├── frontend
│   └── index.html
├── .gitignore
├── LICENSE
├── MLocks-NERC-NFe-Expense-Receipt-Classifier.postman_collection.json
├── mlocks-nferc-database.png
├── mlocks-nferc-logo.png
├── mlocks-nferc-swagger-docs.png
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

21 directories, 45 files
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

Para utilizar outros modelos você pode consultar o catálogo da biblioteca em [OLlama Library](https://ollama.com/library).

Depois basta alterar o arquivo `.env` modificando a variável `LLM_MODEL`.

Exemplo:

```
LLM_MODEL=deepseek-r1
```

## Banco de Dados

O banco de dados contém uma única tabela. O script para criação está em `scripts/init_db.sql`.

![NFERC Database](mlocks-nferc-database.png)

## Swagger Docs

Para acessar documentação Swagger basta acessar http://localhost:8000/docs.

![Swagger Docs](mlocks-nferc-swagger-docs.png)

## Endpoints

Uma coleção de endpoints do Postman está localizada no arquivo [MLocks-NERC-NFe-Expense-Receipt-Classifier.postman_collection.json](./MLocks-NERC-NFe-Expense-Receipt-Classifier.postman_collection.json) e abaixo estão exemplos de chamadas cURL para os endpoints.

### Classificar (POST):

- **/classificar**

Exemplo:

```bash
$ curl --location --request POST 'http://localhost:8000/classificar' \
--header 'Content-Type: application/json' \
--data '{
    "xml_nfe": "<nfeProc xmlns=\"http://www.portalfiscal.inf.br/nfe\"><NFe><infNFe><det><prod><xProd>CONSULTORIA CONTABIL MENSAL</xProd></prod></det><total><ICMSTot><vNF>1500.00</vNF></ICMSTot></total></infNFe></NFe></nfeProc>",
    "modo": "ollama"
}'
```

<details>
<summary><b>Resposta</b></summary>

```json
{
    "id": 174,
    "categoria": "Manutenção de Equipamentos",
    "justificativa": "O histórico de despesas aponta para a categoria Manutenção de Equipamentos, sendo que o valor da nota atual se refere à consulta contábil mensal. A classificação é justificada pela natureza das operações realizadas.",
    "origem": "auto",
    "status": "sugerido"
}
```

</details>

---

### Aprovar por id (POST):

- **/classificacoes/{{id}}/aprovar**

Exemplo:

```bash
$ curl --location --request POST 'http://localhost:8000/classificacoes/37/aprovar'
```

<details>
<summary><b>Resposta</b></summary>

```json
{
    "ok": true
}
```

</details>

---

### Rejeitar por id (POST):

- **/classificacoes/{{id}}/rejeitar**

Exemplo:

```bash
$ curl --location --request POST 'http://localhost:8000/classificacoes/8/rejeitar'
```

<details>
<summary><b>Resposta</b></summary>

```json
{
    "ok": true
}
```

</details>

---

### Listar aprovados (GET):

- **/classificacoes?status=aprovado**

Exemplo:

```bash
$ curl --location 'http://localhost:8000/classificacoes?status=aprovado'
```

<details>
<summary><b>Resposta</b></summary>

```json
{
    "items": [
        {
            "id": 64,
            "categoria": "Manutenção de Equipamentos",
            "justificativa": "O histórico aprovado indica que o produto está relacionado à manutenção de equipamentos. A nota atual descreve o mesmo produto com o mesmo tamanho e especificações, indicando que a descrição é consistente com o histórico.",
            "origem": "ollama",
            "status": "aprovado",
            "valor": "70.00",
            "descricao": "RAIO INOX PTO, NIPLE, 2,0 X 283MM",
            "criado_em": "2026-06-23T00:38:36.490774"
        },
        {
            "id": 63,
            "categoria": "Manutenção e Reparos",
            "justificativa": "O histórico de despesas aprovadas indica repetições frequentes para o produto CONDUITE TEFLON PRETO 20M, corroborando a necessidade de manutenção e reparos em equipamentos.",
            "origem": "ollama",
            "status": "aprovado",
            "valor": "12.00",
            "descricao": "CONDUITE TEFLON PRETO 20M",
            "criado_em": "2026-06-23T00:38:17.271461"
        },
        {
            "id": 62,
            "categoria": "Manutenção de Equipamentos",
            "justificativa": "O histórico mostra que o produto é manuseado em manutenção de equipamentos. O registro da nota atual se assemelha ao histórico, com o mesmo nome do produto e descrição.",
            "origem": "ollama",
            "status": "aprovado",
            "valor": "53.99",
            "descricao": "MANOPLA ABSOLUTE HL-G247 VMO",
            "criado_em": "2026-06-23T00:37:52.030018"
        },
        {
            "id": 60,
            "categoria": "Despesas com Materiais de Equipamento",
            "justificativa": "A descrição do produto indica que a SAPATILHA MTB AVVA PRETO 40 AVVA é utilizada como material de equipamento para atividades de ciclismo.  Conforme o histórico aprovado, esta categoria se aplica a itens como este.",
            "origem": "ollama",
            "status": "aprovado",
            "valor": "234.00",
            "descricao": "SAPATILHA MTB AVVA PRETO 40 AVVA",
            "criado_em": "2026-06-23T00:37:07.223334"
        },
        {
            "id": 58,
            "categoria": "Manutenção de Equipamentos",
            "justificativa": "A descrição do produto mudou para 'RAIO INOX PTO, NIPLE, 2,0 X 290MM' que corresponde a uma categoria de manutenção de equipamentos. Apesar de ser um produto de manutenção, o histórico aponta que a solicitação é relacionada à manutenção de equipamentos, e não apenas de reparos.",
            "origem": "ollama",
            "status": "aprovado",
            "valor": "2.50",
            "descricao": "RAIO INOX PTO, NIPLE, 2,0 X 290MM",
            "criado_em": "2026-06-23T00:36:34.234381"
        },
        {
            "id": 56,
            "categoria": "Eletrônicos de entretenimento",
            "justificativa": "O produto é um headset gamer da marca Redragon, conhecido por oferecer alta qualidade em áudio para jogos.  A categoria se aplica pois ele é destinado a ser utilizado em atividades relacionadas ao entretenimento, especialmente em jogos.",
            "origem": "ollama",
            "status": "aprovado",
            "valor": "139.99",
            "descricao": "Headset Gamer Redragon Hylas, RGB, 7.1 Surround, Drivers de 50mm, USB, Preto, H371-RGB",
            "criado_em": "2026-06-23T00:35:51.415252"
        },
        {
            "id": 53,
            "categoria": "Despesas com Materiais de Equipamento",
            "justificativa": "Os pedidos de equipamentos são constantes e justificam a inclusão da categoria Despesas com Materiais de Equipamento.",
            "origem": "ollama",
            "status": "aprovado",
            "valor": "367.00",
            "descricao": "SELIM MTB STRATUS PTO GTA",
            "criado_em": "2026-06-23T00:35:23.900363"
        },
        {
            "id": 52,
            "categoria": "Transporte",
            "justificativa": "O histórico sugere que o produto é uma bicicleta, que se encaixa na categoria de transporte, e a nota atual mantém essa classificação, considerando a descrição e valor do item.",
            "origem": "ollama",
            "status": "aprovado",
            "valor": "3800.00",
            "descricao": "BICICLETA CALOI EXPLORER EXPERT PTO TAM: M (17)",
            "criado_em": "2026-06-23T00:35:14.336918"
        },
        {
            "id": 51,
            "categoria": "Manutenção de Equipamentos",
            "justificativa": "O histórico aponta a necessidade de manutenção de equipamentos como justificativa para o gasto, especificando o modelo de equipamento 'MOV CENTRAL PFIT 41, KL 102 A VERMELHO'. O valor da compra se encaixa nessa categoria de acordo com o histórico aprovado.",
            "origem": "ollama",
            "status": "aprovado",
            "valor": "139.00",
            "descricao": "MOV CENTRAL PFIT 41, KL 102 A VERMELHO",
            "criado_em": "2026-06-23T00:35:03.817298"
        },
        {
            "id": 50,
            "categoria": "Material de Construção",
            "justificativa": "O histórico de compra demonstra a regularidade da categoria 'Material de Construção' para o produto MDF EUCATEX BRANCO 03MM COM TX 275X185 T-HDF 1FC BIANCO PRIME 1 FC SELADOR.",
            "origem": "ollama",
            "status": "aprovado",
            "valor": "115.80",
            "descricao": "MDF EUCATEX BRANCO 03MM COM TX 275X185 T-HDF 1FC BIANCO PRIME 1 FC SELADOR",
            "criado_em": "2026-06-23T00:34:49.938390"
        }
    ],
    "total": 49,
    "page": 1,
    "pages": 5
}
```

</details>

---

### Lista de classificações (GET):

- **/classificacoes?status=sugerido&page=1&limit=10**

Exemplo:

```bash
$ curl --location 'http://localhost:8000/classificacoes?status=sugerido&page=1&limit=10'
```

<details>
<summary><b>Resposta</b></summary>

```json
{
    "items": [
        {
            "id": 174,
            "categoria": "Manutenção de Equipamentos",
            "justificativa": "O histórico de despesas aponta para a categoria Manutenção de Equipamentos, sendo que o valor da nota atual se refere à consulta contábil mensal. A classificação é justificada pela natureza das operações realizadas.",
            "origem": "auto",
            "status": "sugerido",
            "valor": "1500.00",
            "descricao": "CONSULTORIA CONTABIL MENSAL",
            "criado_em": "2026-06-23T20:46:12.662170"
        },
        {
            "id": 173,
            "categoria": "Material de Construção",
            "justificativa": "O histórico de compra apresenta o mesmo produto, com descrição e valores constantes. O pedido se encaixa na categoria Material de Construção.",
            "origem": "ollama",
            "status": "sugerido",
            "valor": "115.80",
            "descricao": "MDF EUCATEX BRANCO 03MM COM TX 275X185 T-HDF 1FC BIANCO PRIME 1 FC SELADOR",
            "criado_em": "2026-06-23T19:24:32.261375"
        },
        {
            "id": 172,
            "categoria": "Transporte",
            "justificativa": "O histórico de compras demonstra a compra de Bicicletas Redstone Chroma, categorizando-as como transporte. O valor da compra é consistente com esse tipo de item e sua descrição, confirmando que as despesas são relacionadas ao transporte.",
            "origem": "ollama",
            "status": "sugerido",
            "valor": "2500.00",
            "descricao": "BICICLETA REDSTONE CHROMA",
            "criado_em": "2026-06-23T19:24:22.374232"
        },
        {
            "id": 171,
            "categoria": "Manutenção de Equipamentos",
            "justificativa": "O histórico indica que o produto é classificado como Manutenção e Reparos, mas também em Manutenção de Equipamentos. A categoria 'Manutenção de Equipamentos' se encaixa melhor, pois a descrição do produto (RAIO INOX PTO, NIPLE, 2,0 X 283MM) indica que o item está sendo utilizado para manutenção de equipamentos, sem especificações sobre reparos.",
            "origem": "ollama",
            "status": "sugerido",
            "valor": "70.00",
            "descricao": "RAIO INOX PTO, NIPLE, 2,0 X 283MM",
            "criado_em": "2026-06-23T19:24:14.460872"
        },
        {
            "id": 170,
            "categoria": "Manutenção e Reparos",
            "justificativa": "O pedido se enquadra na categoria de Manutenção e Reparos pois o item, CONDUITE TEFLON PRETO 20M,  é destinado a realizar reparos ou manutenção em equipamentos, como por exemplo veículos. A utilização do material para esse fim é justificada pela necessidade da manutenção.",
            "origem": "ollama",
            "status": "sugerido",
            "valor": "12.00",
            "descricao": "CONDUITE TEFLON PRETO 20M",
            "criado_em": "2026-06-23T19:23:59.310602"
        },
        {
            "id": 169,
            "categoria": "Transporte",
            "justificativa": "A bicicleta Redstone Chroma foi comprada para transporte pessoal e não se enquadra na categoria de material de construção, como o MDF Eucatex Branco. O valor zero indica que a compra é apenas para uso pessoal e não representa despesas para o negócio.",
            "origem": "ollama",
            "status": "sugerido",
            "valor": "0",
            "descricao": "",
            "criado_em": "2026-06-23T19:23:47.433683"
        },
        {
            "id": 168,
            "categoria": "Manutenção de Equipamentos",
            "justificativa": "O histórico aponta a categoria 'Manutenção de Equipamentos' como padrão para o produto 'MOV CENTRO PFIT, ABSOLUTE-102A, 24MM, PT'. A descrição detalha a natureza da compra, confirmando a categorização.",
            "origem": "ollama",
            "status": "sugerido",
            "valor": "124.00",
            "descricao": "MOV CENTRO PFIT, ABSOLUTE-102A, 24MM, PT",
            "criado_em": "2026-06-23T19:23:36.379461"
        },
        {
            "id": 167,
            "categoria": "Despesas com Equipamento",
            "justificativa": "O histórico de despesas indica que o produto é classificado como 'Equipamento' e, considerando a descrição da nota atual, a compra se refere a um equipamento para ciclismo. Portanto, a categoria correta é Despesas com Equipamento.",
            "origem": "ollama",
            "status": "sugerido",
            "valor": "234.00",
            "descricao": "SAPATILHA MTB AVVA PRETO 40 AVVA",
            "criado_em": "2026-06-23T19:23:23.905234"
        },
        {
            "id": 166,
            "categoria": "Manutenção de Equipamentos",
            "justificativa": "O histórico mostra que o produto é utilizado para manutenção de equipamentos, com especificações semelhantes às do pedido atual. Ajuste na descrição para maior clareza.",
            "origem": "ollama",
            "status": "sugerido",
            "valor": "2.50",
            "descricao": "RAIO INOX PTO, NIPLE, 2,0 X 290MM",
            "criado_em": "2026-06-23T19:23:11.987050"
        },
        {
            "id": 165,
            "categoria": "Eletrônicos de entretenimento",
            "justificativa": "O produto é um headset gamer, sendo classificado como eletrônicos de entretenimento, considerando a natureza do seu uso (jogos) e a categoria da venda (eletrônicos).",
            "origem": "ollama",
            "status": "sugerido",
            "valor": "139.99",
            "descricao": "Headset Gamer Redragon Hylas, RGB, 7.1 Surround, Drivers de 50mm, USB, Preto, H371-RGB",
            "criado_em": "2026-06-23T19:23:01.592951"
        }
    ],
    "total": 110,
    "page": 1,
    "pages": 11
}
```

</details>

---

## Referências

OLLama Library - [library](https://ollama.com/library)

Llama LLM - [Llama](https://developer.meta.com/ai/docs/overview/)

Qdrant - [High-Performance Vector Search](https://qdrant.tech/)

freeCodeCamp YouTube Channel - [Ollama Course – Build AI Apps Locally](https://www.youtube.com/watch?v=GWB9ApTPTv4)

Docker: Accelerated Container Application Development - [Docker](https://docs.docker.com/install/)

Docker Compose is a tool for defining and running multi-container
applications - [Docker Compose](https://docs.docker.com/compose/install/)

Git is a free and open source distributed version control system - [Git](https://git-scm.com/)

## License

FastAPI - This project is licensed under the terms of the [MIT license](https://fastapi.tiangolo.com/#license)

Vue.js - The Progressive JavaScript Framework is released under the [MIT license](https://opensource.org/licenses/MIT).