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

import time
from pathlib import Path
from interfaces import XmlParser, Classifier
from models import ClassificationResult


class FileClassifier:
    def __init__(self, parser: XmlParser, classifier: Classifier):
        self.parser = parser
        self.classifier = classifier

    async def execute(self, file: Path, mode: str) -> ClassificationResult:
        xml = file.read_text(encoding="utf-8", errors="ignore")
        xml_clean = " ".join(xml.split())
        preview = self.parser.extract_preview(xml)

        start = time.time()

        try:
            response = await self.classifier.classify(xml_clean, mode)

            return ClassificationResult(
                arquivo=file.name,
                id=response.get("id", ""),
                categoria=response.get("categoria", ""),
                justificativa=response.get("justificativa", ""),
                origem=response.get("origem", mode),
                status=response.get("status", ""),
                valor_xml=preview.valor,
                descricao_xml=preview.descricao,
                tempo_seg=round(time.time() - start, 2),
            )
        except Exception as e:
            return ClassificationResult(
                arquivo=file.name,
                origem=mode,
                status="erro",
                valor_xml=preview.valor,
                descricao_xml=preview.descricao,
                tempo_seg=round(time.time() - start, 2),
                erro=str(e)[:200],
            )
