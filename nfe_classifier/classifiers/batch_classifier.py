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
import asyncio
from pathlib import Path
from classifiers.file_classifier import FileClassifier


class BatchClassifier:
    def __init__(self, classifier: FileClassifier, workers: int):
        self.classifier = classifier
        self.semaphore = asyncio.Semaphore(workers)

    async def execute(self, files: list[Path], mode: str):
        async def with_limit(f):
            async with self.semaphore:
                return await self.classifier.execute(f, mode)

        tasks = [with_limit(f) for f in files]
        results = []
        for i, coro in enumerate(asyncio.as_completed(tasks), 1):
            res = await coro
            print(f"{'✅' if res.status == 'sugerido' else '❌'} [{i}/{len(files)}] {res.arquivo} -> {res.categoria}")
            results.append(res)
        return results
