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

from datetime import datetime
from typing import Literal, Optional

import hashlib
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker
from lxml import etree

ENV = os.getenv("ENV", "local")
PROJECT_ID = os.getenv("PROJECT_ID")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:qwerty@database:5432/mlocks_nferc_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


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
        ns = {"nfe": "http://www.portalfiscal.inf.br/nfe"}
        valor = root.xpath("string(//nfe:vNF)", namespaces=ns) or "0"
        descricao = root.xpath("string(//nfe:xProd)", namespaces=ns) or ""

        return {"valor": valor, "descricao": descricao}

    except Exception as e:
        raise HTTPException(400, f"XML inválido: {e}")


async def mock_classifier(dados):
    return {"categoria": "6.2.01 - Desenvolvimento de Software", "justificativa": f"Mock valor R${dados['valor']}"}


async def ollama_classifier(dados: dict) -> dict:
    prompt = f"""
                Você é um classificador de despesas fiscais.                
                Responda APENAS um JSON válido.                
                Formato obrigatório:                
                {{
                  "categoria": "...",
                  "justificativa": "..."
                }}                
                Descrição:
                {dados["descricao"]}                
                Valor:
                {dados["valor"]}
                """

    try:
        async with httpx.AsyncClient(timeout=60) as client:
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

            response.raise_for_status()

            body = response.json()
            result = json.loads(body["response"])

            if not isinstance(result, dict):
                raise ValueError("Resposta não é um objeto JSON")

            if "categoria" not in result or "justificativa" not in result:
                raise ValueError(f"JSON inválido: {result}")

            return result

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Erro ao classificar via Ollama: {e}"
        )


@app.post("/classificar", response_model=ClassificarResponse)
async def classify(req: ClassificarRequest):
    dados = extract_xml_data(req.xml_nfe)

    mode = req.mode if req.mode != "auto" else ENV

    if mode == "local": mode = "mock"

    classifier = {
        "mock": mock_classifier,
        "ollama": ollama_classifier,
    }.get(mode)

    if classifier is None:
        raise HTTPException(
            400,
            "Modo inválido"
        )

    result = await classifier(dados)

    if "categoria" not in result or "justificativa" not in result:
        raise HTTPException(
            500,
            f"Ollama retornou JSON inválido: {result}"
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
        raise HTTPException(404, "Não encontrado")

    classification.status = "aprovado"

    db.commit()
    db.close()

    return {"ok": True}


@app.post("/classificacoes/{id}/rejeitar")
def reject_classification(id: int):
    db = SessionLocal()

    classification = db.query(Classificacao).get(id)

    if not classification:
        raise HTTPException(404, "Não encontrado")

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
        "environment": ENV
    }
