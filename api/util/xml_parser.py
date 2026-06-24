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

from lxml import etree
from fastapi import HTTPException


def extract_xml_data(xml_str: str) -> dict:
    try:
        root = etree.fromstring(xml_str.encode())
        ns = {"nfe_files": "http://www.portalfiscal.inf.br/nfe"}
        valor = root.xpath("string(//nfe_files:vNF)", namespaces=ns) or "0"
        descricao = root.xpath("string(//nfe_files:xProd)", namespaces=ns) or ""

        return {"valor": valor, "descricao": descricao}

    except Exception as e:
        raise HTTPException(400, f"XML invalid: {e}")
