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
from interfaces import Classifier


class OllamaClassifier(Classifier):
    def __init__(self, api): self.api = api

    async def classify(self, xml_clean, mode): return await self.api.classify(xml_clean, mode)


class MockClassifier(Classifier):
    async def classify(self, xml_clean, mode):
        return {"id": "mock", "categoria": "teste", "justificativa": "mock", "origem": mode, "status": "sugerido"}


class ClassifierFactory:
    @staticmethod
    def create(mode: str, api) -> Classifier:
        return MockClassifier() if mode == "mock" else OllamaClassifier(api)
