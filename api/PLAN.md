# PLAN v3 — `analisa-saham`: CLI Analisa Fundamental & Dividen Saham IDX

## Spec (hasil interview dengan user)

- **Pasar:** IDX (Bursa Efek Indonesia) saja.
- **Bentuk:** CLI di terminal. Alat personal, bukan produk komersial (yfinance = personal/research use; dicantumkan di README).
- **Fokus:** analisa fundamental. TIDAK ada analisa teknikal, screening, atau backtest.
- **Cakupan wajib:**
  1. Data historis 5 tahun ke belakang (lihat "kejujuran data" di bawah).
  2. Proyeksi pertumbuhan 5–10 tahun ke depan.
  3. Proyeksi laba (earnings).
  4. **Paling penting:** perkiraan dividen per tahun — DPS dan yield %. TIDAK menghitung nominal kepemilikan user.

## Kejujuran data (kontrak dengan user)

- **Laporan keuangan:** Yahoo/yfinance hanya menyediakan ~4 periode tahunan. Tabel diberi judul "Historis (maks. 4 periode dari Yahoo)" — tidak mengklaim 5 tahun.
- **Dividen & harga:** riwayat panjang tersedia → bagian dividen dan harga benar-benar 5–10 tahun.
- Setiap tabel mencantumkan as-of date dan sumber.

## Penggunaan

```
saham BBCA            # laporan lengkap satu emiten
saham BBCA --tahun 10 # horizon proyeksi 10 tahun (default 5)
```

## Stack

Python 3.11+, `yfinance` (versi di-pin di pyproject), `rich`, `argparse`, `pytest`.

## Struktur

```
analisa_saham/
  __init__.py
  cli.py          # entry point, orkestrasi laporan
  data.py         # fetch yfinance + validasi + cache per-dataset
  fundamental.py  # rasio historis (formula eksplisit di bawah)
  dividen.py      # agregasi dividen kalender, yield, payout
  proyeksi.py     # proyeksi skenario dengan fade & guard
tests/fixtures/
```

## Validasi ticker & data (data.py)

- Normalisasi suffix idempoten: `BBCA` → `BBCA.JK`; `BBCA.JK` tetap. Uppercase.
- Validasi hasil Yahoo: `quoteType == EQUITY`, exchange Jakarta, currency `IDR` (harga & laporan keuangan). Mismatch → error jelas, bukan angka diam-diam salah.
- Harga: `history(auto_adjust=False, repair=True)` — basis harga eksplisit (Close unadjusted, split-adjusted manual seperlunya); metadata repair disimpan.
- Cache per-dataset dengan TTL berbeda: harga 1 jam, laporan keuangan 7 hari, dividen 1 hari. Timestamp pengambilan ditampilkan.
- Kegagalan: retry terbatas (2× backoff). Dataset gagal → laporan parsial dengan bagian itu ditandai "data tidak tersedia" — TIDAK PERNAH dikonversi jadi 0.

## Formula rasio (eksplisit)

| Rasio | Formula | Catatan |
|---|---|---|
| EPS | Diluted EPS dari laporan; fallback: laba bersih attributable ÷ diluted shares | field & fallback dicatat di output |
| Net margin | Net income ÷ revenue | untuk bank: revenue = total revenue Yahoo, diberi label |
| ROE | Net income ÷ rata-rata ekuitas (awal+akhir)/2; fallback ekuitas akhir jika periode sebelumnya tak ada | fallback ditandai |
| DER | Total liabilities ÷ total equity | **untuk sektor bank/asuransi: ditampilkan N/A** dengan catatan leverage inheren; deteksi via `info.sector/industry` |
| PER historis | Harga akhir tahun fiskal ÷ EPS tahun itu | N/A jika EPS ≤ 0 |
| PBV historis | Harga akhir tahun fiskal ÷ book value per share tahun itu | N/A jika BVPS ≤ 0 |

**Guard pembagi (berlaku semua rasio):** penyebut ≤ 0 atau hilang → rasio = N/A dengan alasan, tidak pernah ZeroDivisionError/inf. EPS = 0 ikut memicu penolakan proyeksi.

**Harga "akhir tahun fiskal":** Close terakhir yang tersedia pada atau sebelum tanggal tutup buku (tutup buku bisa jatuh di hari libur bursa).

**Basis per lembar tunggal:** semua besaran per lembar (harga, EPS, DPS, BVPS) dikonversi ke basis jumlah saham HARI INI memakai faktor split kumulatif dari data split Yahoo — satu fungsi adjustment dipakai bersama, tidak ada adjustment ganda. Harga diambil `auto_adjust=False` lalu di-split-adjust oleh fungsi ini (dividen TIDAK ikut meng-adjust harga).

## Dividen (dividen.py)

- Definisi jujur: **"dividen kas yang tercatat per tahun kalender di data Yahoo"** — bukan atribusi ke tahun buku. Label ini tercetak di laporan.
- Tahun berjalan → label **YTD**, dikecualikan dari CAGR & median payout.
- Yield historis: DPS tahun itu ÷ rata-rata Close harian tahun itu (unadjusted), diberi label formula persis.
- Payout ratio: DPS kalender ÷ EPS tahun fiskal yang sama; tahun dengan EPS ≤ 0 dikecualikan dari median dan ditandai.
- Anomali: `repair=True` + tanda pada perubahan DPS >5× antar tahun (kemungkinan split/dividen spesial/data rusak) — ditampilkan, tidak diperbaiki diam-diam.
- Dividen kosong → "tidak ditemukan event dividen di data Yahoo" (bukan klaim "tidak membagikan dividen").
- **Tahun-nol:** tahun kalender lengkap tanpa event dividen (dalam rentang listing) diisi DPS = 0 di tabel — bukan dihilangkan. CAGR dividen dihitung hanya jika kedua endpoint > 0; selain itu N/A dengan keterangan.

## Proyeksi (proyeksi.py) — sensitivitas deterministik, bukan ramalan

Dicetak sebagai **"Skenario sensitivitas"** dengan kotak asumsi eksplisit:

- **Basis:** EPS diluted tahun fiskal lengkap terakhir (as-of date dicetak). Asumsi jumlah saham konstan (dicetak).
- **Baseline growth:** CAGR EPS dari seluruh periode tersedia; interval antar-tahun ikut diperiksa — jika ada tahun rugi atau tanda berubah → **proyeksi ditolak** dengan penjelasan, bukan dipaksakan.
- **Negatif dipertahankan:** CAGR negatif TIDAK di-floor ke 0. Perusahaan menyusut terlihat menyusut di semua skenario.
- **Skenario:** konservatif = CAGR − 3 p.p., moderat = CAGR, optimis = CAGR + 3 p.p. Semua di-clamp ke [−15%, +20%] dan clamping dilaporkan.
- **Fade:** untuk horizon >5 tahun, growth memudar linear ke 4%/tahun (proksi PDB nominal) mulai tahun ke-6 — tidak ada 20% yang bertahan 10 tahun.
- **DPS proyeksi:** EPS proyeksi × median payout (hanya dari tahun valid), di-cap 100%. Disertai catatan: "asumsi payout konstan; bukan model kesinambungan dividen".
- **"Yield proyeksi"** dinamai persis: **proyeksi DPS ÷ harga sekarang** — bukan prediksi yield pasar masa depan.
- Syarat minimal: ≥3 observasi EPS valid dan ≥3 tahun dividen; kurang dari itu → bagian proyeksi berisi penjelasan kenapa tidak dihitung.

## Isi laporan (urutan)

1. Profil — nama, sektor, harga terakhir + timestamp, market cap.
2. Historis fundamental (maks. 4 periode) — tabel formula-eksplisit di atas.
3. Riwayat dividen 5–10 tahun — DPS, yield, payout, CAGR; YTD terpisah.
4. Skenario sensitivitas 5–10 tahun — EPS & DPS per tahun, 3 skenario + kotak asumsi.
5. Disclaimer — bukan saran investasi; data Yahoo delayed & bisa tak lengkap; personal use.

## Testing

- yfinance di-pin; unit test semua perhitungan (CAGR, interval check, fade, clamp, payout, yield).
- Fixtures: BBCA (bank, dividen rutin), TLKM (non-bank), emiten rugi, emiten tanpa dividen, tahun YTD, currency mismatch, DataFrame kosong.
- Test parsial-failure: satu dataset gagal → laporan tetap keluar dengan bagian ditandai.
- Satu smoke test live opsional (`pytest -m live`), tidak jalan default.

## Keputusan scope (dipertahankan melawan kritik)

- **Bukan model sustainability dividen** (cash flow/capex/regulatory capital): terlalu berat untuk CLI personal; diganti kotak asumsi eksplisit + cap payout 100%.
- **Bukan set metrik per-sektor penuh:** hanya special-case bank/asuransi (DER→N/A, label revenue). Sektor lain pakai set umum.
- **CAGR + fade, bukan robust trend fitting:** cukup untuk sensitivitas deterministik yang diberi label jujur; penolakan proyeksi saat data tidak layak adalah guard utamanya.
