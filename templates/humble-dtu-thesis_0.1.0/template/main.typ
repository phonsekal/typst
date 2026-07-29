#import "../src/lib.typ": *

#set text(font: "Noto Sans", lang: "id")

// Membaca file data.json hasil ektraksi AI yang diletakkan di root folder temporary
#let data = json("../data.json")

#show: dtu-project.with(
  title: data.title,
  description: data.description,
  authors: if type(data.authors) == array { data.authors } else if data.authors != none { (str(data.authors),) } else { () },
  date: data.date,
  
  university: data.university,
  department: data.department,
  department-full-title: data.department_full_title,
  address-i: data.address_i,
  address-ii: data.address_ii,
  departmentwebsite: data.departmentwebsite,
)

// --- KONTEN LAPORAN DINAMIS DARI AI ---

= Ringkasan Eksekutif
#data.ringkasan_eksekutif

#v(1em)

= Realisasi Anggaran
#if "realisasi" in data [
  #table(
    columns: (2fr, 1.5fr, 1.5fr, 1fr),
    align: (left, right, right, center),
    fill: (x, y) => if y == 0 { rgb("f0f0f0") } else { none },
    [*Uraian*], [*Pagu (Rp)*], [*Realisasi (Rp)*], [*%*],
    [Belanja Pegawai], [#data.realisasi.belanja_pegawai.pagu], [#data.realisasi.belanja_pegawai.realisasi], [#data.realisasi.belanja_pegawai.persen%],
    [Belanja Barang], [#data.realisasi.belanja_barang.pagu], [#data.realisasi.belanja_barang.realisasi], [#data.realisasi.belanja_barang.persen%]
  )
]

#v(1em)

= Catatan dan Temuan Penting
#if "catatan_penting" in data [
  #for poin in data.catatan_penting [
    - #poin
  ]
]
