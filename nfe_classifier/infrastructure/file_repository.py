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

from pathlib import Path


class FileSystemXmlRepository:
    def list_files(self, directory: Path) -> list[Path]:
        if not directory.exists():
            raise FileNotFoundError(f"Diretório não encontrado: {directory}")

        if not directory.is_dir():
            raise NotADirectoryError(f"{directory} não é uma pasta válida")

        files = sorted(p for p in directory.glob("*.xml") if p.is_file())

        return files


def list_xml_files(directory: Path) -> list[Path]:
    repo = FileSystemXmlRepository()
    files = repo.list_files(directory)

    if not files:
        print(f"Nenhum arquivo.xml encontrado em {directory}")
    else:
        print(f"Encontrados {len(files)} XMLs")

    return files
