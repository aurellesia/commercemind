# CommerceMind Documentation Guide

Folder `docs/` mengelompokkan dokumentasi berdasarkan tujuan dan jenisnya.

- `product/`: mendefinisikan scope produk CommerceMind dan fitur-fitur yang dicatat dalam Features Tree.
- `architecture/`: berisi dokumentasi arsitektur terkini.
- `discovery/`: berisi hasil investigasi repository dan penilaian teknis, termasuk inventaris modul, dependensi, konfigurasi, proses menjalankan aplikasi, dan pengujian.
- `quality/`: berisi dokumentasi verifikasi kualitas dan tinjauan risiko. Subfolder `risk-review/` menyimpan analisis alur dan risiko spesifik.
- `archive/initial-planning/`: mempertahankan dokumen perencanaan historis dari tahap awal pengembangan CommerceMind.

Dokumen dalam arsip merupakan referensi historis. Isinya merekam rencana dan konteks pada masa penulisannya, sehingga tidak otomatis menjadi keputusan arsitektur atau scope produk yang berlaku saat ini. Gunakan dokumentasi terkini pada `architecture/` dan `product/` untuk memahami keputusan saat ini, serta periksa tanggal dan konteks sebelum mengandalkan dokumen arsip.

## Language Standards

Bahasa utama dokumentasi internal adalah Bahasa Indonesia. Gunakan Bahasa Inggris untuk judul dokumen, heading, nama fitur/modul, technical terminology, API endpoint, identifier, serta nama class, function, dan variable. Tulis penjelasan dan analisis teknis dalam Bahasa Indonesia; label tabel menggunakan Bahasa Inggris dan uraian tabel menggunakan Bahasa Indonesia.

Jangan menerjemahkan istilah teknis yang menjadi kurang tepat atau kurang dikenal developer bila diterjemahkan. Pertahankan code block, command, dan komentar kode sesuai sumbernya. Nama teknis seperti `Order Creation Flow`, `Product Catalog`, `POST /orders/`, dan `create_order` tetap dalam Bahasa Inggris.
