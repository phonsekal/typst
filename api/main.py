import os
import json
import tempfile
import shutil
import typst
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import Response
from openai import OpenAI

app = FastAPI()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

@app.post("/generate-pdf")
async def generate_pdf(raw_text: str = Form(...)):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY belum set.")

    try:
        # 1. Olah data via OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"""
        Ekstrak teks ini menjadi JSON sesuai kebutuhan laporan:
        {raw_text}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        extracted_json = json.loads(response.choices[0].message.content)

        # 2. Proses Kompilasi Multi-File Typst
        with tempfile.TemporaryDirectory() as tmpdir:
            # Path lokasi template asli di project
            base_template_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "humble-dtu-thesis")
            
            # Copy seluruh struktur folder template ke folder temporary Vercel
            shutil.copytree(base_template_dir, tmpdir, dirs_exist_ok=True)

            # Simpan file data.json hasil AI ke dalam folder temp tersebut
            json_path = os.path.join(tmpdir, "data.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(extracted_json, f)

            # Tentukan file entrypoint Typst (misal: template/main.typ atau main.typ)
            entrypoint_typst = os.path.join(tmpdir, "template", "main.typ")

            # Kompilasi dari file entrypoint
            pdf_bytes = typst.compile(entrypoint_typst)

        # 3. Return PDF
        return Response(content=pdf_bytes, media_type="application/pdf", headers={
            "Content-Disposition": "inline; filename=Laporan_Keuangan_DTU.pdf"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses dokumen: {str(e)}")
