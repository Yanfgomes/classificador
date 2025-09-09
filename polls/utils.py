import re
import os
import json
from openai import OpenAI
from django.conf import settings
import PyPDF2

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def avaliar_email(texto_email, arquivo_path=None):
    # Conteúdo do anexo (se houver)
    conteudo_anexo = ""
    if arquivo_path:
        ext = os.path.splitext(arquivo_path)[1].lower()
        try:
            if ext == ".txt":
                with open(arquivo_path, "r", encoding="utf-8", errors="ignore") as f:
                    conteudo_anexo = f.read()

            elif ext == ".pdf":
                with open(arquivo_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    conteudo_anexo = ""
                    for page in reader.pages:
                        conteudo_anexo += page.extract_text() or ""

            else:
                conteudo_anexo = "[Arquivo enviado, mas o formato não é suportado para leitura de texto.]"
        except Exception:
            conteudo_anexo = "[Erro ao tentar extrair o conteúdo do arquivo.]"

    prompt = f"""
    Você é um avaliador de e-mails. Analise o conteúdo abaixo (texto e, se houver, o texto extraído do anexo)
    e responda **apenas em JSON válido**, no seguinte formato:

    {{
    "produtivo": true|false,
    "resposta": "uma frase breve que será enviada como resposta ao solicitante, no máximo 1 frase",
    "nota": 1-10
    }}

    Texto do e-mail:
    {texto_email}

    {"Texto extraído do anexo:\n" + conteudo_anexo if conteudo_anexo else ""}
        """.strip()

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[{"role": "user", "content": prompt}]
    )

    # Parse da resposta
    saida = (response.output_text or "").strip()

    # Remove cercas de código caso o modelo embrulhe em ```json ... ```
    bruto = re.sub(r"^```(?:json)?\s*|\s*```$", "", saida, flags=re.IGNORECASE | re.MULTILINE).strip()

    try:
        data = json.loads(bruto)
        produtivo = bool(data.get("produtivo"))
        resposta = (data.get("resposta") or "").strip()
        nota = int(data.get("nota")) if data.get("nota") is not None else None

        # Sanitiza nota entre 1 e 10
        if nota is not None:
            nota = max(1, min(10, nota))
            
        return produtivo, resposta, nota
    except Exception as e:
        raise ValueError(f"Erro ao interpretar resposta da IA: {saida}") from e
    