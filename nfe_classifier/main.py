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

import argparse, asyncio
from pathlib import Path
import httpx
from services.nfe_xml_extractor import NfeXMLExtractor
from services.api_client import HttpClassifier
from services.classifiers import ClassifierFactory
from classifiers import FileClassifier
from classifiers import BatchClassifier
from infrastructure.csv_reporter import CSVReporter
from infrastructure.file_repository import list_xml_files
from utils.execution_timer import ExecutionTimer

"""
main.py - Classificador em batch de NF-e

Lê todos os .xml de uma pasta e envia para /classificar
Gera CSV com o resultado para auditoria

Uso:
    python classifier/nfe_classifier/main.py ./nfe_files/ --mode ollama --workers 5
"""


async def main():
    p = argparse.ArgumentParser()
    p.add_argument("dir")
    p.add_argument("--mode", default="ollama", choices=["mock", "ollama", "auto"])
    p.add_argument("--workers", type=int, default=5)
    args = p.parse_args()

    directory = Path(args.dir)
    files = list_xml_files(directory)

    timer = ExecutionTimer()

    async with httpx.AsyncClient() as client:
        api = HttpClassifier(client)
        classifier = ClassifierFactory.create(args.mode, api)
        parser = NfeXMLExtractor()
        file_uc = FileClassifier(parser, classifier)
        batch_uc = BatchClassifier(file_uc, args.workers)

        with timer:
            results = await batch_uc.execute(files, args.mode)

    csv_path = CSVReporter().write(results, directory)
    print(f"\nCSV salvo em: {csv_path}")
    print(f"Tempo total: {timer.elapsed:.2f}s")  # ou timer.total, depende da sua classe
    print(f"Média por arquivo: {timer.elapsed / len(results):.2f}s")


if __name__ == "__main__":
    asyncio.run(main())
