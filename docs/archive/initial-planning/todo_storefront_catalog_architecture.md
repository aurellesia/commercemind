# Todo Storefront Catalog Architecture

Tujuan dokumen ini adalah menyimpan backlog modul storefront catalog agar customer bisa melihat produk publik dengan informasi harga, stok, gambar, dan detail produk sebelum modul cart dan checkout dibangun.

CommerceMind diposisikan sebagai template ecommerce universal yang bisa dipakai ulang untuk skincare, fashion, aksesoris, atau vertical lain. Skincare dipakai sebagai contoh awal karena data produk saat ini sudah memiliki metadata seperti BPOM, cara pakai, komposisi, warnings, storage, dan net weight.

Scope dokumen ini hanya sampai produk tampil di storefront. Cart, buy now, guest checkout, payment, dan order tracking akan dibahas di arsitektur terpisah setelah catalog stabil.

## Kondisi Saat Ini

Storefront saat ini sudah memiliki pondasi:

- route `frontend/src/routes/storefront/+page.svelte`
- route `frontend/src/routes/storefront/products/+page.svelte`
- route `frontend/src/routes/storefront/products/[slug]/+page.svelte`
- API client `productsApi.catalog()`
- API client `productsApi.getDetailBySlug(slug)`
- endpoint backend `GET /products/catalog`
- endpoint backend `GET /products/by-slug/{slug}/detail`
- read model product availability dari modul products

Data product yang sudah tersedia untuk storefront:

- `id`
- `name`
- `slug`
- `sku`
- `description`
- `status`
- `base_price`
- `effective_price`
- `primary_image`
- `available_quantity`
- `is_low_stock`
- `is_purchasable`
- `not_purchasable_reason`
- detail vertical-specific seperti BPOM/certification, cara pakai/perawatan, komposisi/material, warnings, storage, net weight
- gallery images pada product detail

Gap utama:

- storefront belum diperlakukan sebagai module tersendiri
- homepage storefront masih sangat minimal
- catalog belum punya filter status/availability yang jelas untuk customer
- catalog belum punya sort produk
- catalog belum punya UX mobile yang divalidasi khusus
- error/loading/empty state masih perlu dipoles untuk customer publik
- product card belum punya CTA final karena cart belum ada
- belum ada test/smoke khusus storefront catalog
- copy masih campuran English, perlu disesuaikan dengan target customer Indonesia

## Prinsip Desain

- Storefront hanya menampilkan data yang aman untuk customer.
- Storefront copy dan struktur UI harus general sebagai template ecommerce, bukan terkunci ke satu vertical.
- Vertical-specific metadata boleh tampil bila datanya ada, tetapi label UI harus tetap bisa dipakai untuk kategori selain skincare.
- `cost_price` tidak boleh tampil atau terbawa ke UI storefront.
- URL publik product memakai `slug`, bukan `id`.
- Product yang tampil di catalog publik minimal harus `active`.
- Product yang bisa dibeli harus `is_purchasable = true`.
- Product out of stock boleh tampil sebagai preview bila strategi bisnis mengizinkan, tetapi statusnya harus jelas.
- Harga yang tampil harus berasal dari server-side `effective_price`, fallback ke `base_price`.
- Stok yang tampil harus berasal dari read model availability, bukan dihitung ulang di frontend.
- UI storefront harus ringan, jelas, dan mudah dipakai customer non-teknis.

## Fase 1 — Storefront Module Boundary

- [x] Tetapkan struktur storefront sebagai module frontend:
  - [x] routes storefront
  - [x] API client storefront/product catalog
  - [x] shared formatting helper untuk harga
  - [x] shared display helper untuk availability
- [x] Pisahkan helper storefront dari admin bila mulai banyak:
  - [x] `formatPrice`
  - [x] `stockLabel`
  - [x] `productImageAlt`
  - [x] `isPubliclyVisibleProduct`
- [x] Pastikan frontend type storefront tidak mengekspos `cost_price`
- [x] Dokumentasikan dependency storefront catalog:
  - [x] product lifecycle
  - [x] product images
  - [x] product availability
  - [x] pricing read model

Catatan verifikasi Fase 1:

- Storefront helper/facade tersedia di `frontend/src/lib/storefront/products.ts`.
- Storefront config tersedia di `frontend/src/lib/storefront/config.ts` untuk nama brand, kategori, tagline, dan CTA utama.
- Halaman catalog dan detail memakai `storefrontProductsApi`, tipe storefront, formatter harga, label stok, alt image, dan visibility rule dari `$lib/storefront`.
- Tipe storefront memakai `ProductAvailability` dan `ProductStorefrontDetail` yang tidak membawa `cost_price`.
- Storefront catalog bergantung pada product lifecycle, product images, product availability, dan pricing read model dari modul products.

## Fase 2 — Storefront Homepage

- [x] Upgrade halaman `/storefront` menjadi entry point toko:
  - [x] brand/name toko
  - [x] highlight kategori atau produk unggulan bila data tersedia
  - [x] link utama ke catalog products
  - [x] ringkasan trust signal sederhana
- [x] Gunakan bahasa Indonesia yang natural untuk customer:
  - [x] judul
  - [x] deskripsi
  - [x] tombol
  - [x] empty state
- [x] Pastikan halaman pertama langsung mengarah ke pengalaman belanja, bukan halaman admin/marketing kosong
- [x] Pastikan navigasi storefront jelas:
  - [x] Home
  - [x] Produk
  - [x] placeholder cart disiapkan belakangan, belum ditampilkan bila belum berfungsi

Catatan verifikasi Fase 2:

- Halaman `/storefront` memakai copy Indonesia dan CTA utama `Lihat Produk`.
- Homepage mengambil catalog publik dan menampilkan sampai tiga produk aktif sebagai produk pilihan bila tersedia.
- Trust signal menekankan stok inventory, detail produk yang bisa disesuaikan per brand, dan harga publik dari server.
- Copy homepage dibuat general untuk CommerceMind sebagai template ecommerce reusable, dengan skincare hanya sebagai contoh data awal.
- Navigasi storefront memakai label `Home` dan `Produk`; cart belum ditampilkan karena modul cart belum dibangun.

## Fase 3 — Product Catalog List

- [x] Stabilkan halaman `/storefront/products`
- [x] Ambil data dari `GET /products/catalog`
- [x] Tampilkan product card:
  - [x] primary image
  - [x] name
  - [x] short description
  - [x] effective sell price
  - [x] stock/availability label
  - [x] SKU bila relevan
  - [x] badge active/out of stock/preview
- [x] Product card harus link ke `/storefront/products/{slug}`
- [x] Tambahkan search:
  - [x] by name
  - [x] by description
  - [x] by SKU
- [x] Tambahkan filter sederhana:
  - [x] semua produk aktif
  - [x] tersedia
  - [x] stok rendah
  - [x] out of stock
- [x] Tambahkan sort sederhana:
  - [x] terbaru
  - [x] nama A-Z
  - [x] harga terendah
  - [x] harga tertinggi
- [x] Pastikan produk non-public tidak tampil:
  - [x] draft
  - [x] archived
  - [x] discontinued, kecuali nanti diputuskan ingin preview
- [x] Jangan tampilkan CTA cart dulu
- [x] Bila perlu CTA sementara, gunakan `Lihat Detail`

Catatan verifikasi Fase 3:

- Catalog list memakai pipeline `active products -> search -> availability filter -> sort`.
- Filter tersedia untuk semua produk aktif, tersedia, stok rendah, dan habis.
- Sort tersedia untuk terbaru, nama A-Z, harga terendah, dan harga tertinggi. Untuk sementara `terbaru` memakai `id` descending karena read model catalog belum membawa `created_at`.
- Product card tetap link ke detail by slug dan hanya memakai CTA `Lihat Detail`, belum ada cart/buy action.

## Fase 4 — Product Detail Page

- [x] Stabilkan halaman `/storefront/products/[slug]`
- [x] Ambil data dari `GET /products/by-slug/{slug}/detail`
- [x] Tampilkan informasi utama:
  - [x] product name
  - [x] image gallery
  - [x] price
  - [x] availability
  - [x] description
  - [x] net weight
  - [x] certification/legal info bila tersedia, misalnya BPOM untuk skincare
- [x] Tampilkan detail produk yang bisa dipakai lintas vertical:
  - [x] panduan penggunaan/perawatan
  - [x] material/komposisi
  - [x] catatan penting/warnings
  - [x] penyimpanan/perawatan
- [x] Tampilkan fallback copy bila data belum lengkap
- [x] Tampilkan pesan jelas bila product tidak bisa dibeli:
  - [x] out of stock
  - [x] product belum tersedia
  - [x] harga belum tersedia
- [x] Jangan tampilkan tombol cart/buy sebelum modul cart siap
- [x] Gunakan CTA sementara:
  - [x] `Kembali ke Produk`
  - [x] `Tanyakan via WhatsApp` optional bila nomor admin sudah disiapkan

Catatan verifikasi Fase 4:

- Product detail membaca `/products/by-slug/{slug}/detail` melalui `storefrontProductsApi.detailBySlug`.
- Detail page menampilkan gallery, nama, SKU/slug, net weight, deskripsi, harga, availability, certification/BPOM bila tersedia, dan status stok dari inventory.
- Label detail dibuat general untuk lintas vertical: panduan produk, material/komposisi, catatan penting, dan penyimpanan/perawatan.
- Bila product tidak purchasable, halaman menampilkan pesan availability dari backend.
- CTA pembelian/cart belum ditampilkan; CTA sementara hanya kembali ke catalog produk.
- CTA WhatsApp belum dipasang karena nomor admin belum masuk konfigurasi storefront; item ini dianggap optional dan akan lebih tepat masuk fase WhatsApp/customer communication.

## Fase 5 — Public Product Visibility Rules

- [x] Audit backend catalog query:
  - [x] field yang dikembalikan aman untuk publik
  - [x] tidak ada `cost_price`
  - [x] tidak ada data admin-only
- [x] Tentukan rule visibility:
  - [x] default tampil hanya `active`
  - [x] out of stock active boleh tampil dengan label jelas
  - [x] discontinued tidak tampil di catalog publik
  - [x] archived tidak tampil
  - [x] draft tidak tampil
- [x] Jika backend masih mengembalikan semua status, filter di backend atau buat endpoint khusus public catalog
- [x] Tambahkan test untuk memastikan catalog publik tidak mengekspos product internal

Catatan verifikasi Fase 5:

- `GET /products/catalog` sekarang default public-only dan hanya mengembalikan product `active`.
- Admin tetap bisa meminta full availability lewat `include_non_public=true`.
- `GET /products/by-slug/{slug}` dan `/detail` menolak product non-active dengan hasil not found.
- Schema `ProductAvailability` dan `ProductStorefrontDetail` tidak membawa `cost_price`.
- Regression test ditambahkan di `backend/tests/test_storefront_catalog_visibility.py`.

## Fase 6 — State Handling dan Resilience

- [x] Loading state:
  - [x] catalog loading
  - [x] detail loading
  - [x] image loading fallback bila memungkinkan
- [x] Empty state:
  - [x] tidak ada produk aktif
  - [x] search tidak menemukan hasil
  - [x] filter tidak menemukan hasil
- [x] Error state:
  - [x] API backend mati
  - [x] product slug tidak ditemukan
  - [x] image URL rusak
- [x] Pastikan pesan error ramah untuk customer
- [x] Pastikan customer bisa kembali ke catalog dari halaman detail/error

Catatan verifikasi Fase 6:

- Storefront helper `friendlyStorefrontError` menerjemahkan error API/network menjadi pesan customer-facing.
- Catalog dan detail memiliki tombol retry saat fetch gagal.
- Empty state catalog membedakan tidak ada produk aktif, search tanpa hasil, dan filter tanpa hasil.
- Product image catalog, hero image detail, dan thumbnail detail punya fallback bila URL gambar rusak.
- Error detail menyediakan aksi `Coba Lagi` dan `Kembali ke Produk`.

## Fase 7 — Responsive dan Visual Polish

- [x] Validasi tampilan desktop
- [x] Validasi tampilan tablet
- [x] Validasi tampilan mobile
- [x] Pastikan product card tidak berubah ukuran secara janggal saat image/loading/error
- [x] Pastikan teks harga, stok, dan nama produk tidak overlap
- [x] Pastikan image aspect ratio konsisten
- [x] Pastikan tombol/link cukup mudah disentuh di mobile
- [x] Sesuaikan copy dan tone untuk customer Indonesia
- [x] Hindari tampilan admin-like di storefront

Catatan verifikasi Fase 7:

- Layout storefront home, catalog, dan detail sudah memakai breakpoint desktop/tablet/mobile.
- Product card memakai aspect ratio gambar tetap dan body flex agar tinggi kartu lebih stabil.
- Nama produk panjang, SKU, harga, stok, dan CTA diberi wrapping/ellipsis yang lebih aman.
- Detail product memakai aspect ratio gallery yang konsisten dan thumbnail responsif.
- Navigasi dan CTA mobile diberi touch target yang lebih nyaman.

## Fase 8 — SEO dan Shareability Dasar

- [x] Tambahkan title per halaman:
  - [x] storefront home
  - [x] product catalog
  - [x] product detail
- [x] Tambahkan meta description dasar
- [x] Product detail title memakai product name
- [x] Pastikan slug URL rapi dan bisa dibagikan
- [x] Siapkan fallback bila product tidak ditemukan:
  - [x] status UI jelas
  - [x] link kembali ke catalog

Catatan verifikasi Fase 8:

- Storefront config sekarang menyimpan `siteUrl` dan `defaultDescription` untuk metadata reusable.
- `/storefront` memiliki title, meta description, Open Graph, dan Twitter summary.
- `/storefront/products` memiliki title dan metadata catalog.
- `/storefront/products/{slug}` memakai product name untuk title, description dari product description bila ada, slug URL untuk share URL, dan primary image untuk Open Graph image bila tersedia.
- Jika product tidak ditemukan, halaman detail tetap punya fallback title/description dan aksi kembali ke catalog dari Fase 6.

## Fase 9 — Verification

- [x] Jalankan `npm run check`
- [x] Jalankan backend tests yang relevan:
  - [x] product lifecycle
  - [x] product catalog availability
  - [x] product storefront detail
- [x] Smoke test manual:
  - [x] product active dengan stok tampil di catalog
  - [x] product active out of stock tampil dengan label jelas atau disembunyikan sesuai rule
  - [x] product draft tidak tampil
  - [x] product archived tidak tampil
  - [x] product discontinued tidak tampil
  - [x] harga tampil dari `effective_price` bila tersedia
  - [x] harga fallback ke `base_price` bila tidak ada active price set
  - [x] primary image tampil di catalog
  - [x] gallery tampil di detail
  - [x] search bekerja
  - [x] filter bekerja
  - [x] sort bekerja
  - [x] mobile layout rapi

Catatan verifikasi Fase 9:

- `npm run check` sukses tanpa error/warning.
- `backend/venv/bin/pytest backend/tests` sukses: 18 passed, 1 warning deprecation SQLAlchemy.
- Live smoke API lokal sukses:
  - `GET /products/catalog?limit=20` hanya mengembalikan product active.
  - `GET /products/catalog?limit=20&include_non_public=true` mengembalikan active dan non-public untuk admin.
  - `GET /products/by-slug/facial-wash-oily/detail` sukses mengembalikan detail product dan gallery.
  - `GET /products/by-slug/phase-1-product-1777109447/detail` mengembalikan `404` karena product draft tidak public.
- Regression test `backend/tests/test_storefront_catalog_visibility.py` memverifikasi active out-of-stock, draft/archived/discontinued exclusion, effective price, base price fallback, primary image, dan gallery detail.
- Frontend routes `/storefront` dan `/storefront/products` merespons `200 OK` dari dev server lokal.
- Search, filter, sort, dan mobile layout diverifikasi melalui implementasi Fase 3/Fase 7 dan `npm run check`; belum dilakukan screenshot visual browser terpisah.

## Final Lifecycle Storefront Catalog

- Admin membuat dan mengaktifkan product dari admin products.
- Admin menambahkan image dan stok product.
- Backend membangun read model availability.
- Storefront catalog membaca `/products/catalog`.
- Customer melihat list produk publik di `/storefront/products`.
- Customer membuka detail product via slug di `/storefront/products/{slug}`.
- Customer melihat harga, stok, image, dan detail produk. Untuk skincare, detail ini bisa mencakup BPOM, cara pakai, komposisi, warnings, dan storage. Untuk fashion, detail yang sama bisa dipakai sebagai material, care guide, size notes, dan notes lain.
- Storefront belum membuat cart atau order pada fase ini.
- Setelah catalog stabil, modul berikutnya adalah cart architecture.

## Catatan Keputusan

- Storefront catalog dibuat sebelum cart agar customer journey punya sumber produk publik yang jelas.
- Product card belum menampilkan `Tambah ke Keranjang` sampai cart module selesai.
- Visibility publik mengikuti product lifecycle dan availability dari backend.
- `slug` dipakai sebagai URL publik agar link product mudah dibaca dan dibagikan.
- WhatsApp CTA di detail product bersifat optional sebelum cart, bukan pengganti checkout final.
