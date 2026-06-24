"""
The MIT License

Copyright 2026 Juliano Maciel.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import hashlib
from typing import Optional
from sqlalchemy.orm import Session

from util.xml_parser import extract_xml_data
from ai.classifiers.rag_classifier import classify_expense
from ai.chunker.text_chunker import chunk_text
from ai.retriever.vector_store import upsert_vectors
from repositories import classification_repo


async def process_new_nfe(xml_nfe: str, mode: str, db: Session):
    # 1. Parse XML
    dados = extract_xml_data(xml_nfe)

    # 2. AI Classification
    result = await classify_expense(dados)

    # 3. Save to PostgreSQL via Repository
    record_data = {
        "xml_hash": hashlib.sha256(xml_nfe.encode()).hexdigest(),
        "categoria": result["categoria"],
        "justificativa": result["justificativa"],
        "origem": mode,
        "valor": dados["valor"],
        "descricao": dados["descricao"],
    }

    reg = classification_repo.create(db, record_data)

    return {**result, "id": reg.id, "origem": mode, "status": "sugerido"}


def list_classifications(db: Session, status: Optional[str], page: int, limit: int):
    offset = (page - 1) * limit

    # Fetch from Repository
    items, total = classification_repo.list_all(db, status, offset, limit)

    return {
        "items": [
            {
                "id": i.id,
                "categoria": i.categoria,
                "justificativa": i.justificativa,
                "origem": i.origem,
                "status": i.status,
                "valor": i.valor,
                "descricao": i.descricao,
                "criado_em": i.criado_em.isoformat() if i.criado_em else None,
            }
            for i in items
        ],
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
    }


def approve_classification(id: int, db: Session) -> bool:
    # Fetch from Repository
    classification = classification_repo.get_by_id(db, id)

    if not classification:
        return False

    # Update via Repository
    classification_repo.update_status(db, classification, "aprovado")

    # --- RAG INGESTION ---
    try:
        text_to_vectorize = f"Produto: {classification.descricao}. Justificativa: {classification.justificativa}"
        chunks = chunk_text(text_to_vectorize)

        upsert_vectors(
            chunks,
            metadata={
                "id_banco": classification.id,
                "descricao": classification.descricao,
                "categoria": classification.categoria,
            },
        )
    except Exception as ex:
        print(f"Error trying to save in Qdrant: {ex}")

    return True


def reject_classification(id: int, db: Session) -> bool:
    # Fetch from Repository
    classification = classification_repo.get_by_id(db, id)

    if not classification:
        return False

    # Update via Repository
    classification_repo.update_status(db, classification, "rejeitado")

    return True
