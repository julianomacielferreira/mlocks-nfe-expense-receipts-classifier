## Classificador com IA generativa para despesas a partir de Nota Fiscais Eletrônicas.  $${\color{red}[in \space progress]}$$

NFERC - _Nota Fiscal Eletrônica Receipt Classifier_ é um sistema que automatiza a classificação de despesas a partir de arquivos XML de NF-e (Notas Fiscais Eletrônicas) usando IA generativa (LLMs - Large Language Models).

O projeto é implementado em Python e Vuejs, **rodando localmente com Docker e sem depender de cloud**. Todas as dependências rodam em ambiente de desenvolvimento.

Em resumo o kernel do sistema faz o seguinte:

> **Python extrai XML → FastAPI envia para LLaMA 2 → LLaMA 2 sugere categoria com justificativa → Python grava no PostgreSQL com status "sugerido" → Usuário valida no frontend Vuejs**

---

Profissionais da área contábil / administrativa muitas vezes passam horas classificando a mesmas despesas para diferentes clientes. 

O **NFERC** lê o XML da NF-e, consulta o plano de contas e sugere a _categoria_ com _justificativa_ auditável. O profissional apenas valida aprovando ou rejeitando a despesa.

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

@TODO

### Diretórios e permissões

@TODO

### Modelos do Ollama e como utilizá-los

@TODO

## Testes

@TODO

## Endpoints

@TODO

## Referências

@TODO

## Licença

@TODO