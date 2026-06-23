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
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from domain.entities import Classificacao


def create(db: Session, data: dict) -> Classificacao:
    """Creates a new classification record in the database."""
    db_obj = Classificacao(**data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_by_id(db: Session, record_id: int) -> Optional[Classificacao]:
    """Fetches a single classification by its ID."""
    return db.query(Classificacao).get(record_id)


def list_all(
        db: Session, status: Optional[str], offset: int, limit: int
) -> Tuple[List[Classificacao], int]:
    """Returns a list of classifications and the total count for pagination."""
    query = db.query(Classificacao)

    if status:
        query = query.filter(Classificacao.status == status)

    total = query.count()
    items = query.order_by(Classificacao.id.desc()).offset(offset).limit(limit).all()

    return items, total


def update_status(db: Session, db_obj: Classificacao, new_status: str) -> Classificacao:
    """Updates the status of an existing classification."""
    db_obj.status = new_status
    db.commit()
    db.refresh(db_obj)
    return db_obj
