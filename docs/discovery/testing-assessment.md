# Testing Assessment

**Tanggal inspeksi statis:** 10 November 2026
**Catatan:** bagian discovery statis dibuat tanpa menjalankan test. Hasil runtime TASK 5.5 dicatat terpisah di bagian 8 berdasarkan output yang diberikan.

## 1. Testing Stack and Configuration

- Framework backend: **pytest**, tercantum di `backend/pyproject.toml` dan `backend/requirements.txt`.
- Konfigurasi pytest di `pytest.ini` menetapkan `pythonpath = .` dan `testpaths = backend/tests`.
- Tidak ditemukan `conftest.py`, konfigurasi pytest tambahan, atau konfigurasi test frontend pada file konfigurasi yang diperiksa.
- `frontend/package.json` menyediakan script `dev`, `build`, `preview`, `check`, dan `check:watch`; tidak ada script `test` dan tidak ada dependency test runner seperti Vitest, Jest, atau Playwright yang dideklarasikan di manifest tersebut.
- Pencarian file frontend tidak menemukan file `*.test.*`, `*.spec.*`, atau direktori test umum. Kesimpulan ini dibatasi pada file yang ada di repository dan pola pencarian tersebut.

## 2. Existing Test Structure

Direktori `backend/tests/` memiliki 10 file Python dengan total **49 fungsi bernama `test_*`** yang dihitung dari source. Angka ini adalah hitungan statis, bukan hasil eksekusi.

- `backend/tests/test_customer_schema.py`
- `backend/tests/test_customer_addresses.py`
- `backend/tests/test_customer_admin_api.py`
- `backend/tests/test_customer_checkout_hooks.py`
- `backend/tests/test_inventory_lifecycle.py`
- `backend/tests/test_module_flags.py`
- `backend/tests/test_platform_security.py`
- `backend/tests/test_platform_settings.py`
- `backend/tests/test_product_reporting.py`
- `backend/tests/test_storefront_catalog_visibility.py`

Test mencakup schema/customer, aturan alamat, handler customer admin, helper customer checkout, lifecycle order-inventory-payment, feature flags, role guard/settings, reporting produk, dan aturan visibilitas katalog.

## 3. Test Coverage by Module

Status berikut mengukur keberadaan test relevan, bukan kelengkapan atau keberhasilan test. Sebagian besar test domain memanggil fungsi CRUD/helper langsung; beberapa memanggil fungsi handler FastAPI langsung, bukan mengirim HTTP melalui aplikasi.

| Module | Status | Evidence and Coverage Limits |
|---|---|---|
| Product Management | **Partially Tested** | Katalog, status publik, availability, harga efektif, gambar utama/gallery diuji pada `test_storefront_catalog_visibility.py`; penentuan harga dan penolakan produk nonaktif juga diuji dalam `test_inventory_lifecycle.py`. CRUD UI produk, lifecycle endpoint CRUD secara lengkap, serta add/update/delete/set-primary image tidak ditemukan test khusus. |
| Customers | **Has Tests** | Schema, guest/registered, brand scope, password hash exposure, address CRUD/default/isolation, customer summary/detail/list/update, serta helper checkout customer/address tercakup dalam empat file customer. Tidak mencakup alur login atau public checkout end-to-end. |
| Orders | **Partially Tested** | Pembuatan order, pembatalan, perubahan lifecycle terkait pembayaran dan fulfillment diuji melalui fungsi domain di `test_inventory_lifecycle.py`; sebagian dipakai juga oleh fixtures test reporting. Tidak ditemukan cakupan menyeluruh semua endpoint list/detail/update/status/delete order melalui HTTP. |
| Order Items | **Partially Tested** | Pembuatan item lewat `create_order` dan snapshot produk/harga diuji pada `test_inventory_lifecycle.py`; perilaku order item terlibat tidak langsung dalam reporting. Tidak ditemukan test khusus untuk endpoint/CRUD baca, update, dan delete order item. |
| Payments | **Partially Tested** | Status paid/failed/refunded serta interaksi reservation/order diuji dalam `test_inventory_lifecycle.py`; flag payments disabled diuji pada `test_module_flags.py`. Tidak ditemukan test menyeluruh untuk seluruh endpoint payment read/update/delete atau integrasi gateway eksternal. |
| Inventory | **Has Tests** | Receive, reserve, release, commit/deduction, adjustment invariant, rollback saat stok kurang, payment failure, refund, dan return tercakup pada `test_inventory_lifecycle.py`. Pengujian terutama domain service/CRUD, bukan kontrak HTTP inventory lengkap. |
| Reporting | **Partially Tested** | Gross revenue/margin berbasis snapshot serta low-stock, slow-moving, dan discontinued-with-stock diuji di `test_product_reporting.py`. Endpoint report, seluruh bentuk pagination/empty cases, dan konsumsi UI tidak ditemukan sebagai cakupan test. |
| Platform Settings and Brand Management | **Has Tests** | Default settings, update/public config, isolasi brand, role guard, brand access, dan audit log diuji di `test_platform_settings.py` serta `test_platform_security.py`. Tidak semua endpoint brand/settings diuji melalui HTTP. |
| Storefront | **Partially Tested** | Filter status katalog, detail slug, out-of-stock label, effective/base price, primary image/gallery, isolasi brand, serta flag public catalog diuji pada `test_storefront_catalog_visibility.py` dan `test_module_flags.py`. Tidak ditemukan test komponen/route Svelte atau browser. |

**Frontend terpisah:** tidak ditemukan automated test untuk Admin Dashboard, storefront UI, console UI, atau API client frontend dalam struktur frontend yang diperiksa.

## 4. Existing Test Case Inventory

Daftar di bawah merangkum test berdasarkan isi assertion dan fungsi yang dipanggil. Nama test dan keberadaan assertion diverifikasi lewat pembacaan source; test tidak dijalankan pada task ini.

### Customer schema — `backend/tests/test_customer_schema.py`

- `test_guest_customer_can_be_created_without_email` — menerima guest tanpa email dan memeriksa lookup email kosong.
- `test_registered_customer_can_have_email` — membuat registered customer dengan email dan memeriksa lookup.
- `test_customer_brand_scope_isolated` — memastikan daftar customer terpisah menurut brand.
- `test_customer_type_validation` — menolak tipe customer yang tidak dikenal melalui Pydantic validation.
- `test_password_hash_is_not_exposed_in_customer_schema` — memastikan `password_hash` tidak ada pada hasil schema publik.
- Interaksi: schema, CRUD customer/settings/brand dan SQLite; bukan HTTP API.

### Customer addresses — `backend/tests/test_customer_addresses.py`

- `test_customer_address_can_be_created_for_brand_scoped_customer` — membuat alamat untuk customer dan memeriksa brand/default/address fields.
- `test_only_one_default_address_per_customer` — alamat baru yang diset default menggantikan alamat default sebelumnya.
- `test_updating_default_address_clears_previous_default` — update default membersihkan default lama.
- `test_customer_addresses_are_isolated_by_brand` — memeriksa isolasi lookup serta respons 404 ketika handler alamat dipanggil memakai brand yang salah.
- `test_customer_address_requires_checkout_fields` — menolak field checkout wajib yang kosong melalui schema validation.
- Interaksi: CRUD, schema, dan pemanggilan langsung handler `read_customer_addresses`; tidak memakai HTTP client.

### Customer admin API — `backend/tests/test_customer_admin_api.py`

- `test_customer_list_search_and_type_filter_are_brand_scoped` — pencarian, filter guest/registered, dan isolasi brand.
- `test_customer_summary_includes_order_metrics` — jumlah order, total spent, dan tanggal order terakhir.
- `test_customer_detail_includes_addresses_and_recent_orders` — alamat, order terbaru, status order, dan penyembunyian password hash.
- `test_customer_detail_rejects_other_brand` — detail lintas brand menghasilkan 404.
- `test_customer_update_is_brand_scoped` — update customer dengan brand yang tidak cocok menghasilkan 404.
- Interaksi: fungsi handler `read_customers`, `read_customer_summaries`, `read_customer_detail`, dan `update_customer` dipanggil langsung; database SQLite.

### Customer checkout hooks — `backend/tests/test_customer_checkout_hooks.py`

- `test_resolve_checkout_customer_creates_guest_without_email` — membuat guest tanpa email.
- `test_resolve_checkout_customer_reuses_phone_and_updates_more_complete_data` — memakai ulang customer berdasar phone dan memperbarui data lebih lengkap.
- `test_resolve_checkout_customer_does_not_attach_email_owned_by_same_brand` — mencegah penggunaan email yang telah dimiliki customer lain dalam brand sama.
- `test_resolve_checkout_customer_does_not_mix_brands` — phone sama pada brand berbeda menghasilkan customer berbeda.
- `test_resolve_checkout_address_creates_default_first_address` — alamat pertama otomatis menjadi default.
- `test_resolve_checkout_address_reuses_matching_address` — alamat cocok dipakai ulang agar tidak duplikat.
- `test_resolve_checkout_address_rejects_customer_from_other_brand` — alamat tidak dibuat jika customer bukan milik brand yang diminta.
- Interaksi: fungsi helper CRUD langsung dan SQLite; tidak menguji endpoint public checkout karena endpoint tersebut tidak ditemukan dalam test ini.

### Inventory, Order, and Payment Lifecycle — `backend/tests/test_inventory_lifecycle.py`

- `test_create_order_with_enough_stock_reserves_inventory` — order dengan stok cukup membuat reservation, total, snapshot item, dan status awaiting payment.
- `test_create_order_ignores_client_price_and_uses_price_set` — harga dari client diabaikan dan harga aktif dari price set dipakai.
- `test_create_order_rejects_non_active_product` — produk discontinued ditolak dan order tidak dibuat.
- `test_create_order_with_insufficient_stock_rolls_back` — stok kurang menolak order dan memeriksa tidak ada reservation/order parsial.
- `test_cancel_order_releases_reservation` — cancel melepas reservation tanpa mengurangi stok fisik.
- `test_payment_failed_releases_reservation` — payment failed melepas reservation dan mengubah order menjadi cancelled.
- `test_fulfillment_deducts_on_hand_quantity` — fulfillment mengurangi stok fisik, menutup reservation, dan mencatat deduction movement.
- `test_refund_does_not_automatically_restock` — refund tidak otomatis mengembalikan stok atau membuat movement return.
- `test_return_receive_stock_adds_stock_back` — receive stock dengan referensi return menaikkan stok kembali.
- `test_inventory_aggregate_invariant_blocks_invalid_adjustment` — adjustment yang membuat stok fisik lebih kecil dari reservation ditolak dan state tetap konsisten.
- Interaksi: CRUD/domain service order, payment, inventory, model dan SQLite; bukan endpoint HTTP.

### Module flags — `backend/tests/test_module_flags.py`

- `test_public_catalog_disabled_rejects_public_catalog_endpoint` — handler katalog mengembalikan 403 saat katalog publik mati; mode include-non-public/admin preview tetap mengembalikan produk.
- `test_payments_disabled_rejects_payment_endpoint` — handler create payment menolak operasi dengan 403 saat modul payments nonaktif.
- Interaksi: handler `read_product_catalog` dan `api_create_payment` dipanggil langsung bersama CRUD/settings serta SQLite; tidak menggunakan `TestClient`.

### Platform security — `backend/tests/test_platform_security.py`

- `test_platform_access_requires_platform_operator_role` — role kosong menghasilkan 401, merchant role menghasilkan 403, platform operator memperoleh context.
- `test_merchant_brand_access_requires_matching_brand` — brand cocok diterima dan brand berbeda menghasilkan 403.
- `test_platform_setting_update_writes_audit_log` — handler update storefront brand-scoped memperbarui setting dan merekam actor/action/before/after.
- Interaksi: fungsi guard dan handler dipanggil langsung; dua test guard tidak memakai database, satu test memakai SQLite.

### Platform settings — `backend/tests/test_platform_settings.py`

- `test_get_platform_settings_creates_defaults` — pembacaan settings membuat nilai default yang diharapkan.
- `test_update_settings_and_public_config_exposes_only_safe_fields` — update berbagai settings serta memeriksa public config tidak mengekspos field internal tertentu.
- `test_brand_scoped_settings_are_isolated` — update brand lain tidak mengubah konfigurasi default.
- Interaksi: fungsi CRUD/settings langsung dengan SQLite; bukan HTTP API.

### Product reporting — `backend/tests/test_product_reporting.py`

- `test_product_revenue_and_margin_reports_use_snapshots` — revenue dan estimated margin dihitung dari snapshot order item.
- `test_stock_reports_find_low_stock_slow_moving_and_discontinued` — menemukan produk low-stock, slow-moving, serta discontinued dengan stok.
- Interaksi: fungsi report, order, inventory dan CRUD dipanggil langsung dengan SQLite.

### Storefront catalog visibility — `backend/tests/test_storefront_catalog_visibility.py`

- `test_public_catalog_only_returns_active_products` — katalog publik hanya berisi produk active dan tidak mengekspos cost price.
- `test_admin_catalog_can_include_non_public_products` — katalog admin dapat memuat status non-public.
- `test_storefront_slug_detail_rejects_non_active_products` — lookup/detail slug tidak mengembalikan produk non-active.
- `test_public_catalog_keeps_active_out_of_stock_with_clear_label` — produk active tanpa stok tetap terlihat dengan status tidak purchasable dan alasan stok.
- `test_public_catalog_uses_effective_price_with_base_price_fallback` — memakai price set aktif atau fallback harga dasar.
- `test_storefront_detail_returns_primary_image_and_gallery` — detail memuat gambar utama dan urutan galeri.
- `test_brand_scoped_catalog_allows_same_slug_and_isolates_products` — slug sama diperbolehkan antar-brand dan lookup tetap terisolasi.
- Interaksi: fungsi CRUD catalog/detail langsung dengan SQLite; bukan browser atau frontend route.

## 5. Test Fixtures and Database Strategy

- Setiap file test mendefinisikan fixture lokal `db_session`; tidak ditemukan fixture bersama di `conftest.py`.
- Fixture membuat engine `sqlite:///:memory:`, membuat tabel melalui `Base.metadata.create_all`, membuka SQLAlchemy session, lalu menutup session setelah test.
- Test umumnya membuat data fixture sendiri melalui model/CRUD, sehingga tidak mengarah ke database PostgreSQL development yang diatur di `backend/database.py`.
- Tidak ditemukan mock, `unittest.mock`, `monkeypatch`, `mocker`, atau stub service eksternal pada direktori test yang diperiksa.
- Sejumlah test memanggil fungsi handler FastAPI secara langsung dengan parameter dan `db` yang diberikan; tidak ditemukan penggunaan FastAPI `TestClient` atau client HTTP async pada test yang diperiksa.
- Karena database pengujian adalah SQLite in-memory, perilaku khusus PostgreSQL, migrasi, concurrency, dan konfigurasi produksi tidak dibuktikan oleh strategi test ini.

## 6. Initial Testing Gaps

- Tidak ditemukan automated test frontend, komponen Svelte, route browser, atau API client frontend.
- Tidak ditemukan test untuk alur UI admin dashboard, products, inventory, order, payment, console, atau customer admin secara browser end-to-end.
- Product API mutations seperti create/update/archive/discontinue/reactivate/delete tidak memiliki cakupan langsung yang terlihat; test produk berfokus pada catalog visibility dan pembentukan order.
- Product image API mutations add/update/delete/set-primary tidak ditemukan test langsung; hanya pembacaan primary image dan gallery yang diuji.
- Price set memiliki skenario pembacaan harga efektif dan penggunaan harga saat order, tetapi pengelolaan price set serta aturan channel/region tidak memiliki test yang ditemukan.
- Orders dan Order Items tidak memiliki cakupan menyeluruh endpoint CRUD/status melalui HTTP; skenario utama yang ditemukan berjalan lewat domain function.
- Payments tidak memiliki cakupan langsung untuk semua metode endpoint read/update/delete; integrasi payment gateway eksternal tidak ditemukan test.
- Inventory API belum terlihat diuji melalui HTTP; perilaku yang diuji terutama service/domain lifecycle.
- Reporting API endpoint/dashboard response model, pagination boundaries, data kosong, dan konsumsi UI tidak ditemukan dalam test.
- Platform API routing, middleware, serialization melalui HTTP, dan semua operasi brand/settings tidak diuji menyeluruh.
- Test database SQLite tidak memverifikasi kesetaraan skema dan perilaku dengan PostgreSQL atau penerapan Alembic migration.
- Ketiadaan test di area tersebut adalah hasil pencarian repository saat ini, bukan bukti bahwa seluruh pengujian manual atau eksternal tidak pernah dilakukan.

## 7. Items Requiring Runtime Verification

- Catatan historis di dokumen mencatat jumlah berbeda pada tahapan pengembangan: 18 passed (`docs/archive/initial-planning/todo_storefront_catalog_architecture.md`), 27 passed (`docs/archive/initial-planning/todo_platform_console_architecture.md`), kemudian 37, 42, dan 49 passed (`docs/archive/initial-planning/todo_customer_architecture.md`). Angka-angka ini tetap merupakan catatan dokumentasi lama; hasil runtime TASK 5.5 saat ini dicatat terpisah di bagian 8.
- Bila tahap berikutnya menyetujui, verifikasi test API melalui TestClient/HTTP; test suite yang dilaporkan saat ini memanggil sebagian handler secara langsung.
- Periksa kesesuaian hasil SQLite dengan PostgreSQL untuk constraint, tipe data, transaction behavior, dan query report.
- Verifikasi browser/UI serta alur integrasi frontend-backend secara terpisah; tidak ada hasil tersebut dalam penilaian statis ini.

## 8. Runtime Verification Results

Hasil berikut dicatat dari output eksekusi yang diberikan untuk TASK 5.5. Ini merupakan verifikasi runtime terpisah dari inspeksi statis dan catatan historis pada bagian sebelumnya.

**Command:**

```bash
DATABASE_URL=sqlite:///:memory: backend/venv/bin/python -m pytest
```

**Hasil:**

- Pytest mengoleksi 49 item.
- 49 test berhasil (`49 passed`).
- Terdapat 1 warning.
- Durasi yang dilaporkan: 3.51 detik.

**Environment yang dilaporkan:**

- Python 3.8.10
- pytest 8.3.5
- pluggy 1.5.0
- anyio 4.5.2

**Warning:**

- Jenis: `MovedIn20Warning` dari SQLAlchemy.
- Lokasi sumber: `backend/database.py:12`.
- Berkaitan dengan penggunaan `declarative_base()` dari API SQLAlchemy lama.
- Warning tidak menyebabkan test gagal.
- Warning hanya dicatat; tidak ada perbaikan kode pada task ini.

Hasil ini hanya menyatakan bahwa 49 automated test yang dikoleksi berhasil dalam environment dan konfigurasi command tersebut. Ini tidak menyatakan seluruh aplikasi telah diuji, seluruh fitur bebas bug, atau perilaku PostgreSQL/browser telah diverifikasi.

## 9. Testing Gap Analysis

Analisis di bawah menggunakan test case yang benar-benar dipanggil, termasuk cakupan tidak langsung. “Belum ditemukan” berarti tidak ada test untuk perilaku/lapisan tersebut pada source test yang diperiksa; ini bukan klaim bahwa test manual atau eksternal tidak pernah ada.

| Module | Tested Behavior and Layer | Identified Gaps | Current Coverage Limitations |
|---|---|---|---|
| Product Management | Domain/CRUD: public catalog hanya active, admin preview non-public, availability out-of-stock, effective price/fallback, detail image gallery; order lifecycle juga menguji harga price set dan penolakan produk non-active. Bukti: `test_storefront_catalog_visibility.py`, `test_inventory_lifecycle.py`. | Belum ditemukan test create/update/delete product API, archive/discontinue/reactivate endpoint, delete blockers, atau mutation image add/update/remove/set-primary. Aturan date/channel/region pada pricing juga belum diuji. | Test memanggil CRUD/helper secara langsung; bukan API HTTP atau admin UI. Image coverage memeriksa read/detail, bukan mutasi.
| Customers | Schema/CRUD: guest tanpa email, registered email, phone reuse, alamat default/reuse, validasi field, isolasi brand. Handler langsung: list/filter/summary/detail/update dan 404 lintas brand. Bukti: empat file test customer. | Belum ditemukan HTTP-level test untuk customer/address endpoints, termasuk create/delete endpoint, address update/delete, serta authentication/authorization customer. | Banyak jalur dites lewat CRUD; handler terpilih dipanggil langsung tanpa routing, dependency override, middleware, atau serialization HTTP. Checkout hooks diuji sebagai helper, bukan checkout publik.
| Orders | Domain: create order sukses, harga server-side, status produk ditolak, insufficient stock rollback, cancel melepas reservation, fulfillment. Bukti: `test_inventory_lifecycle.py`; report tests juga membangun order sebagai data setup. | Belum ditemukan test handler HTTP untuk list/detail/update/status/delete, transisi status yang tidak dicakup, order tanpa item, duplicate/repeated action, dan transaksi beberapa item ketika salah satu item gagal. | Cakupan utama melalui fungsi domain; jalur validasi request/API dan concurrency tidak diuji.
| Order Items | Tidak langsung: pembuatan order membentuk item, menghitung subtotal dan menyimpan product/price snapshots; reporting membaca item snapshots. Bukti: `test_inventory_lifecycle.py`, `test_product_reporting.py`. | Belum ditemukan test langsung untuk route/CRUD list, get, update, delete order item atau konsistensi total order setelah item diubah/dihapus. | Tidak ada test file khusus bukan satu-satunya dasar gap; gap disimpulkan dari isi seluruh test yang diperiksa.
| Payments | Domain: paid/failed/refunded lifecycle, relasi ke order dan reservation; handler langsung: create payment ditolak saat payments module disabled. Bukti: `test_inventory_lifecycle.py`, `test_module_flags.py`. | Belum ditemukan HTTP-level test seluruh payment routes, aturan nominal pembayaran terhadap total order, duplicate payment/transition berulang, atau kasus update/delete dan order state boundary. Gateway eksternal tidak ditemukan dalam implementasi yang diperiksa. | Test berfokus pada efek domain, bukan alur request HTTP atau integrasi provider pembayaran.
| Inventory | Domain/SQLite: receive, reservation, release, commit/deduction, insufficient stock rollback, invariant reserved ≤ on-hand, payment failure, return/refund, dan audit movement. Bukti: `test_inventory_lifecycle.py`. | Belum ditemukan HTTP-level test untuk seluruh `/inventory-items/*`, pagination/read endpoints, error mapping, concurrency/locking, reservation expiry, atau operasi berulang terhadap reservation non-active. | Logika utama diuji terhadap SQLite in-memory; locking dan perilaku PostgreSQL tidak tercakup.
| Reporting | Domain/CRUD: revenue dan margin dari snapshot; laporan low-stock, slow-moving, discontinued-with-stock. Bukti: `test_product_reporting.py`. | Belum ditemukan test handler `/reports/*`, `get_product_reporting_dashboard`, pagination/batas, dataset kosong, serta filter brand pada seluruh report route. Tidak ditemukan UI report untuk diuji. | Query langsung diuji dengan data SQLite kecil; akurasi query dan performa pada volume/data PostgreSQL belum diketahui.
| Platform Settings and Brand Management | CRUD/handler langsung: defaults, update/public config field exposure, isolasi settings per brand, role guard, brand guard, audit log. Bukti: `test_platform_settings.py`, `test_platform_security.py`. | Belum ditemukan HTTP-level coverage semua route brand/settings, autentikasi dependency wiring per route, role selain yang diuji, dan validasi/error paths seluruh operasi brand. | Guard dites langsung dan satu handler settings dipanggil langsung; test tidak mengirim request ke aplikasi FastAPI.
| Storefront | Domain/CRUD: visibility, slug detail, availability, price/image, isolasi brand; handler langsung: public catalog disabled dan admin preview. Bukti: `test_storefront_catalog_visibility.py`, `test_module_flags.py`. | Belum ditemukan test route/komponen Svelte untuk loading/error/retry, search/filter/sort, responsive behavior, metadata, konfigurasi storefront, atau navigasi browser. | Backend catalog tests tidak memverifikasi interaksi frontend dengan API. Cart/checkout tidak ditemukan sebagai implementasi end-to-end dan bukan sekadar test yang tertinggal.
| Admin Dashboard | Tidak ditemukan test khusus; halaman yang diperiksa menggunakan data statis dan tidak memanggil Reporting API. Bukti discovery: `frontend/src/routes/admin/+page.svelte`, `docs/discovery/existing-modules.md`. | Tidak ada test frontend untuk render dashboard, tombol, atau perlindungan agar angka statis tidak disalahartikan sebagai data runtime. Tidak ada integrasi dashboard-report karena integrasi tersebut tidak ditemukan. | Ini adalah gap pengujian UI untuk implementasi tampilan saat ini; integrasi analytics tidak boleh diuji seolah sudah tersedia.

### Cross-Module Coverage

- **API HTTP:** tidak ditemukan `TestClient` atau client HTTP dalam test suite; beberapa handler FastAPI dipanggil langsung. Karena itu status code pada pemanggilan fungsi tertentu telah diuji, tetapi routing, dependency injection, middleware, request parsing, response serialization, dan CORS belum dibuktikan oleh test ini.
- **Frontend:** tidak ditemukan automated test component, route, atau browser.
- **Database:** test memakai SQLite in-memory. Ini mengisolasi data aplikasi tetapi tidak memverifikasi PostgreSQL, Alembic migration, locking, atau concurrency.
- **Efek eksternal:** source test tidak menunjukkan pemanggilan external API/service; tidak ada mock service eksternal yang ditemukan.

## 10. Testing Gap Prioritization

Prioritas ini adalah analisis risiko dari jalur kode yang ditemukan, bukan hasil insiden atau bukti bahwa bug sudah terjadi.

### High

- **Integritas order-inventory-payment lintas kegagalan dan retry.** Order create menghitung total dari harga produk, membuat reservation, dan mengubah status; cancel/payment failure melepas reservation; fulfillment mengurangi stok (`backend/crud/orders.py`, `backend/crud/inventory_service.py`, `backend/crud/payments.py`). Test sudah mencakup jalur utama dan rollback insufficient stock, tetapi belum mencakup beberapa item dengan kegagalan parsial, pengulangan aksi, idempotensi, atau konkurensi. Kesalahan pada area ini berpotensi mengubah saldo stok/order/payment secara tidak konsisten.
- **Isolasi brand dan otorisasi pada API.** Data produk, customer, order, payment, inventory, dan settings menggunakan konteks brand; test saat ini menguji beberapa kasus customer/storefront dan guard secara langsung, bukan wiring seluruh route melalui HTTP. Kegagalan scoping berpotensi mengekspos atau mengubah data tenant lain.
- **Kompatibilitas PostgreSQL dan schema migration.** Semua fixture menggunakan SQLite in-memory, sementara aplikasi menggunakan PostgreSQL. Test sukses di SQLite tidak membuktikan tipe, constraint, transaksi, query, dan migration bekerja sama pada database runtime; kesalahan di sini dapat memengaruhi data persisten.
- **Kebenaran harga dan payment di jalur order.** Test membuktikan harga price set dan fallback, tetapi tidak mencakup semua keadaan price set atau transisi payment berulang. Relasi antara `Payment.amount` dan `Order.total_amount` juga belum diuji; aturan bisnis yang diharapkan perlu dipastikan karena kedua nilai disimpan dan pelaporan memakai nilai order item. Ketidaksesuaian harga/status dapat berdampak pada total order dan laporan revenue.

### Medium

- **Mutation Product dan Product Images.** Test katalog membaca availability/image, tetapi belum menguji rangkaian tulis API. Kesalahan mutation dapat merusak katalog atau membuat primary image tidak sesuai.
- **API contract untuk Orders, Order Items, Inventory, Payments, dan Settings.** Domain test kuat pada beberapa jalur, namun HTTP routing/validasi/serialization/error mapping belum tercakup; dampaknya dapat berupa perilaku endpoint berbeda dari fungsi domain yang diuji.
- **Customer endpoint coverage dan alamat.** Banyak aturan domain customer telah diuji, tetapi sejumlah operasi endpoint create/delete serta address update/delete belum punya test HTTP. Dampak umumnya pada pengelolaan data customer/address.
- **Reporting query boundaries.** Perhitungan dasar diuji, tetapi report dashboard, data kosong, pagination, dan brand filter route belum ditemukan cakupannya; kesalahan dapat memberi laporan kosong atau ringkasan salah.
- **Storefront UI/API interaction.** Catalog backend diuji, tetapi state loading/error, filter/search, serta tampilan detail belum otomatis diuji; dampaknya terutama kegagalan perjalanan browsing yang luput dari domain tests.

### Low

- **Regression test untuk Admin Dashboard statis dan elemen UI pendukung.** Tidak ada test UI. Dampak data bisnis lebih rendah karena implementasi yang ditemukan berupa konstanta statis dan bukan metrik backend; nilai contoh tidak boleh dianggap sebagai analytics aktual.
- **Kelengkapan test frontend untuk state visual/accessibility dan API client.** Kesenjangan ini dapat menangkap regresi interaksi/presentasi, namun diprioritaskan setelah kontrak data dan proses bisnis berisiko tinggi.

## 11. Recommended Testing Strategy

Rekomendasi berikut adalah strategi untuk tahap lanjutan, bukan test yang dibuat atau dijalankan pada task ini. Untuk test yang mengakses database, gunakan SQLite in-memory untuk unit/domain, dan database PostgreSQL khusus test yang disposable untuk kompatibilitas; jangan arahkan test ke database development.

| Order | Area/Gap | Recommended Test Types | Focus |
|---|---|---|---|
| 1 | Order, Order Items, Inventory, Payments | Unit/domain test; API integration test; PostgreSQL compatibility test | Uji rollback multi-item, transisi ganda/berulang, interaksi paid/failed/refunded/cancel/fulfill, konsistensi reservation, kesesuaian nominal setelah aturan bisnis dipastikan, dan perilaku transaksi. API integration test memeriksa validasi request serta pemetaan error. |
| 2 | Isolasi brand dan access control | API integration test; database compatibility test; targeted end-to-end test | Uji route FastAPI aktual dengan konteks platform/merchant; verifikasi penolakan baca/tulis lintas brand untuk produk, customer, inventory, order, payment, dan settings. E2E dibatasi pada alur console/customer yang memang tersedia. |
| 3 | PostgreSQL dan migrasi | Database compatibility test | Jalankan pemeriksaan migrasi hanya pada database test sementara yang khusus; validasi constraint, index, transaksi, serta query report/catalog di PostgreSQL. Pisahkan database ini dari data development. |
| 4 | Product Management, Pricing, Product Images | Unit/domain test; API integration test; frontend component test; targeted end-to-end test | Uji transisi lifecycle/delete blockers, pemilihan/fallback price set, create/update/delete/set-primary gambar, serta respons form/API admin. E2E dapat memeriksa produk yang dibuat muncul pada storefront sesuai aturan publik. |
| 5 | Customers dan addresses | Unit/domain test; API integration test; frontend component test; targeted end-to-end test | Pertahankan kasus schema/helper yang ada; tambah test route aktual untuk mutasi customer/alamat, validasi, brand mismatch, dan kontrak response API. E2E dapat mencakup pengelolaan customer dalam lingkup brand oleh admin, bukan checkout/login publik yang belum tersedia. |
| 6 | Platform Brand Management dan Platform Settings | API integration test; frontend component test; targeted end-to-end test | Verifikasi wiring dependency/access pada route, default settings, create/update brand, public config aman, audit log, serta simpan/muat settings lewat console. |
| 7 | Reporting API | Unit/domain test; API integration test; PostgreSQL compatibility test | Tambahkan kasus data kosong, pagination, brand scope, agregasi dashboard, dan response schema. Belum ada rekomendasi E2E laporan sampai UI laporan tersedia. |
| 8 | Storefront dan Admin Dashboard | Frontend component test; targeted end-to-end test | Verifikasi state loading/error/empty, pencarian/filter/pengurutan, dan tampilan detail produk. Untuk dashboard saat ini, uji hanya tampilan statis dan pastikan data contoh diberi label dengan jelas; jangan menganggapnya metrik bisnis aktual. |

Perangkat frontend component/E2E test saat ini tidak tercantum di `frontend/package.json`; pemilihan atau penambahan framework/dependency merupakan perubahan terpisah yang memerlukan persetujuan. Hasil `49 passed` menjadi baseline yang berguna, tetapi bukan bukti bahwa seluruh aplikasi sudah tercakup.
