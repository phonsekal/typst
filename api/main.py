import os
import json
import tempfile
import shutil
import typst
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import Response, HTMLResponse
from openai import OpenAI

app = FastAPI(title="Typst Multi-File AI Generator")

# Inisialisasi API Key dari Environment Variable Vercel
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

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
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY belum dikonfigurasi di Environment Variables Vercel.")

    try:
        # 1. Minta OpenAI mengekstrak teks ke format JSON
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"""
        Ekstrak data dari teks berikut menjadi format JSON terstruktur untuk laporan:
        {{
            "nama_instansi": "Nama Kementerian / Instansi / Judul",
            "tahun_anggaran": "202X",
            "ringkasan_eksekutif": "Narasi ringkasan laporan 2-3 paragraf",
            "realisasi": {{
                "belanja_pegawai": {{"pagu": "100.000.000", "realisasi": "95.000.000", "persen": "95"}},
                "belanja_barang": {{"pagu": "50.000.000", "realisasi": "40.000.000", "persen": "80"}}
            }},
            "catatan_penting": ["Poin catatan 1", "Poin catatan 2"]
        }}

        Teks Input:
        {raw_text}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Kamu adalah asisten pengolah dokumen resmi yang bertugas mengekstrak data menjadi JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        extracted_json = json.loads(response.choices[0].message.content)

        # 2. Proses Kompilasi Typst dengan menyalin seluruh folder template ke Temp Directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Tentukan path lokasi template asli di repository
            base_template_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "humble-dtu-thesis")
            
            # Salin seluruh struktur folder template (termasuk subfolder src, images, lib.typ) ke tmpdir
            shutil.copytree(base_template_dir, tmpdir, dirs_exist_ok=True)

            # Simpan file data.json hasil ekstraksi AI di root tmpdir
            json_path = os.path.join(tmpdir, "data.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(extracted_json, f)

            # Entrypoint file Typst utama (sesuai struktur DTU thesis: template/main.typ)
            entrypoint_typst = os.path.join(tmpdir, "template", "main.typ")

            # Jika file main.typ tidak ditemukan di subfolder template, fallback ke root tmpdir
            if not os.path.exists(entrypoint_typst):
                entrypoint_typst = os.path.join(tmpdir, "main.typ")

            # Kompilasi dari Python binding
            pdf_bytes = typst.compile(entrypoint_typst)

        # 3. Kembalikan PDF langsung ke browser
        return Response(
            content=pdf_bytes, 
            media_type="application/pdf", 
            headers={"Content-Disposition": "inline; filename=Laporan_Hasil.pdf"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses dokumen: {str(e)}")
