#import "../src/lib.typ": *

// 1. Membaca data JSON yang dihasilkan oleh OpenAI
#let data = json("../data.json")

// 2. Mengirim data JSON ke template dtu-project (yang akan meneruskannya ke frontpage-dtu)
#show: doc => dtu-project(
  title: data.title,
  description: data.description,
  authors: if type(data.authors) == array { data.authors } else { (str(data.authors),) },
  date: data.date,
  university: data.university,
  department: data.department,
  department-full-title: data.department_full_title,
  doc
)

// 3. Isi Konten Laporan (Body)
= Ringkasan Eksekutif
#data.ringkasan_eksekutif

= Catatan & Temuan Penting
#for poin in data.catatan_penting [
  - #poin
]
