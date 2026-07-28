#import "../src/lib.typ": *

#set text(font: "Noto Sans", lang: "id")

#show: dtu-project.with(
  title: "Laporan Keuangan",
  description: [Tahun Anggaran 2025 (_Audited_)],
  authors: ("Sekretariat Badan Pengembangan dan Pembinaan Bahasa",),
  date: datetime.today().display("[day] [month repr:long] [year]"),
  
  university: "",
  department: "",
  department-full-title: "",
  address-i: "Badan Pengembangan dan Pembinaan Bahasa",
  address-ii: "Jalan Daksinapati Barat IV, Ramawangun",
  departmentwebsite: "badanbahasa.kemendikdasmen.go.id",  

  // --- HAPUS/KOMENTARI BAGIAN INI (PREFACE) ---
  /* before: (
    summary-english: include "sections/preface/english.typ",
    summary-danish: include "sections/preface/danish.typ",
    preface: include "sections/preface/preface.typ",
    acknowledgement: include "sections/preface/acknowledgement.typ",
    contents: include "sections/preface/contents.typ", 
    readers-guide: include "sections/preface/readers-guide.typ",
  ),
  */
)

// --- HAPUS SEMUA BARIS DI BAWAH INI ---
// #include "sections/introduction.typ"
// #include "sections/conclusion.typ"
// #pagebreak()
// #bibliography("works.bib")
// #pagebreak()
// #include "sections/appendix.typ"