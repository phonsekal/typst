import os
import json
import tempfile
import typst
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import Response, HTMLResponse
from openai import OpenAI

app = FastAPI(title="Typst AI Generator (OpenAI)")

# Inisialisasi Client OpenAI (Ambal API Key dari Environment Variable)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

@app.get("/", response_class=HTMLResponse)
async def home():
    """Form Sederhana untuk Testing"""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Typst + OpenAI Generator</title></head>
    <body style="font-family: sans-serif; max-width: 600px; margin: 40px auto; padding: 0 20px;">
        <h2>Generator Laporan Keuangan (Typst + OpenAI)</h2>
        <form action="/generate-pdf" method="post">
            <label><b>Masukkan Teks Mentah / Ringkasan Dokumen:</b></label><br><br>
            <textarea name="raw_text" rows="10" style="width: 100%;" placeholder="Contoh: Laporan Keuangan Kemenag T.A 2025. Belanja pegawai pagu 100jt realisasi 95jt (95%). Belanja barang pagu 50jt realisasi 40jt (80%). Catatan: DIPA awal revisi 2 kali."></textarea><br><br>
            <button type="submit" style="padding: 10px 20px; background: #10a37f; color: white; border: none; cursor: pointer;">Generate PDF</button>
        </form>
    </body>
    </html>
    """

@app.post("/generate-pdf")
async def generate_pdf(raw_text: str = Form(...)):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY belum dikonfigurasi.")

    try:
        # 1. Inisialisasi OpenAI Client
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"""
        Ekstrak informasi dari teks berikut menjadi format JSON persis sesuai struktur ini:
        {{
            "nama_instansi": "Nama Instansi / Kementerian",
            "tahun_anggaran": "202X",
            "ringkasan_eksekutif": "Ringkasan singkat 2-3 kalimat",
            "realisasi": {{
                "belanja_pegawai": {{"pagu": "100.000.000", "realisasi": "95.000.000", "persen": "95"}},
                "belanja_barang": {{"pagu": "50.000.000", "realisasi": "40.000.000", "persen": "80"}}
            }},
            "catatan_penting": ["Catatan 1", "Catatan 2"]
        }}

        Teks Input:
        {raw_text}
        """

        # Memanggil Model OpenAI (gpt-4o-mini disarankan karena cepat & murah)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "Kamu adalah asisten pengolah data laporan keuangan yang bertugas mengekstrak data menjadi JSON terstruktur."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        extracted_json = json.loads(response.choices[0].message.content)

        # 2. Proses Kompilasi Typst di folder temporary
        with tempfile.TemporaryDirectory() as tmpdir:
            # Tulis data JSON hasil AI ke folder temp
            json_path = os.path.join(tmpdir, "data.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(extracted_json, f)

            # Baca template Typst
            template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "lkkl.typ")
            with open(template_path, "r", encoding="utf-8") as f:
                typst_code = f.read()

            # Tulis template ke folder temp agar bisa membaca data.json lokal
            typst_file_path = os.path.join(tmpdir, "main.typ")
            with open(typst_file_path, "w", encoding="utf-8") as f:
                f.write(typst_code)

            # Kompilasi langsung dari Python ke bytes PDF
            pdf_bytes = typst.compile(typst_file_path)

        # 3. Kembalikan PDF ke User
        return Response(content=pdf_bytes, media_type="application/pdf", headers={
            "Content-Disposition": "inline; filename=Laporan_Keuangan.pdf"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses dokumen: {str(e)}")
