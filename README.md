## NFERC - Classificador de despesas a partir de Nota Fiscais Eletrônicas com IA generativa (LLM).  $${\color{red}[in \space progress]}$$

**NFERC - _Nota Fiscal Eletrônica Receipt Classifier_** é um sistema que automatiza a classificação de despesas a partir de
arquivos XML de NF-e (Notas Fiscais Eletrônicas) usando IA generativa (LLMs - Large Language Models).

O projeto é implementado em Python e Vuejs, **rodando localmente com Docker e sem depender de cloud**. Todas as
dependências rodam em ambiente de desenvolvimento.

Em resumo o sistema faz o seguinte processo:

> **Python extrai XML → FastAPI envia para LLaMA 2 → LLaMA 2 sugere categoria com justificativa → Python grava no
PostgreSQL com status "sugerido" → Usuário valida no frontend Vuejs**

---

Profissionais da área contábil / administrativa muitas vezes passam horas classificando a mesmas despesas para
diferentes clientes.

O **NFERC** lê o XML da NF-e, consulta o plano de contas e sugere a _categoria_ com _justificativa_ auditável. O
profissional apenas valida aprovando ou rejeitando a despesa.

**Diferencial:** roda 100% em Docker na sua máquina com LLaMA 2 via Ollama.

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

### Pré-requisitos

## URLs principais

#### Backend: http://localhost:8000/

#### Frontend: http://localhost:5173/

#### Swagger docs da API: http://localhost:8000/docs

#### Ollama: http://localhost:11434

@TODO

### Estrutura de arquivos e permissões

@TODO

### Importador de NFe nfe_importer.py

@TODO

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

@TODO

FastAPI - This project is licensed under the terms of the [MIT license](https://fastapi.tiangolo.com/#license)
Vue.js - The Progressive JavaScript Framework is released under the [MIT license](https://opensource.org/licenses/MIT).