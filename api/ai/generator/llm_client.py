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

import os
import json
import httpx

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "gemma2:2b")


async def generate_json_response(prompt: str) -> dict:
    """
    Communicates with the local Ollama instance to generate a response
    based on the provided prompt, enforcing a strict JSON output schema.
    """
    payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": {
            "type": "object",
            "properties": {
                "categoria": {"type": "string"},
                "justificativa": {"type": "string"},
            },
            "required": ["categoria", "justificativa"],
        },
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{OLLAMA_URL}/api/generate", json=payload)

            # Raise an error if the HTTP request failed (e.g., 404, 500)
            response.raise_for_status()

            body = response.json()
            result = json.loads(body["response"])

            # Validation
            if not isinstance(result, dict):
                raise ValueError("A resposta do modelo não é um objeto JSON válido.")

            if "categoria" not in result or "justificativa" not in result:
                raise ValueError(
                    f"JSON retornado não contém os campos obrigatórios: {result}"
                )

            return result

    except httpx.HTTPError as ex:
        raise RuntimeError(f"Erro de comunicação com o Ollama: {str(ex)}")
    except json.JSONDecodeError as ex:
        raise ValueError(
            f"Falha ao fazer parse do JSON retornado pelo Ollama: {str(ex)}"
        )
    except Exception as ex:
        raise RuntimeError(f"Erro inesperado na geração do LLM: {str(ex)}")
