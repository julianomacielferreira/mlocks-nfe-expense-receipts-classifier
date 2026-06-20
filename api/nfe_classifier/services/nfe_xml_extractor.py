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
from interfaces import XmlParser
from models import NFePreview


class NfeXMLExtractor(XmlParser):
    def extract_preview(self, xml_str: str) -> NFePreview:
        try:
            root = etree.fromstring(xml_str.encode())
            ns = {"nfe": "http://www.portalfiscal.inf.br/nfe"}
            valor = root.xpath("string(//nfe:vNF)", namespaces=ns) or "0"
            description = root.xpath("string(//nfe:xProd)", namespaces=ns) or ""

            return NFePreview(valor, description[:80])
        except Exception:
            return NFePreview("0", "ERROR_PARSE")
