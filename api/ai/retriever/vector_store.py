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

import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from ai.embeddings.provider import embeddings

QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
COLLECTION_NAME = "nferc_classificacoes"
qdrant_client = QdrantClient(url=QDRANT_URL)


async def search_similar_expenses(descricao: str, limit: int = 3) -> list:
    query_vector = embeddings.embed_query(descricao)
    results = qdrant_client.search(
        collection_name=COLLECTION_NAME, query_vector=query_vector, limit=limit
    )
    return results


def upsert_vectors(chunks: list, metadata: dict):
    points = []
    for chunk in chunks:
        vector = embeddings.embed_query(chunk)
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={**metadata, "texto_chunk": chunk},
            )
        )
    qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
