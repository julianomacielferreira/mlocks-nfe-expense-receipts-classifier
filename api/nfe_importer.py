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

"""
nfe_importer.py - Classificador em batch de NF-e

Lê todos os .xml de uma pasta e envia para /classificar
Gera CSV com o resultado para auditoria

Uso:
    python api/nfe_importer.py ./nfe_files/ --mode ollama --workers 10
"""
import argparse
import asyncio
import csv
import time
from pathlib import Path
from datetime import datetime

import httpx
from lxml import etree

# Setup ENVs
API_URL = "http://localhost:8000/classificar"
TIMEOUT = 120  # LLaMa 2 pode demorar


def extrai_preview(xml_str: str) -> dict:
    """Extrai valor e descrição sem depender da API"""
    try:
        root = etree.fromstring(xml_str.encode())
        ns = {"nfe_files": "http://www.portalfiscal.inf.br/nfe"}
        valor = root.xpath("string(//nfe_files:vNF)", namespaces=ns) or "0"
        descricao = root.xpath("string(//nfe_files:xProd)", namespaces=ns) or ""

        return {"valor": valor, "descricao": descricao[:80]}
    except:
        return {"valor": 0, "descricao": "ERROR_PARSE"}


async def classifica_arquivo(client: httpx.AsyncClient, file: Path, mode: str, semaphore: asyncio.Semaphore):
    """Envia um XML para a API"""
    async with semaphore:  # controla concorrência
        try:
            xml_content = file.read_text(encoding="utf-8", errors="ignore")

            # Remove quebras para JSON limpo
            xml_clean = " ".join(xml_content.split())

            preview = extrai_preview(xml_content)

            payload = {
                "xml_nfe": xml_clean,
                "mode": mode
            }

            start = time.time()

            response = await client.post(API_URL, json=payload, timeout=TIMEOUT)

            elapsed = round(time.time() - start, 2)

            if response.status_code == 200:
                data = response.json()

                return {
                    "arquivo": file.name,
                    "id": data.get("id"),
                    "categoria": data.get("categoria"),
                    "justificativa": data.get("justificativa"),
                    "origem": data.get("origem"),
                    "status": data.get("status"),
                    "valor_xml": preview["valor"],
                    "descricao_xml": preview["descricao"],
                    "tempo_seg": elapsed,
                    "erro": ""
                }
            else:
                return {
                    "arquivo": file.name,
                    "id": "",
                    "categoria": "",
                    "justificativa": "",
                    "origem": mode,
                    "status": "erro_http",
                    "valor_xml": preview["valor"],
                    "descricao_xml": preview["descricao"],
                    "tempo_seg": elapsed,
                    "erro": f"HTTP {response.status_code}: {response.text[:100]}"
                }
        except Exception as e:
            return {
                "arquivo": file.name,
                "id": "",
                "categoria": "",
                "justificativa": "",
                "origem": mode,
                "status": "erro",
                "valor_xml": "",
                "descricao_xml": "",
                "tempo_seg": 0,
                "erro": str(e)[:200]
            }


async def main():
    parser = argparse.ArgumentParser(description="Classifica NF-e em batch")
    parser.add_argument("dir", help="Diretório com arquivos .xml")
    parser.add_argument("--mode", default="ollama", choices=["mock", "ollama", "auto"], help="Modo da IA")
    parser.add_argument("--workers", type=int, default=5, help="Requisições paralelas (cuidado com RAM)")
    args = parser.parse_args()

    directory = Path(args.dir)
    files = sorted(directory.glob("*.xml"))

    if not files:
        print(f"Nenhum arquivo .xml encontrado em {directory}")
        return

    print(f"Encontrados {len(files)} XMLs")
    print(f"Modo: {args.mode} | Workers: {args.workers}")
    print(f"Iniciando...")

    semaphore = asyncio.Semaphore(args.workers)
    results = []

    async with httpx.AsyncClient() as client:
        tasks = [classifica_arquivo(client, file, args.mode, semaphore) for file in files]

        for i, request in enumerate(asyncio.as_completed(tasks), 1):
            result = await request
            results.append(result)

            status_icon = "✅" if result["status"] == "sugerido" else "❌"
            print(f"{status_icon} [{i}/{len(files)}] {result['arquivo']} -> {result['categoria']}")

    # Gera CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    csv_path = directory / f"resultado_classificacao_{timestamp}.csv"

    fields = [
        "arquivo",
        "id",
        "categoria",
        "justificativa",
        "origem",
        "status",
        "valor_xml",
        "descricao_xml",
        "tempo_seg",
        "erro"
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    # Resumo
    ok = sum(1 for r in results if r["status"] == "sugerido")
    errors = len(results) - ok
    total_time = sum(r["tempo_seg"] for r in results)

    print(f"\nRESUMO")
    print(f"Sucesso: {ok}")
    print(f"Erros: {errors}")
    print(f"Tempo total: {total_time:.1f}s (média {total_time / len(results):.1f}s)")
    print(f"CSV salvo em: {csv_path}")


if __name__ == "__main__":
    asyncio.run(main())
