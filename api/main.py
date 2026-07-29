import os
import json
import tempfile
import shutil
import typst
from pathlib import Path
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import Response, HTMLResponse
from openai import OpenAI

CACHE_DIR = Path("/tmp/typst_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ["TYPST_CACHE_DIR"] = str(CACHE_DIR)

app = FastAPI()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "templates" / "humble-dtu-thesis_0.1.0"

@app.get("/", response_class=HTMLResponse)
async def home():
    """Halaman Form Sederhana untuk Testing"""
    return """
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <title>Generator Dokumen Typst + AI</title>
        <style>
            body { font-family: system-ui, -apple-system, sans-serif; max-width: 700px; margin: 40px auto; padding: 0 20px; line-height: 1.5; }
            textarea { width: 100%; box-sizing: border-box; padding: 10px; font-family: inherit; border-radius: 6px; border: 1px solid #ccc; }
            button { background: #0070f3; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 6px; cursor: pointer; }
            button:hover { background: #0051a2; }
        </style>
    </head>
    <body>
        <h2>Generator Laporan & Dokumen (Typst + OpenAI)</h2>
        <p>Masukkan narasi/teks data mentah di bawah ini untuk diproses menjadi PDF resmi via Typst.</p>
        <form action="/generate-pdf" method="post">
            <label for="raw_text"><b>Teks Data Input:</b></label><br><br>
            <textarea id="raw_text" name="raw_text" rows="10" placeholder="Contoh: Laporan Keuangan Kementerian Pekerjaan Umum T.A. 2025. Belanja pegawai pagu 100jt realisasi 95jt. Belanja barang pagu 50jt realisasi 40jt. Catatan: Ada revisi DIPA pada triwulan II..."></textarea><br><br>
            <button type="submit">Generate PDF Sekarang</button>
        </form>
    </body>
    </html>
    """

@app.post("/generate-pdf")
async def generate_pdf(raw_text: str = Form(...)):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY belum dikonfigurasi.")

    if not TEMPLATE_DIR.exists():
        raise HTTPException(
            status_code=500, 
            detail=f"Folder template tidak ditemukan di: {TEMPLATE_DIR}"
        )

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"""
Ekstrak data dari teks berikut menjadi format JSON terstruktur persis sesuai skema ini:
{{
    "title": "Judul Utama Laporan / Dokumen",
    "description": "Sub-judul / Deskripsi Singkat Laporan",
    "authors": ["Nama Penyusun 1", "Nama Penyusun 2"],
    "date": "Tanggal / Tahun Anggaran",
    "university": "Nama Kementerian / Lembaga Utama",
    "department": "Nama Unit Kerja / Ditjen (Singkatan)",
    "department_full_title": "Nama Lengkap Unit Kerja / Biro",
    "ringkasan_eksekutif": "Ringkasan isi laporan 2-3 paragraf",
    "catatan_penting": ["Poin penting 1", "Poin penting 2"]
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

            # Copy seluruh folder template ke temp folder
            shutil.copytree(TEMPLATE_DIR, tmpdir_path, dirs_exist_ok=True)

            # Simpan data.json di root folder temporary
            json_path = tmpdir_path / "data.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(extracted_json, f)

            # Cari entrypoint main.typ
            entrypoint_typst = tmpdir_path / "template" / "main.typ"
            if not entrypoint_typst.exists():
                entrypoint_typst = tmpdir_path / "main.typ"

            # Kompilasi PDF dengan menentukan 'root' ke folder temporary paling luar
            pdf_bytes = typst.compile(
                str(entrypoint_typst),
                root=str(tmpdir_path)
            )

        return Response(
            content=pdf_bytes, 
            media_type="application/pdf", 
            headers={"Content-Disposition": "inline; filename=Laporan_Hasil.pdf"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses dokumen: {str(e)}")
