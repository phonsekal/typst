// Membaca file JSON yang digenerate oleh backend
#let data = json("data.json")

#set page(
  paper: "a4",
  margin: (top: 2.5cm, bottom: 2.5cm, left: 3cm, right: 2.5cm),
  header: align(right, text(8pt, fill: luma(120))[LAPORAN KEUANGAN T.A. #data.tahun_anggaran]),
  footer: align(center)[#counter(page).display()]
)

#set text(font: "Liberation Sans", size: 11pt)

// Title / Halaman Judul Sederhana
#align(center)[
  #v(2cm)
  #text(16pt, weight: "bold")[RINGKASAN LAPORAN KEUANGAN] \
  #v(0.2cm)
  #text(13pt, weight: "bold")[#data.nama_instansi] \
  #text(11pt)[TAHUN ANGGARAN #data.tahun_anggaran]
]

#v(1cm)

== 1. Ringkasan Executif
#data.ringkasan_eksekutif

#v(0.5cm)

== 2. Realisasi Anggaran
#table(
  columns: (2fr, 1.5fr, 1.5fr, 1fr),
  align: (left, right, right, center),
  fill: (x, y) => if y == 0 { rgb("e0e0e0") } else { none },
  [*Uraian*], [*Pagu (Rp)*], [*Realisasi (Rp)*], [*%*],
  [Belanja Pegawai], [#data.realisasi.belanja_pegawai.pagu], [#data.realisasi.belanja_pegawai.realisasi], [#data.realisasi.belanja_pegawai.persen%],
  [Belanja Barang], [#data.realisasi.belanja_barang.pagu], [#data.realisasi.belanja_barang.realisasi], [#data.realisasi.belanja_barang.persen%]
)

#v(0.5cm)

== 3. Catatan Penting
#for poin in data.catatan_penting [
  - #poin
]
