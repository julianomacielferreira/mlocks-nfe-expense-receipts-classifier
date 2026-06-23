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
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, text
from sqlalchemy.orm import declarative_base

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
