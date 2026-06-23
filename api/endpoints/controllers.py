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
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database.session import get_db
from domain.schemas import ClassificarRequest, ClassificarResponse
from util import classification_service

router = APIRouter()


@router.post("/classificar", response_model=ClassificarResponse)
async def classify(req: ClassificarRequest, db: Session = Depends(get_db)):
    try:
        return await classification_service.process_new_nfe(req.xml_nfe, req.mode, db)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.get("/classificacoes")
def list_classifications(
        status: Optional[str] = None,
        page: int = Query(1, ge=1),
        limit: int = Query(10, le=100),
        db: Session = Depends(get_db)  # Auto-manages session lifecycle
):
    return classification_service.list_classifications(db, status, page, limit)


@router.post("/classificacoes/{id}/aprovar")
def approve_classification(id: int, db: Session = Depends(get_db)):
    success = classification_service.approve_classification(id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}


@router.post("/classificacoes/{id}/rejeitar")
def reject_classification(id: int, db: Session = Depends(get_db)):
    success = classification_service.reject_classification(id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}
