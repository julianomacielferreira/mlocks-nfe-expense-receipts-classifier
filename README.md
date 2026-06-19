## Classificador com IA generativa para despesas a partir de Nota Fiscais Eletrônicas.  $${\color{red}[in \space progress]}$$

> **Python extrai XML → FastAPI envia para LLaMA 2 → LLaMA 2 sugere categoria com justificativa → Python grava no PostgreSQL com status "sugerido" → Contador valida no Vue**

Um sistema local-first para automatizar a classificação contábil de NF-e usando IA generativa, sem depender da nuvem em desenvolvimento.

---

## 🎯 Por que existe

Contadores perdem horas classificando a mesma despesa de hospedagem, software ou material de escritório. Este classificador lê o XML da NF-e, consulta o plano de contas e sugere a categoria com justificativa auditável. O contador apenas valida — não digita.

**Diferencial:** roda 100% em Docker na sua máquina com LLaMA 2 via Ollama. Quando quiser escalar, troca uma variável e aponta para Vertex AI.

## 🏗️ Arquitetura

```
[Docker Compose na sua máquina]
  ├─ fastapi (Python 3.11) → chama llama AI
  ├─ postgres:15
  └─ vue-dev (frontend)
```