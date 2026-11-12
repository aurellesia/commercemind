# CommerceMind — Living Product Scope

> **Single Source of Truth for CommerceMind Product Scope**

Dokumen ini mendefinisikan fitur yang sedang dipertimbangkan atau telah diputuskan untuk scope produk CommerceMind, struktur dan hubungan antarfitur, tanggung jawabnya, serta status keputusan produk dan implementasinya. Dokumen bersifat dinamis dan perlu diperbarui saat keputusan scope atau kondisi implementasi berubah.

Features Tree bukan daftar struktur folder repository, daftar endpoint API, daftar task sprint, atau kumpulan seluruh ide yang belum disetujui. Keberadaan kode, dokumentasi lama, atau feature flag **tidak** dengan sendirinya membuktikan fitur telah disetujui masuk scope produk.

## Reading Status

### Product Decision Status

- **Approved** — telah diputuskan sebagai bagian dari scope produk.
- **Under Review** — sedang dievaluasi; belum menjadi komitmen scope.
- **Deprecated** — diputuskan untuk dihentikan, tetapi masih dicatat untuk transisi.
- **Removed** — telah dikeluarkan dari current product scope dan dipertahankan sebagai riwayat.

Fitur `Under Review` bukan bagian dari committed scope. Status keputusan pada baseline ini dibuat `Under Review` bila dokumen/repository Discovery yang diperiksa tidak menunjukkan keputusan scope yang eksplisit. Ini menandai keputusan yang belum diketahui, bukan rekomendasi agar fitur disetujui.

### Implementation Status

- **Not Implemented** — implementasi tidak ditemukan pada area yang diperiksa.
- **In Development** — pengembangan sedang berlangsung dan ada bukti pekerjaan aktif.
- **Partially Implemented** — sebagian tanggung jawab tersedia, tetapi cakupan yang dideskripsikan belum seluruhnya ada.
- **Implemented** — implementasi untuk tanggung jawab yang dicatat ditemukan di repository.
- **Unknown** — bukti belum cukup untuk menentukan kondisi implementasi.

`Implemented` hanya menyatakan implementasi ditemukan, bukan `Verified`; bukan pula klaim bahwa fitur bebas bug, telah diuji end-to-end, atau siap produksi. Rincian dan batas bukti dicatat per fitur.

## 1. Product Management

### CM-PM-001 — Product Catalog

- **Description / responsibility:** Pengelolaan informasi produk di admin serta pembacaan katalog publik, detail, availability, dan harga efektif.
- **Product decision:** `Under Review` — keputusan scope eksplisit belum ditemukan pada sumber Discovery yang diperiksa.
- **Implementation:** `Implemented` — halaman admin/storefront, API, CRUD, model, dan schema terkait ditemukan; belum diverifikasi runtime sebagai satu alur lengkap.
- **Capabilities found:** melihat daftar/detail; mencari nama, slug, SKU, atau status; membuat, mengubah, serta menghapus produk draft bila tidak terhalang; melihat katalog publik, availability, dan harga efektif.
- **Relevant paths:** `frontend/src/routes/admin/products/+page.svelte`; `frontend/src/routes/storefront/products/+page.svelte`; `backend/api/products.py`; `backend/crud/products.py`; `backend/models/catalog.py`; `backend/schema_models/product.py`.
- **Notes / limitations:** status implementasi berdasarkan bukti repository. Keterkaitan dengan lifecycle produk ada di CM-PM-002.

### CM-PM-002 — Product Lifecycle

- **Description / responsibility:** Status produk draft, active, archived, discontinued, reactivation, dan aturan purchasability/availability.
- **Product decision:** `Under Review` — keputusan scope eksplisit belum ditemukan.
- **Implementation:** `Implemented` — implementasi status dan availability ditemukan; belum diverifikasi sebagai workflow runtime penuh.
- **Capabilities found:** menetapkan status; menghitung apakah produk dapat dibeli berdasar status, harga, dan availability; menyediakan alasan tidak dapat dibeli.
- **Relevant paths:** `frontend/src/routes/admin/products/+page.svelte`; `backend/api/products.py`; `backend/crud/products.py`; `backend/schema_models/product.py`; `backend/schema_models/common.py` (`ProductStatus`).
- **Notes / limitations:** status tersedia tidak membuktikan seluruh transisi/status telah diuji.

### CM-PM-003 — Product Images

- **Description / responsibility:** Mengelola gambar produk dan menyajikannya sebagai galeri storefront.
- **Product decision:** `Under Review` — keputusan scope eksplisit belum ditemukan.
- **Implementation:** `Implemented` — halaman, endpoint/CRUD, model, dan tampilan galeri ditemukan; belum diverifikasi runtime.
- **Capabilities found:** melihat, menambah melalui URL, mengubah URL/alt text, menetapkan gambar utama, menghapus, memilih gambar galeri, dan fallback saat gambar tidak tersedia/gagal dimuat.
- **Relevant paths:** `frontend/src/routes/admin/products/images/+page.svelte`; `frontend/src/routes/storefront/products/[slug]/+page.svelte`; `backend/api/products.py`; `backend/crud/product_images.py`; `backend/models/catalog.py`.
- **Notes / limitations:** dukungan upload file atau media storage tidak dinyatakan oleh bukti yang dicatat di Discovery.

### CM-PM-004 — Pricing

- **Description / responsibility:** Menyimpan harga dasar/modal dan data price set/item harga yang dapat terhubung dengan channel atau region.
- **Product decision:** `Under Review` — keputusan scope eksplisit belum ditemukan.
- **Implementation:** `Partially Implemented` — model dan CRUD price set ditemukan, tetapi route API dan UI khusus pengelolaan harga tidak ditemukan.
- **Capabilities found:** harga dasar produk; harga modal internal; harga efektif untuk data katalog; price set/item harga; validasi rentang tanggal pada schema price set.
- **Relevant paths:** `backend/api/products.py`; `backend/crud/products.py`; `backend/crud/price_sets.py`; `backend/crud/price_set_items.py`; `backend/models/pricing.py`; `backend/models/channels.py`; `backend/models/regions.py`; `backend/schema_models/price_set.py`.
- **Notes / limitations:** alur lengkap penetapan harga, termasuk pengelolaan channel/region, belum diverifikasi.

### CM-PM-005 — Inventory

- **Description / responsibility:** Membaca dan mengubah saldo stok serta mencatat reservasi dan pergerakan stok.
- **Product decision:** `Under Review` — keputusan scope eksplisit belum ditemukan.
- **Implementation:** `Implemented` — halaman admin, API, layanan domain, CRUD, dan model ditemukan; belum diverifikasi runtime secara end-to-end.
- **Capabilities found:** melihat stok, stok rendah, on-hand/reserved/available; menerima dan menyesuaikan stok; membuat/melepas/mengonfirmasi reservasi; melihat movement dan reservasi aktif menurut produk/order.
- **Relevant paths:** `frontend/src/routes/admin/inventory/+page.svelte`; `backend/api/inventory_items.py`; `backend/crud/inventory_service.py`; `backend/crud/inventory_items.py`; `backend/models/inventory.py`.
- **Notes / limitations:** proses inventory terkait order/payment; hal itu tidak menyatakan semua alur transaksi telah terverifikasi.

## 2. Customer & Transaction Management

### CM-CT-001 — Customer Management

- **Description / responsibility:** Pengelolaan customer per brand, termasuk data dasar, pencarian/filter, ringkasan, detail, dan alamat.
- **Product decision:** `Under Review` — keputusan scope eksplisit belum ditemukan.
- **Implementation:** `Implemented` untuk admin customer/address; helper terkait checkout tersedia terpisah. Implementasi belum diverifikasi runtime secara menyeluruh.
- **Capabilities found:** list/search/filter guest atau registered; ringkasan/detail; create/update/delete customer; baca/tambah/ubah/hapus alamat. Helper dapat menggunakan kembali atau membuat guest customer dan alamat yang cocok.
- **Relevant paths:** `frontend/src/routes/brands/[brandSlug]/admin/customers/+page.svelte`; `frontend/src/lib/api/customers.ts`; `backend/api/customers.py`; `backend/crud/customers.py`; `backend/models/customers.py`; `backend/schema_models/customer.py`.
- **Notes / limitations:** helper checkout tidak membuktikan public checkout. Login dan akun customer tidak ditemukan pada area kode yang diperiksa.

### CM-CT-002 — Order Management

- **Description / responsibility:** Membuat dan mengelola order, status/lifecycle, serta koordinasi dengan inventory.
- **Product decision:** `Under Review` — keputusan scope eksplisit belum ditemukan.
- **Implementation:** `Partially Implemented` — backend order dan hubungan lifecycle dengan inventory ditemukan; UI admin order masih placeholder/legacy.
- **Backend capabilities found:** create/list/detail/update/status/cancel/fulfill/delete order; perubahan lifecycle terhubung ke inventory service.
- **Relevant paths:** `backend/api/orders.py`; `backend/crud/orders.py`; `backend/crud/inventory_service.py`; `backend/models/orders.py`.
- **Frontend paths:** `frontend/src/routes/admin/orders/+page.svelte`; `frontend/src/routes/brands/[brandSlug]/admin/orders/+page.svelte`.
- **Notes / limitations:** halaman `/admin/orders` placeholder; halaman brand-scoped memiliki tautan ke panel order legacy default. Perilaku backend belum diverifikasi runtime sebagai workflow lengkap.

### CM-CT-003 — Order Items

- **Description / responsibility:** Mengelola baris item order dan mengaitkannya dengan produk, kuantitas, harga, serta snapshot.
- **Product decision:** `Under Review` — keputusan scope eksplisit belum ditemukan.
- **Implementation:** `Partially Implemented` — API dan CRUD backend ditemukan; antarmuka admin khusus tidak ditemukan pada route frontend yang diperiksa.
- **Backend capabilities found:** tambah, list, get, update, dan delete item order; penggunaan informasi produk/inventory pada proses pembuatan item.
- **Relevant paths:** `backend/api/order_items.py`; `backend/crud/order_items.py`; `backend/models/orders.py`; `backend/schema_models/order.py`.
- **Notes / limitations:** kemampuan backend belum diverifikasi runtime; tidak ditemukan UI operasional khusus.

### CM-CT-004 — Payments

- **Description / responsibility:** Membuat dan mengelola payment record/status yang terkait dengan order.
- **Product decision:** `Under Review` — keputusan scope eksplisit belum ditemukan.
- **Implementation:** `Partially Implemented` — backend payment tersedia, tetapi UI admin placeholder dan gateway eksternal tidak ditemukan.
- **Backend capabilities found:** create/list/detail/by-order/update/status/delete payment; batas satu payment record per order pada model; pemeriksaan module flag pada operasi API tertentu; integrasi lifecycle dengan order/inventory.
- **Relevant paths:** `backend/api/payments.py`; `backend/crud/payments.py`; `backend/crud/inventory_service.py`; `backend/models/payments.py`; `frontend/src/routes/admin/payments/+page.svelte`.
- **Notes / limitations:** tidak ditemukan external payment gateway. Halaman admin hanya placeholder; status code atau keberhasilan runtime bukan bagian dari klaim ini.

## 3. Sales Channels & Platform

### CM-SP-001 — Storefront Catalog

- **Description / responsibility:** Pengalaman baca katalog storefront berdasarkan brand, meliputi daftar, detail, availability, harga, gambar, dan konfigurasi publik.
- **Product decision:** `Under Review` — keputusan scope eksplisit belum ditemukan.
- **Implementation:** `Implemented` untuk alur baca katalog yang ditemukan; belum diverifikasi runtime end-to-end.
- **Capabilities found:** homepage dan daftar produk publik; pencarian/filter ketersediaan/pengurutan sesuai UI; detail slug; harga, availability, gambar; konfigurasi per brand slug; metadata SEO/share pada halaman detail default; menyembunyikan cart/account berdasarkan flag.
- **Relevant paths:** `frontend/src/routes/storefront/`; `frontend/src/routes/brands/[brandSlug]/`; `frontend/src/lib/api/storefront-config.ts`; `frontend/src/lib/storefront/products.ts`; `backend/api/products.py`; `backend/api/settings.py`.
- **Notes / limitations:** link cart/account dapat tampil kondisional tetapi route tujuan tidak ditemukan. Katalog tidak membuktikan proses pembelian.

### CM-SP-002 — Platform Brand Management

- **Description / responsibility:** Operasi platform untuk membuat dan mengelola brand serta membaca konfigurasi brand.
- **Product decision:** `Under Review` — keputusan scope eksplisit belum ditemukan.
- **Implementation:** `Implemented` — UI/API/CRUD terkait brand ditemukan; belum diverifikasi runtime end-to-end.
- **Capabilities found:** list/create/detail/update brand; baca settings per brand; baca konfigurasi storefront publik berdasarkan brand slug.
- **Relevant paths:** `frontend/src/routes/console/brands/`; `frontend/src/lib/api/platform-settings.ts`; `backend/api/settings.py`; `backend/crud/settings.py`; `backend/models/settings.py`.
- **Notes / limitations:** resolusi tenant berdasarkan custom domain tidak ditemukan. Operasi backend menggunakan platform access guard berbasis role header.

### CM-SP-003 — Platform Settings

- **Description / responsibility:** Membaca/mengubah settings platform, storefront, SEO, flag modul, dan konfigurasi sistem serta melihat audit log.
- **Product decision:** `Under Review` — keputusan scope eksplisit belum ditemukan.
- **Implementation:** `Implemented` — halaman console, API, CRUD, dan model ditemukan; belum diverifikasi menyeluruh melalui runtime.
- **Capabilities found:** pengaturan informasi brand/storefront/SEO; module flags; system settings; maintenance mode; ketersediaan katalog publik; checkout flag; audit log API; public storefront config.
- **Relevant paths:** `frontend/src/routes/console/settings/+page.svelte`; `frontend/src/routes/console/storefront/+page.svelte`; `frontend/src/routes/console/modules/+page.svelte`; `frontend/src/routes/console/system/+page.svelte`; `frontend/src/lib/api/platform-settings.ts`; `backend/api/settings.py`; `backend/crud/settings.py`; `backend/models/settings.py`.
- **Notes / limitations:** flag cart, checkout, customer account, payment, dan shipping tidak membuktikan workflow fitur tersebut. Endpoint platform memakai role header untuk platform operator yang disediakan frontend untuk development; autentikasi akun penuh tidak ditemukan.

### CM-SP-004 — Brand-scoped Merchant Admin

- **Description / responsibility:** Area admin merchant dengan konteks brand pada URL dan operasi yang tersedia.
- **Product decision:** `Under Review` — keputusan scope eksplisit belum ditemukan.
- **Implementation:** `Partially Implemented`.
- **Capabilities found:** halaman brand-scoped; pengelolaan customer; baca konfigurasi publik untuk identitas brand; navigasi produk/inventory/order ke panel legacy default.
- **Relevant paths:** `frontend/src/routes/brands/[brandSlug]/admin/`; `backend/api/customers.py`; `backend/models/settings.py`; `backend/models/customers.py`; `backend/models/catalog.py`; `backend/models/orders.py`.
- **Notes / limitations:** halaman produk dan inventory brand-scoped masih mengarah ke panel legacy; halaman order juga mengarah ke panel legacy. Konsistensi brand context endpoint berbeda-beda dan belum diverifikasi menyeluruh.

## 4. Business Monitoring

### CM-BM-001 — Admin Dashboard

- **Description / responsibility:** Halaman dashboard admin yang saat ini menampilkan ringkasan dan daftar contoh.
- **Product decision:** `Under Review` — keputusan scope eksplisit belum ditemukan.
- **Implementation:** `Partially Implemented` — tampilan tersedia, tetapi angka bukan hasil query backend dan tombol tertentu tidak memiliki handler yang tampak.
- **Elements found:** angka contoh pendapatan/order/customer/fulfillment; contoh order terbaru dan peringatan inventory; tombol Export dan New Product tanpa handler yang tampak.
- **Relevant paths:** `frontend/src/routes/admin/+page.svelte`.
- **Notes / limitations:** pemanggilan Reporting API tidak ditemukan pada halaman ini. Angka tidak boleh dianggap sebagai metrik bisnis aktual.

### CM-BM-002 — Reporting API

- **Description / responsibility:** Reporting produk melalui backend API dan query data.
- **Product decision:** `Under Review` — keputusan scope eksplisit belum ditemukan.
- **Implementation:** `Implemented` pada backend; belum diverifikasi runtime.
- **Capabilities found:** ringkasan/dashboard reporting produk; gross revenue per produk; slow-moving; produk aktif dengan stok rendah; produk discontinued yang masih memiliki stok.
- **Relevant paths:** `backend/api/reports.py`; `backend/crud/reports.py`; `backend/schema_models/reporting.py`.
- **Notes / limitations:** UI laporan tidak ditemukan pada `frontend/src/routes/` yang diperiksa.

## 5. Existing Not Implemented / Missing Features

Daftar ini mempertahankan gap yang ditemukan saat Discovery. Pencantuman di sini **bukan** persetujuan bahwa fitur tersebut akan dibangun. Semua keputusan scope tetap `Under Review` karena keputusan eksplisit belum ditemukan.

### CM-GAP-001 — Cart

- **Description / responsibility:** Workflow cart belum dapat dirinci dari implementasi yang ditemukan.
- **Product decision:** `Under Review`.
- **Implementation:** `Not Implemented` pada area yang diperiksa; route frontend dan endpoint backend cart tidak ditemukan.
- **Relevant evidence:** hanya flag dan tautan kondisional yang ditemukan pada konfigurasi/storefront.
- **Notes / limitations:** jangan menyamakan flag/link dengan implementasi cart.

### CM-GAP-002 — Public Checkout

- **Description / responsibility:** Workflow checkout publik.
- **Product decision:** `Under Review`.
- **Implementation:** `Partially Implemented` — helper resolve customer/alamat checkout tersedia, tetapi route frontend dan endpoint checkout tidak ditemukan.
- **Relevant paths:** `backend/crud/customers.py`.
- **Notes / limitations:** helper bukan alur checkout end-to-end.

### CM-GAP-003 — Customer Login

- **Description / responsibility:** Login customer.
- **Product decision:** `Under Review`.
- **Implementation:** `Not Implemented` pada area yang diperiksa; halaman login, endpoint autentikasi customer, dan mekanisme session/token customer tidak ditemukan.

### CM-GAP-004 — Customer Account

- **Description / responsibility:** Area akun customer.
- **Product decision:** `Under Review`.
- **Implementation:** `Not Implemented` pada area yang diperiksa; route account dan API akun customer tidak ditemukan.
- **Notes / limitations:** link account dapat muncul dari flag konfigurasi, tetapi itu bukan implementasi account.

### CM-GAP-005 — Shipping Execution

- **Description / responsibility:** Workflow eksekusi pengiriman.
- **Product decision:** `Under Review`.
- **Implementation:** `Not Implemented` pada area yang diperiksa; workflow shipping, shipment API, dan integrasi carrier tidak ditemukan.
- **Notes / limitations:** flag shipping bukan implementasi workflow.

### CM-GAP-006 — Order Tracking

- **Description / responsibility:** Tracking order publik.
- **Product decision:** `Under Review`.
- **Implementation:** `Not Implemented` pada area yang diperiksa; halaman dan endpoint tracking publik tidak ditemukan.

### CM-GAP-007 — External Payment Gateway

- **Description / responsibility:** Integrasi gateway pembayaran eksternal.
- **Product decision:** `Under Review`.
- **Implementation:** `Not Implemented` pada area yang diperiksa; implementasi payment record/status backend tidak mencakup bukti gateway eksternal.

### CM-GAP-008 — Reporting Interface

- **Description / responsibility:** Antarmuka frontend untuk mengakses laporan.
- **Product decision:** `Under Review`.
- **Implementation:** `Not Implemented` pada route frontend yang diperiksa; Reporting API backend dicatat terpisah sebagai CM-BM-002.

### CM-GAP-009 — AI Partner

- **Description / responsibility:** Kemampuan AI Partner berbasis percakapan dan analisis data bisnis.
- **Product decision:** `Under Review`.
- **Implementation:** `Not Implemented` pada area frontend/API/backend yang diperiksa; implementasinya tidak ditemukan.
- **Relevant context:** arah Decision Engine dibahas sebagai konteks arsitektur masa depan di `docs/architecture/architecture_notes.md`.
- **Notes / limitations:** dokumen arsitektur masa depan bukan bukti implementasi atau keputusan bahwa AI Partner masuk committed scope.

## 6. Feature Relationships

- **Product Catalog (CM-PM-001)** menggunakan informasi lifecycle (CM-PM-002), pricing (CM-PM-004), images (CM-PM-003), dan availability inventory (CM-PM-005) pada pembacaan katalog sesuai implementasi yang ditemukan.
- **Order Management (CM-CT-002)** berhubungan dengan Customer Management (CM-CT-001), Order Items (CM-CT-003), Product/Pricing (CM-PM-001/004), Inventory (CM-PM-005), serta Payments (CM-CT-004). Detail alur kode order dicatat dalam `docs/quality/risk-review/order-creation-flow.md`.
- **Storefront Catalog (CM-SP-001)** membaca konfigurasi Platform Settings (CM-SP-003) dan katalog produk; tampilnya flag atau link checkout/cart tidak menambahkan implementasi CM-GAP-001/002.
- **Platform Brand Management (CM-SP-002)** dan Platform Settings (CM-SP-003) menyediakan konteks brand/settings untuk bagian merchant/storefront yang didukung kode.
- **Admin Dashboard (CM-BM-001)** tidak ditemukan terhubung ke Reporting API (CM-BM-002); dashboard yang ditemukan memakai data statis.

Hubungan di atas merangkum temuan kode dan dokumen Discovery, bukan klaim bahwa setiap alur telah diuji runtime.

## 7. Change Management Rules

### Adding Features

- Tambahkan fitur hanya setelah keputusan scope dibuat.
- Masukkan pada kategori yang sesuai dan berikan Feature ID baru yang unik; jangan mengubah atau menggunakan ulang ID lama.
- Catat tanggal penambahan, Product Decision Status, Implementation Status, deskripsi, path relevan bila diketahui, serta alasan/rujukan keputusan.
- Ide yang belum disetujui tidak dicatat sebagai `Approved`; bila memang perlu dilacak, gunakan `Under Review` dan nyatakan bukan committed scope.

### Modifying Features

- Perbarui deskripsi/tanggung jawab/scope pada fitur yang ada.
- Catat tanggal, ringkasan perubahan, alasan, dan rujukan keputusan pada Change History.
- Jangan mengubah Feature ID hanya karena deskripsi atau implementasi berubah.

### Splitting Features

- Pertahankan Feature ID lama sebagai jejak dan ubah status/notes untuk menunjukkan fitur dipecah.
- Buat Feature ID baru bagi setiap hasil pemecahan dan catat hubungan induk-anak serta tanggalnya.
- Jangan memakai ulang ID lama.

### Merging Features

- Pertahankan Feature ID fitur asal pada riwayat dan catat ID fitur hasil penggabungan sebagai pengganti.
- Catat alasan, tanggal, dan relasi ID pada Change History.
- Jangan menggunakan kembali ID lama untuk fitur lain.

### Deprecating or Removing Features

- Jangan menghapus riwayat fitur yang dihentikan/dikeluarkan.
- Perbarui status menjadi `Deprecated` atau `Removed`, catat tanggal, alasan, dan fitur pengganti jika ada.
- `Deprecated` tetap dicatat untuk transisi; `Removed` tidak lagi termasuk current product scope.

### Status Updates

- Perbarui Implementation Status hanya berdasarkan bukti implementasi repository atau hasil verifikasi yang dicatat.
- Jangan mengubah status ke `Implemented` hanya karena nama file, komentar, dokumentasi rencana, atau feature flag.
- Catat verifikasi sebagai bukti terpisah; status `Implemented` tidak sama dengan `Verified`.
- Product Decision Status hanya berubah berdasarkan keputusan produk, bukan karena implementasi sudah ada atau belum ada.

## 8. Change History

Tanggal historis yang tidak diketahui tidak direkonstruksi. Entri pertama berikut mencatat pembaruan living-scope yang dilakukan pada tanggal yang diminta.

| Date | Feature ID / Section | Change Type | Description | Reason |
|---|---|---|---|---|
| 2026-11-12 | Seluruh dokumen | Establish living scope | Menata ulang inventaris Discovery menjadi scope register dengan ID fitur, pemisahan status keputusan dan implementasi, catatan batas bukti, aturan perubahan, serta relasi antarfitur. Fitur tanpa bukti keputusan scope eksplisit diberi `Under Review`. | Menjadikan Features Tree sumber acuan scope yang hidup tanpa menganggap inventaris implementasi sebagai persetujuan produk. |

## Discovery Sources and Limitations

- `docs/discovery/existing-modules.md`
- Frontend routes: `frontend/src/routes/`
- Frontend API clients: `frontend/src/lib/api/`
- Backend API: `backend/api/`
- Backend CRUD/domain: `backend/crud/`
- Models: `backend/models/`
- Schemas: `backend/schema_models/`
- Access guard: `backend/security.py`
- Konteks/rencana terdahulu: `docs/architecture/architecture_notes.md`, `docs/archive/initial-planning/todo_platform_console_architecture.md`, `docs/archive/initial-planning/todo_storefront_catalog_architecture.md`

Status di dokumen ini membedakan scope produk dari kondisi kode. Temuan Discovery tidak membuktikan keberhasilan runtime; tidak ada test, migrasi, atau operasi data dijalankan dalam pembaruan ini.
