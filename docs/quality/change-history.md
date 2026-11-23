# CommerceMind Change History

## Purpose

Change History adalah catatan kronologis perubahan aktual pada dokumentasi, keputusan, arsitektur, test, dan implementasi CommerceMind. Dokumen ini mempertahankan alasan serta konteks saat perubahan dicatat. Change History bukan pengganti current-state registers dan tidak dengan sendirinya mengesahkan keputusan atau membuktikan implementasi.

## Scope and Relationship to Project Registers

Catat perubahan aktual yang memengaruhi arah produk, Features Tree, Flow Register, Risk Register, Decision Register, arsitektur, testing, dokumentasi, atau software implementation. Hubungkan record dengan Decision ID, Feature ID, Flow ID, dan Risk ID yang relevan. Referensi tidak berarti semua item terkait ikut berubah.

Change History menjaga jejak perubahan lintas dokumen dan tahapan. Current-state register tetap menjadi sumber untuk status saat ini:

- docs/product/features-tree.md mencatat target-state product capabilities dan status keputusan/implementasi feature.
- docs/quality/flow-register.md mencatat flow dan status verifikasinya.
- docs/quality/risk-register.md mencatat risiko dan status assessment.
- docs/quality/decision-register.md mencatat pertanyaan keputusan, alternatif, serta keputusan yang telah disetujui.
- docs/architecture/architecture_notes.md dan dokumentasi discovery mencatat konteks arsitektur dan temuan repository.

Perubahan keputusan dan implementasi keputusan adalah kejadian terpisah dan dapat memerlukan record terpisah. Perubahan yang dilakukan pada beberapa dokumen atau tahap juga dicatat dengan dokumen dan status aktual masing-masing secara akurat.

## Recording Rules

1. Catat setiap perubahan project yang benar-benar dilakukan.
2. Jangan sajikan perubahan yang masih diusulkan sebagai perubahan yang telah diimplementasikan.
3. Keputusan dan implementasi keputusan adalah dua kejadian terpisah.
4. Referensikan Decision, Feature, Flow, dan Risk ID yang relevan bila tersedia; jangan mengarang relasi.
5. Jangan gunakan ulang atau mengubah ID yang sudah ada tanpa proses perubahan yang tercatat.
6. Jelaskan apa yang benar-benar berubah dan alasan perubahan tersebut.
7. Perubahan pada dokumen berbeda atau tahap implementasi berbeda dapat memerlukan record terpisah.
8. Jangan menulis ulang catatan historis untuk mencocokkan keadaan baru. Catat perubahan berikutnya sebagai record baru.
9. Gunakan Notes untuk menyatakan batasan, ketidakpastian, atau arti khusus dari status record.

## Fields

| Field | Description |
|---|---|
| Change ID | Unique permanent ID, format CM-CHG-NNN. |
| Date | Tanggal perubahan dicatat, dalam format YYYY-MM-DD. |
| Change Type | Kategori perubahan: Product, Feature, Flow, Risk, Decision, Architecture, Implementation, Testing, atau Documentation. Cantumkan kategori yang berlaku. |
| Change Title | Judul singkat perubahan aktual. |
| Description | Apa yang benar-benar berubah. |
| Reason | Alasan perubahan dilakukan. |
| Related Decision IDs | Decision ID yang terkait, bila ada. |
| Affected Feature IDs | Feature ID yang terdampak, bila ada. |
| Affected Flow IDs | Flow ID yang terdampak, bila ada. |
| Affected Risk IDs | Risk ID yang terdampak, bila ada. |
| Affected Documents | Dokumen yang benar-benar diubah; jangan mencantumkan dokumen yang hanya dibaca atau dirujuk. |
| Affected Modules | Modul software yang benar-benar terdampak; gunakan Not applicable bila perubahan hanya dokumentasi. |
| Change Status | Proposed, Approved, Implemented, atau Reverted. |
| Notes | Konteks tambahan, batasan, dan klarifikasi status. |

## Change ID and Status Conventions

- Tetapkan ID permanen berurutan dengan format CM-CHG-NNN, dimulai dari CM-CHG-001. Periksa register sebelum menetapkan ID baru; jangan gunakan ulang ID.
- Proposed berarti perubahan dicatat sebagai usulan dan belum disetujui.
- Approved berarti perubahan telah mendapat persetujuan, tetapi belum tentu diterapkan.
- Implemented berarti perubahan yang dicatat benar-benar telah dilakukan pada scope yang disebutkan. Status ini tidak otomatis berarti keputusan produk telah final atau software telah diimplementasikan.
- Reverted berarti perubahan yang sebelumnya dilakukan kemudian dibatalkan; simpan record lama dan tambahkan record pembatalan tersendiri.
- Jangan menyimpulkan approval dari perubahan dokumen. Catat approval eksplisit pada decision owner dan current-state register yang relevan.

## Records

[Google Sheet | https://docs.google.com/spreadsheets/d/1Nlnxef9hvqDGjeB_Whk2XMj-2hOdIZJod4f1bTxEKro/edit?gid=96869610#gid=96869610]
