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
import json
import hashlib
import httpx
import uuid
import logging

from datetime import datetime
from typing import Literal, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from langchain_community.embeddings import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client.models import PointStruct
from lxml import etree

logger = logging.getLogger(__name__)

ENV = os.getenv("ENV", "development")
MODE = os.getenv("MODE", "ollama")
PROJECT_ID = os.getenv("PROJECT_ID")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:qwerty@database:5432/mlocks_nferc_db")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
COLLECTION_NAME = "nferc_classificacoes"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

qdrant_client = QdrantClient(url=QDRANT_URL)
embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_URL)

try:
    if not qdrant_client.collection_exists(COLLECTION_NAME):
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),  # nomic-embed-text uses 768 dimensions
        )
except Exception as e:
    print(f"Warning: Could not initialize Qdrant collection: {e}")


class Classificacao(Base):
    __tablename__ = "classificacoes"
    id = Column(Integer, primary_key=True)
    xml_hash = Column(String(64))
    categoria = Column(String(100))
    justificativa = Column(Text)
    origem = Column(String(20))
    status = Column(String(20), default="sugerido")
    valor = Column(String(20))
    descricao = Column(String(200))
    criado_em = Column(DateTime(), default=datetime.utcnow)
    atualizado_em = Column(DateTime())


Base.metadata.create_all(engine)

app = FastAPI(title="NFERC - Classificador de despesas a partir de Nota Fiscais Eletrônicas com IA generativa (LLM).")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class ClassificarRequest(BaseModel):
    xml_nfe: str
    mode: Literal["auto", "mock", "ollama"] = "auto"


class ClassificarResponse(BaseModel):
    id: int
    categoria: str
    justificativa: str
    origem: str
    status: str


def extract_xml_data(xml_str: str) -> dict:
    try:
        root = etree.fromstring(xml_str.encode())
        ns = {"nfe_files": "http://www.portalfiscal.inf.br/nfe"}
        valor = root.xpath("string(//nfe_files:vNF)", namespaces=ns) or "0"
        descricao = root.xpath("string(//nfe_files:xProd)", namespaces=ns) or ""

        return {"valor": valor, "descricao": descricao}

    except Exception as e:
        raise HTTPException(400, f"XML invalid: {e}")


async def get_rag_context(descricao: str, limit: int = 3) -> str:
    try:

        query_vector = embeddings.embed_query(descricao)

        search_result = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=limit
        )

        if not search_result:
            return "Nenhum histórico similar encontrado."

        context_parts = []
        for hit in search_result:
            payload = hit.payload
            context_parts.append(
                f"- Produto: {payload.get('descricao')} | Categoria Aprovada: {payload.get('categoria')}"
            )

        return "\n".join(context_parts)
    except Exception as ex:
        print(f"Error trying to search context on Qdrant: {ex}")
        return "Error when recovering historical context."


async def mock_classifier(dados):
    return {"categoria": "6.2.01 - Desenvolvimento de Software", "justificativa": f"Mock valor R${dados['valor']}"}


async def ollama_classifier(dados: dict) -> dict:
    try:
        historical_context = await get_rag_context(dados["descricao"])
    except Exception:
        logger.exception("RAG failed")
        raise

    prompt = f"""
                Você é um classificador de despesas fiscais. Use o histórico de classificações anteriores como base para a sua decisão.            
                [HISTÓRICO DE DESPESAS SIMILARES APROVADAS]
                {historical_context}
                
                [DADOS DA NOTA ATUAL]
                Descrição: {dados["descricao"]}
                Valor: {dados["valor"]}
                
                Responda APENAS um JSON válido.
                Formato obrigatório:
                {{
                  "categoria": "...",
                  "justificativa": "..."
                }}
                """
    try:
        timeout = httpx.Timeout(
            connect=10,
            read=300,
            write=30,
            pool=30,
        )

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": "gemma2:2b",
                    "prompt": prompt,
                    "stream": False,
                    "format": {
                        "type": "object",
                        "properties": {
                            "categoria": {"type": "string"},
                            "justificativa": {"type": "string"}
                        },
                        "required": ["categoria", "justificativa"]
                    }
                }
            )
    except Exception:
        logger.exception("HTTP request to Ollama failed")
        raise

    response.raise_for_status()

    try:
        body = response.json()
    except Exception:
        logger.exception("Invalid HTTP JSON")
        raise

    try:
        result = json.loads(body["response"])

        if not isinstance(result, dict):
            raise ValueError("Response is not a JSON object")

        if "categoria" not in result or "justificativa" not in result:
            raise ValueError(f"JSON invalid: {result}")
    except Exception:
        logger.exception("LLM JSON parsing failed")
        raise

    return result


@app.post("/classificar", response_model=ClassificarResponse)
async def classify(req: ClassificarRequest):
    dados = extract_xml_data(req.xml_nfe)

    mode = req.mode if req.mode != "auto" else MODE

    if mode == "local": mode = "mock"

    classifier = {
        "mock": mock_classifier,
        "ollama": ollama_classifier,
    }.get(mode)

    if classifier is None:
        raise HTTPException(
            400,
            "Invalid mode"
        )

    result = await classifier(dados)

    if "categoria" not in result or "justificativa" not in result:
        raise HTTPException(
            500,
            f"Ollama returned invalid JSON: {result}"
        )

    db = SessionLocal()

    try:
        reg = Classificacao(
            xml_hash=hashlib.sha256(
                req.xml_nfe.encode()
            ).hexdigest(),
            categoria=result["categoria"],
            justificativa=result["justificativa"],
            origem=mode,
            valor=dados["valor"],
            descricao=dados["descricao"]
        )

        db.add(reg)
        db.commit()
        db.refresh(reg)
    finally:
        db.close()

    return {**result, "id": reg.id, "origem": mode, "status": "sugerido"}


@app.get("/classificacoes")
def list_classifications(status: Optional[str] = None, page: int = Query(1, ge=1), limit: int = Query(10, le=100)):
    db = SessionLocal()

    query = db.query(Classificacao)

    if status:
        query = query.filter(Classificacao.status == status)

    total = query.count()

    items = query.order_by(Classificacao.id.desc()).offset((page - 1) * limit).limit(limit).all()

    db.close()

    return {"items": [{"id": i.id,
                       "categoria": i.categoria,
                       "justificativa": i.justificativa,
                       "origem": i.origem,
                       "status": i.status,
                       "valor": i.valor,
                       "descricao": i.descricao,
                       "criado_em": i.criado_em.isoformat()} for i in items],
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit}


@app.post("/classificacoes/{id}/aprovar")
def approve_classification(id: int):
    db = SessionLocal()
    classification = db.query(Classificacao).get(id)

    if not classification:
        raise HTTPException(404, "Not found")

    classification.status = "aprovado"

    db.commit()

    try:
        text_to_vectorize = f"Produto: {classification.descricao}. Justificativa: {classification.justificativa}"

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_text(text_to_vectorize)

        points = []
        for chunk in chunks:
            vector = embeddings.embed_query(chunk)
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "id_banco": classification.id,
                    "descricao": classification.descricao,
                    "categoria": classification.categoria,
                    "texto_chunk": chunk
                }
            ))

        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
    except Exception as ex:
        print(f"Error trying to save in Qdrant: {ex}")

    db.close()

    return {"ok": True}


@app.post("/classificacoes/{id}/rejeitar")
def reject_classification(id: int):
    db = SessionLocal()

    classification = db.query(Classificacao).get(id)

    if not classification:
        raise HTTPException(404, "Not found")

    classification.status = "rejeitado"

    db.commit()
    db.close()

    return {"ok": True}


@app.get("/health")
def health():
    db = SessionLocal()

    try:
        db.execute(text("SELECT 1"))
        database = "UP"
    except Exception as e:
        database = "DOWN"
    finally:
        db.close()

    return {
        "status": "UP",
        "database": database,
        "ollama": OLLAMA_URL,
        "mode": MODE,
        "environment": ENV
    }
