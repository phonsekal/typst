import os
import json
import tempfile
import shutil
import typst
from pathlib import Path
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import Response, HTMLResponse
from openai import OpenAI

app = FastAPI()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "templates" / "humble-dtu-thesis_0.1.0"

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <title>Generator Dokumen Typst + AI</title>
        <style>
            body { font-family: system-ui, sans-serif; max-width: 700px; margin: 40px auto; padding: 0 20px; line-height: 1.5; }
            textarea { width: 100%; box-sizing: border-box; padding: 10px; font-family: inherit; border-radius: 6px; border: 1px solid #ccc; }
            button { background: #0070f3; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 6px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h2>Generator Laporan & Dokumen (Typst + OpenAI)</h2>
        <form action="/generate-pdf" method="post">
            <textarea id="raw_text" name="raw_text" rows="10" placeholder="Masukkan narasi laporan di sini..."></textarea><br><br>
            <button type="submit">Generate PDF Sekarang</button>
        </form>
    </body>
    </html>
    """

@app.post("/generate-pdf")
async def generate_pdf(raw_text: str = Form(...)):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY belum set.")

    if not TEMPLATE_DIR.exists():
        raise HTTPException(status_code=500, detail=f"Folder template tidak ditemukan di: {TEMPLATE_DIR}")

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"""
        Ekstrak teks ini menjadi JSON terstruktur persis sesuai kunci berikut:
        {{
            "title": "Laporan Keuangan",
            "description": "Tahun Anggaran 2025 (Audited)",
            "authors": ["Sekretariat Badan Pengembangan dan Pembinaan Bahasa"],
            "date": "29 Juli 2026",
            "university": "",
            "department": "Badan Bahasa",
            "department_full_title": "Sekretariat Badan Pengembangan dan Pembinaan Bahasa",
            "address_i": "Badan Pengembangan dan Pembinaan Bahasa",
            "address_ii": "Jalan Daksinapati Barat IV, Rawamangun",
            "departmentwebsite": "badanbahasa.kemendikdasmen.go.id",
            "ringkasan_eksekutif": "Narasi ringkasan laporan 2-3 paragraf...",
            "realisasi": {{
                "belanja_pegawai": {{"pagu": "100.000.000", "realisasi": "95.000.000", "persen": "95"}},
                "belanja_barang": {{"pagu": "50.000.000", "realisasi": "40.000.000", "persen": "80"}}
            }},
            "catatan_penting": ["Catatan 1", "Catatan 2"]
        }}

        Teks Input:
        {raw_text}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        extracted_json = json.loads(response.choices[0].message.content)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Copy seluruh struktur folder template ke tmpdir
            shutil.copytree(TEMPLATE_DIR, tmpdir_path, dirs_exist_ok=True)

            # Simpan data.json
            json_path = tmpdir_path / "data.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(extracted_json, f)

            entrypoint_typst = tmpdir_path / "template" / "main.typ"

            # Compile Typst dengan root ditetapkan ke tmpdir
            pdf_bytes = typst.compile(
                str(entrypoint_typst),
                root=str(tmpdir_path)
            )

        return Response(
            content=pdf_bytes, 
            media_type="application/pdf", 
            headers={"Content-Disposition": "inline; filename=Laporan_Keuangan.pdf"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses dokumen: {str(e)}")
