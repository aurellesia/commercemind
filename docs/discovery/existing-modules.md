# Existing Modules & Features (Initial Discovery)

**Tanggal inspeksi:** 22 Oktober 2026  
**Basis inspeksi:** pembacaan route frontend, API, CRUD/domain service, model, schema, README, dan dokumen arsitektur. Tidak ada tes atau operasi data yang dijalankan untuk task ini.

## 1. Purpose and Scope

Dokumen ini mencatat modul dan fitur yang ditemukan di implementasi CommerceMind pada inspeksi awal. Status menyatakan tingkat bukti kode, bukan jaminan bahwa fitur berfungsi tanpa cacat. Task ini tidak menjalankan browser, tes, endpoint, atau migrasi; hasil startup dan smoke HTTP sebelumnya hanya dirujuk sebagai konteks terpisah.

Status yang digunakan:

- **Implemented — unverified:** alur implementasi ditemukan pada frontend/backend, tetapi belum diverifikasi memadai dalam task ini.
- **Partial:** ada bagian implementasi, tetapi alur terkait belum lengkap atau masih berupa placeholder.
- **Not implemented:** area relevan diperiksa dan implementasi tidak ditemukan.
- **Not verified:** bukti belum cukup untuk menetapkan status.

## 2. Discovery Summary

Repository memiliki backend FastAPI dengan model data commerce multi-brand dan UI SvelteKit untuk platform console, merchant/admin, serta storefront. Backend mencakup katalog produk/gambar/harga, inventory dan reservation, customer/address, order/item, payment, reporting, serta konfigurasi brand/platform. UI yang paling nyata terhubung dengan API adalah console, products, inventory, customer admin brand-scoped, dan katalog storefront.

Beberapa area backend memiliki API/domain service tanpa UI operasional yang setara: orders, payments, dan reports. Dashboard `/admin` memakai data statis; halaman admin orders/payments hanya teks placeholder. Cart, checkout publik, customer account/login, shipping execution, dan order tracking tidak ditemukan sebagai alur end-to-end.

## 3. Module Inventory (Initial)

- **Product catalog & lifecycle**
  - Fitur: daftar/edit/buat/hapus produk; status draft/active/archive/discontinued; availability dan purchasability; galeri gambar.
  - Frontend: `/admin/products`, `/admin/products/images`; katalog/detail `/storefront/products/*` dan `/brands/[brandSlug]/products/*`.
  - Backend/data: `/products/*`; CRUD produk dan gambar; `products`, `product_images`, `price_sets`, `price_set_items`.
  - Status: **Implemented — unverified** untuk alur yang terhubung; tidak diuji end-to-end pada task ini.
- **Inventory**
  - Fitur: ringkasan stok, low-stock, penerimaan/penyesuaian, ledger movements, reservation/release/commit.
  - Frontend: `/admin/inventory`.
  - Backend/data: `/inventory-items/*`; `inventory_service.py`; `inventory_items`, `inventory_movements`, `inventory_reservations`.
  - Status: **Implemented — unverified**; UI dan domain service ditemukan, operasi tulis tidak diuji.
- **Customers**
  - Fitur: daftar/filter/search, detail, ringkasan order, profile dan address CRUD; helper resolve guest customer/address.
  - Frontend: `/brands/[brandSlug]/admin/customers`; `/admin/customers` redirect.
  - Backend/data: `/customers/*`; `crud/customers.py`; `customers`, `customer_addresses`.
  - Status: **Implemented — unverified** untuk admin/API; helper checkout customer ada, tetapi checkout publik **Partial**.
- **Orders & order items**
  - Fitur: CRUD order/item, status, cancel, fulfill; create order memeriksa customer/produk dan mengintegrasikan inventory.
  - Frontend: `/admin/orders` placeholder; brand-scoped order placeholder/link ke legacy.
  - Backend/data: `/orders/*`, `/orders/{id}/items`, `/order-items/*`; `orders`, `order_items`.
  - Status: Backend **Implemented — unverified**; UI admin **Partial**.
- **Payments**
  - Fitur: record payment per order, read/update/status/delete; lifecycle payment memengaruhi order/reservation; flag enablement.
  - Frontend: `/admin/payments` placeholder.
  - Backend/data: `/payments/*`; `payments`; satu payment per order dalam model.
  - Status: Backend **Implemented — unverified**; UI admin **Partial**. Integrasi gateway eksternal tidak ditemukan.
- **Reporting**
  - Fitur: product dashboard, summary, gross revenue, slow-moving, low-stock active, discontinued-with-stock.
  - Frontend: tidak ditemukan halaman report khusus di `frontend/src/routes/`.
  - Backend/data: `/reports/products*`; query di `crud/reports.py`.
  - Status: API **Implemented — unverified**; UI **Not implemented** pada area route yang diperiksa.
- **Platform console & tenant settings**
  - Fitur: Brand CRUD; brand/storefront/SEO/module/system settings; audit log API; storefront public config.
  - Frontend: `/console`, `/console/brands*`, `/console/settings`, `/console/storefront`, `/console/modules`, `/console/system`.
  - Backend/data: `/platform/brands*`, `/platform/settings*`, `/storefront/{slug}/config`; tabel brand/settings/audit.
  - Status: **Implemented — unverified**; tidak diuji alur simpan atau akses per role pada task ini.
- **Brand-scoped merchant admin**
  - Fitur: navigasi admin per brand; halaman customer berfitur; halaman products/inventory/orders berupa pengarah ke legacy default.
  - Frontend: `/brands/[brandSlug]/admin/*`.
  - Backend/data: sebagian endpoint menerima `brand_id`, tetapi beberapa operasi data lama/global tidak konsisten menggunakan konteks brand.
  - Status: **Partial**; UI customer terhubung, halaman lain menunjukkan porting belum selesai.
- **Storefront catalog**
  - Fitur: home, list, search/filter/sort, detail produk, gambar, harga/stok, brand config dan SEO metadata.
  - Frontend: `/storefront/*`, `/brands/[brandSlug]/*`.
  - Backend/data: `/storefront/{slug}/config`, `/products/catalog`, `/products/by-slug/{slug}/detail`.
  - Status: **Implemented — unverified** untuk baca katalog; perjalanan pembelian tidak lengkap.
- **Cart, checkout & customer account**
  - Fitur: flag konfigurasi dan UI conditional link/CTA ada.
  - Frontend: tidak ditemukan route cart/account; link hanya muncul bila flag terkait aktif.
  - Backend/data: tidak ditemukan endpoint cart/checkout/auth; ada schema/helper customer checkout di `backend/schema_models/customer.py` dan `backend/crud/customers.py`.
  - Status: **Partial** untuk integration hooks customer; cart/checkout/account end-to-end **Not implemented** pada area yang diperiksa.

## 4. Frontend Findings

### Routes and Main Pages

- `/` adalah landing pemilih area aplikasi yang menautkan Admin, Storefront, dan Console (`frontend/src/routes/+page.svelte`).
- `/admin` diarahkan ke `/brands/default/admin` melalui load redirect (`frontend/src/routes/admin/+page.ts`). `/admin/customers` diarahkan ke `/brands/default/admin/customers` (`frontend/src/routes/admin/customers/+page.ts`).
- `/admin/products` menyediakan tabel, pencarian, create/edit, detail, lifecycle actions, dan delete; `/admin/products/images` mengelola gambar. Bukti: `frontend/src/routes/admin/products/+page.svelte`, `frontend/src/routes/admin/products/images/+page.svelte`, `frontend/src/lib/api/products.ts`.
- `/admin/inventory` memuat tabel inventori, filter, receive/adjust, detail, dan aksi reservation. Bukti: `frontend/src/routes/admin/inventory/+page.svelte`, `frontend/src/lib/api/inventory.ts`.
- `/brands/[brandSlug]/admin/customers` memuat daftar/search/filter, drawer detail, dan form profile/address yang menggunakan customer API serta konfigurasi publik brand. Bukti: `frontend/src/routes/brands/[brandSlug]/admin/customers/+page.svelte`, `frontend/src/lib/api/customers.ts`.
- `/admin/orders` dan `/admin/payments` masing-masing hanya berisi heading dan teks bahwa workflow akan ditempatkan di sana (`frontend/src/routes/admin/orders/+page.svelte`, `frontend/src/routes/admin/payments/+page.svelte`). Brand-scoped orders/products/inventory juga menampilkan pesan porting dan tautan ke panel legacy (`frontend/src/routes/brands/[brandSlug]/admin/{orders,products,inventory}/+page.svelte`).
- `/console` menyediakan navigasi platform. Route brands membuat/mengelola brand; route settings, storefront, modules, dan system membaca serta menyimpan setting melalui `frontend/src/lib/api/platform-settings.ts`. UI menggunakan header role platform operator yang statis untuk integrasi lokal/development; bukan mekanisme login yang terlihat di frontend.
- `/storefront` dan `/brands/[brandSlug]` menampilkan homepage dan katalog. Daftar katalog menyediakan pencarian, filter availability, sorting, kartu produk; detail menampilkan harga, status stok, galeri, dan metadata SEO pada default storefront. Bukti: `frontend/src/routes/storefront/+page.svelte`, `frontend/src/routes/storefront/products/+page.svelte`, `frontend/src/routes/storefront/products/[slug]/+page.svelte`, serta padanan di `frontend/src/routes/brands/[brandSlug]/`.

### Static Content, Placeholders, and UI Limitations

- Dashboard admin di `frontend/src/routes/admin/+page.svelte` mendefinisikan metric, order terbaru, dan stock alert sebagai konstanta lokal, tidak terlihat mengambil data dashboard dari API. Tombol Export dan New Product pada file tersebut tidak memiliki handler yang tampak pada implementasi yang diperiksa.
- Brand-scoped admin product/inventory/order belum membawa operasi ke konteks brand pada route UI tersebut; halaman secara eksplisit menautkan ke halaman legacy default.
- Default storefront memiliki placeholder gambar bila gambar tidak tersedia/gagal. Ini fallback visual, bukan alur bisnis yang hilang.
- Route brand-scoped product detail memiliki conditional CTA ke `/brands/{slug}/cart`, dan layout conditional link cart/account, tetapi route tujuan cart/account tidak ditemukan dalam daftar route. Ini bukan bukti cart/account sudah tersedia.

## 5. Backend Findings

### API and Domain Logic

- **`/products`**
  - Endpoint: `GET/POST /`, `GET /catalog`, lookup by slug/detail, availability, image CRUD/set-primary, product update/archive/discontinue/reactivate/delete.
  - Implementasi: `backend/api/products.py`, `backend/crud/products.py`, `backend/crud/product_images.py`.
- **`/inventory-items`**
  - Endpoint: list/low-stock/by-product, movements/reservations reads, create/update/delete, receive/adjust/reserve/release/commit actions.
  - Implementasi: `backend/api/inventory_items.py`, `backend/crud/inventory_items.py`, `backend/crud/inventory_service.py`.
- **`/customers`**
  - Endpoint: customer list/summary/detail, CRUD, address list/CRUD.
  - Implementasi: `backend/api/customers.py`, `backend/crud/customers.py`.
- **`/orders`, `/orders/{id}/items`, `/order-items`**
  - Endpoint: order CRUD/status/cancel/fulfill dan item CRUD.
  - Implementasi: `backend/api/orders.py`, `backend/api/order_items.py`, `backend/crud/orders.py`, `backend/crud/order_items.py`.
- **`/payments`**
  - Endpoint: payment CRUD/read-by-order/status.
  - Implementasi: `backend/api/payments.py`, `backend/crud/payments.py`; create/update payment lifecycle memanggil inventory service sesuai implementasi domain.
- **`/reports/products*`**
  - Endpoint: dashboard, summary, revenue, slow-moving, low-stock active, discontinued with stock.
  - Implementasi: `backend/api/reports.py`, `backend/crud/reports.py`.
- **`/platform/brands`, `/platform/settings`, `/storefront`**
  - Endpoint: brand CRUD/read settings, update settings, audit log read, public storefront config.
  - Implementasi: `backend/api/settings.py`, `backend/crud/settings.py`.

Semua router tersebut diregistrasikan di `backend/main.py`. Schema request/response berada di `backend/schema_models/` dan diekspor melalui package schema. CRUD umumnya mengakses SQLAlchemy model; workflow order, inventory, payment, dan customer checkout memiliki fungsi domain di CRUD/service yang terkait.

### Models and Observed Relationships

- Tenant/settings: `brands` memiliki relasi satu-ke-satu dengan `brand_settings`, `storefront_settings`, `seo_settings`, `module_settings`, dan `system_settings`; `audit_logs` dapat terkait brand. Bukti: `backend/models/settings.py`.
- Catalog/pricing: `products` terkait brand, inventory, images, dan price sets; `price_set_items` dapat terkait channel/region. Bukti: `backend/models/catalog.py`, `backend/models/pricing.py`, `backend/models/channels.py`, `backend/models/regions.py`.
- Commerce: `customers` terkait `customer_addresses` dan `orders`; `orders` memiliki `order_items` dan relasi payment; inventory reservations merujuk product/order/order item; movement records merujuk product. Bukti: `backend/models/customers.py`, `backend/models/orders.py`, `backend/models/payments.py`, `backend/models/inventory.py`.

### Feature-Relevant Authentication and Authorization

`backend/security.py` memvalidasi role dari header `x-cm-role` dan menyediakan platform access guard. Route platform settings/brands menggunakan guard tersebut. Di sisi lain, router products, inventory, customers, orders, order-items, payments, reports tidak memasang dependency auth pada handler yang diperiksa. Implementasi ini menunjukkan role-header guard, bukan bukti autentikasi akun/token yang menyeluruh. Cakupan otorisasi brand juga bervariasi per handler dan belum dinilai lewat tes keamanan dalam task ini.

## 6. Initial Data Flow Mapping

1. **Product admin:** halaman products dan image manager memanggil `productsApi` (`frontend/src/lib/api/products.ts`) ke `/products/*`; handler mendelegasikan ke CRUD produk/image, yang menggunakan model `Product` dan `ProductImage`.
2. **Inventory admin:** inventory page memanggil `inventoryApi` ke `/inventory-items/*`; aksi domain diproses oleh `crud/inventory_service.py`, memodifikasi inventory item dan mencatat reservation/movement.
3. **Customer admin:** brand-scoped customer page memperoleh brand config, lalu memanggil `customersApi` dengan `brand_id`; handler customer mendelegasikan ke CRUD untuk customer/address dan response detail/summary.
4. **Storefront brand:** route slug meminta `/storefront/{brand_slug}/config`; konfigurasi memberikan `brand_id` dan flag publik. Katalog/detail kemudian meminta `/products/catalog` atau `/products/by-slug/{slug}/detail` dengan brand ID. Alur kodenya tampak pada `frontend/src/lib/api/storefront-config.ts`, `frontend/src/lib/storefront/products.ts`, dan backend settings/products.
5. **Order/inventory/payment domain:** handler order mendelegasikan pembuatan/perubahan lifecycle ke `crud/orders.py`, yang menggunakan inventory service; payment lifecycle di `crud/payments.py` juga terhubung dengan order/inventory. Hubungan alur dapat dibuktikan di kode, tetapi tidak diuji ulang dalam discovery ini.
6. **Platform settings:** console memakai `platformSettingsApi` dengan header role development; endpoint platform memanggil `crud/settings.py`, menyimpan model settings per brand, dan memiliki helper pencatatan audit.

Alur cart ke checkout publik belum bisa dipetakan karena tidak ditemukan route maupun endpoint cart/checkout.

## 7. Planned but Not Found in Implementation

Dokumen berikut berisi roadmap/checklist atau uraian rencana di dalamnya tidak diperlakukan sebagai bukti fitur aktif. Dibandingkan dengan kode saat ini:

- **Cart dan checkout publik**: dokumen platform menyebut endpoint cart/checkout sebagai pekerjaan mendatang dan mengakui guard backend menunggu endpoint tersebut; route/endpoint tidak ditemukan (`docs/archive/initial-planning/todo_platform_console_architecture.md`, `docs/archive/initial-planning/todo_storefront_catalog_architecture.md`). Helper resolve checkout customer/address sudah ada, tetapi bukan endpoint checkout.
- **Customer account/authentication**: module flag dan role boundary dibahas di `docs/archive/initial-planning/todo_platform_console_architecture.md`; tidak ditemukan route login, registration, account, session/token, atau API customer-auth pada area yang diperiksa. Header role sementara di `backend/security.py` tidak disamakan dengan autentikasi penuh.
- **Shipping workflow/fulfillment carrier**: flag shipping dan teks kondisi UI ada, tetapi tidak ditemukan modul/endpoint shipment, metode pengiriman, atau integrasi carrier.
- **Admin UI operasional untuk orders, payments, reports**: backend endpoint ada, namun halaman orders/payments eksplisit placeholder dan tidak ditemukan route report khusus.
- **Custom domain tenant resolution**: dokumen platform menyebut resolver menggunakan `brandSlug` dan custom domain belum dibuat (`docs/archive/initial-planning/todo_platform_console_architecture.md`); tidak ditemukan resolver domain khusus saat inspeksi.
- **Gateway pembayaran eksternal dan order tracking customer**: tidak ditemukan integrasi gateway atau route tracking publik dalam kode yang diperiksa.

Catatan: beberapa dokumen arsitektur lama menggambarkan kondisi awal yang sudah berubah, misalnya storefront/products atau customer UI yang masih placeholder. Status dalam inventaris ini mengikuti kode saat ini; dokumen dipakai sebagai konteks rencana saja.

## 8. Unverified Areas and Limitations

- Tidak menjalankan tes backend/frontend, browser, atau aksi tulis API untuk task ini. Endpoint HTTP yang pernah diuji pada TASK 2 hanya mencakup subset dan bukan verifikasi seluruh modul.
- Keberhasilan response endpoint sebelumnya tidak membuktikan setiap alur UI, validasi bisnis, error handling, akses per role, atau relasi lintas brand.
- Tidak memeriksa seluruh implementasi setiap fungsi CRUD baris demi baris; kesimpulan mengikuti handler, service utama, model/schema, dan pemanggil frontend yang relevan.
- Reporting API ada dalam kode, tetapi hasil query dan akurasinya belum divalidasi terhadap data.
- Skema database live, konsistensi data, dan kondisi integrasi pihak ketiga tidak menjadi objek pemeriksaan ulang di task ini.
- Tidak ditemukan cart/checkout route dalam daftar `frontend/src/routes/` yang diperiksa; perubahan kode di luar repository atau runtime eksternal tidak diketahui.

## 9. References

- Frontend routes: `frontend/src/routes/`
- Frontend API clients: `frontend/src/lib/api/`
- Storefront helper/client: `frontend/src/lib/storefront/`
- Backend router registration: `backend/main.py`
- Backend handlers: `backend/api/`
- Backend CRUD/domain logic: `backend/crud/`
- SQLAlchemy models: `backend/models/`
- API schemas: `backend/schema_models/`
- Role-header access checks: `backend/security.py`
- Project overview: `README.md`
- Architecture overview: `docs/architecture/architecture_notes.md`
- Planning archive: `docs/archive/initial-planning/todo_customer_architecture.md`, `docs/archive/initial-planning/todo_inventory_architecture.md`, `docs/archive/initial-planning/todo_platform_console_architecture.md`, `docs/archive/initial-planning/todo_products_architecture.md`, `docs/archive/initial-planning/todo_storefront_catalog_architecture.md`
