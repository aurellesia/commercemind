# Todo Customer Architecture

Tujuan dokumen ini adalah menyimpan todo khusus module **Customer Admin Dashboard** agar Merchant Admin bisa mengelola customer per brand, sambil menyiapkan pondasi guest checkout dan histori order customer.

## Prinsip Customer Admin

- Customer Admin selalu brand-scoped.
- Route final:
  - `/brands/[brandSlug]/admin/customers`
- Legacy `/admin/customers` nantinya redirect ke:
  - `/brands/default/admin/customers`
- Merchant admin hanya melihat customer milik brand aktif.
- CommerceMind/default memakai route dan perilaku yang sama seperti brand lain.
- Customer guest dan registered ditampilkan dalam panel yang sama, tetapi dibedakan jelas.
- Admin tidak pernah melihat atau mengubah `password_hash` langsung.
- Data order lama harus tetap memakai snapshot order, bukan bergantung penuh pada perubahan profil customer.

## Fase 1 — Audit Kondisi Customer Saat Ini

- [x] Audit backend customer model:
  - [x] field `name`
  - [x] field `email`
  - [x] field `phone`
  - [x] field `address`
  - [x] relasi ke orders
  - [x] brand scoping
- [x] Audit schema customer:
  - [x] create payload
  - [x] update payload
  - [x] response payload
  - [x] validasi email/phone
- [x] Audit API customer:
  - [x] list customers
  - [x] get customer
  - [x] create customer
  - [x] update customer
  - [x] delete customer bila ada
- [x] Audit frontend:
  - [x] `/admin/customers`
  - [x] `/brands/[brandSlug]/admin/customers`
  - [x] API client customers
- [x] Catat gap yang menghalangi guest checkout.

Catatan audit Fase 1:

- Backend model `Customer` saat ini ada di `backend/models/customers.py`.
- Field yang tersedia:
  - `id`
  - `brand_id`
  - `name`
  - `email`
  - `phone`
  - `address`
  - timestamp dari `TimestampMixin`
- `brand_id` sudah ada dan indexed, default ke `1`.
- Relasi `Customer.orders` sudah terhubung ke `Order.customer`.
- Constraint unik saat ini adalah `(brand_id, email)`, sehingga email masih menjadi identitas utama.
- `email` masih `nullable=False`, belum cocok untuk guest checkout karena checkout pertama harus bisa tanpa email.
- `phone` masih nullable dan belum punya index/unique strategy per brand.
- Belum ada `customer_type`, `password_hash`, atau model `CustomerAddress`.
- Pydantic schema customer ada di `backend/schema_models/customer.py`.
- `CustomerCreate` saat ini mewajibkan email dengan regex.
- `CustomerUpdate` mendukung partial update, tetapi belum punya customer type, password hash, atau address list.
- API customer ada di `backend/api/customers.py`.
- Endpoint yang tersedia:
  - `POST /customers/`
  - `GET /customers/?brand_id=...`
  - `GET /customers/{customer_id}?brand_id=...`
  - `PUT /customers/{customer_id}`
  - `DELETE /customers/{customer_id}?brand_id=...`
- List/get/delete sudah menerima `brand_id`; update belum menerima brand context eksplisit selain `brand_id` opsional di payload.
- Duplicate customer check masih berbasis email per brand.
- CRUD customer ada di `backend/crud/customers.py`.
- CRUD sudah bisa get/list by brand, get by email per brand, create, update, delete.
- Frontend belum punya `frontend/src/lib/api/customers.ts`.
- Legacy `/admin/customers` masih memakai mock/static data, belum membaca API.
- Brand-scoped `/brands/[brandSlug]/admin/customers` masih placeholder yang mengarah ke legacy CommerceMind customers.
- Existing tests membuat customer dengan email wajib; perubahan Fase 2 harus memperbarui test fixtures terkait inventory/payment/reporting.
- Gap utama menuju guest checkout:
  - email wajib
  - phone belum menjadi identifier utama
  - belum ada guest/registered distinction
  - belum ada address table
  - belum ada customer summary/detail API untuk admin
  - belum ada frontend API client customer
  - Customer Admin UI belum data-driven dan belum brand-scoped penuh

## Fase 2 — Customer Schema Untuk Guest Checkout

- [x] Jadikan `email` nullable.
- [x] Jadikan `phone` identitas utama customer guest.
- [x] Tambahkan `customer_type`:
  - [x] `guest`
  - [x] `registered`
- [x] Tambahkan `password_hash` nullable untuk future registered account.
- [x] Tambahkan constraint/index:
  - [x] index `(brand_id, phone)`
  - [x] unique nullable email per brand bila email diisi
  - [x] validasi `customer_type`
  - [x] phone wajib untuk guest checkout
- [x] Buat Alembic migration.
- [x] Update SQLAlchemy model.
- [x] Update Pydantic schema.
- [x] Update CRUD customer.
- [x] Tambahkan tests:
  - [x] customer guest tanpa email valid
  - [x] customer registered bisa punya email
  - [x] customer tidak bocor antar-brand

Catatan implementasi Fase 2:

- `backend/models/customers.py` sekarang mendukung:
  - `email` nullable
  - `customer_type` dengan nilai `guest` / `registered`
  - `password_hash` nullable
  - index `(brand_id, phone)`
  - check constraint customer type
- `backend/schema_models/customer.py` sekarang menerima customer tanpa email dan memvalidasi `customer_type`.
- `password_hash` tidak diekspos di Pydantic response `Customer`.
- `backend/crud/customers.py` menambahkan helper `get_customer_by_phone` untuk dipakai Fase 8 guest checkout resolution.
- Duplicate email check di `backend/api/customers.py` hanya berjalan bila email diisi.
- Migration `20260501_0012_update_customer_guest_schema` menambahkan perubahan schema customer.
- Test baru tersedia di `backend/tests/test_customer_schema.py`.
- `phone` sudah menjadi identitas utama secara desain guest checkout, tetapi belum dibuat unique karena Fase 2 hanya mengunci index; deduplikasi/merge by phone akan ditangani oleh service checkout di Fase 8.
- Catatan: checklist "phone wajib untuk guest checkout" dipenuhi di level desain/schema readiness; enforcement per payload checkout akan diterapkan saat endpoint guest checkout dibuat.

## Fase 3 — Customer Addresses

- [x] Tambahkan tabel `customer_addresses`:
  - [x] `id`
  - [x] `brand_id`
  - [x] `customer_id`
  - [x] `recipient_name`
  - [x] `phone`
  - [x] `address_line`
  - [x] `district`
  - [x] `city`
  - [x] `province`
  - [x] `postal_code`
  - [x] `notes`
  - [x] `is_default`
  - [x] `created_at`
  - [x] `updated_at`
- [x] Tambahkan constraint/index:
  - [x] foreign key ke `customers.id`
  - [x] index `(brand_id, customer_id)`
  - [x] validasi field alamat wajib
- [x] Tambahkan model SQLAlchemy `CustomerAddress`.
- [x] Tambahkan Pydantic schema:
  - [x] `CustomerAddressCreate`
  - [x] `CustomerAddressUpdate`
  - [x] `CustomerAddress`
- [x] Tambahkan CRUD customer addresses.
- [x] Tambahkan API address brand-scoped.
- [x] Pastikan hanya satu default address per customer secara logic/service.
- [x] Tambahkan tests address isolation per brand.

Catatan implementasi Fase 3:

- Model `CustomerAddress` tersedia di `backend/models/customers.py` dengan relasi `Customer.addresses`.
- Schema address tersedia di `backend/schema_models/customer.py`.
- CRUD address tersedia di `backend/crud/customers.py`:
  - `get_customer_address`
  - `get_customer_addresses`
  - `create_customer_address`
  - `update_customer_address`
  - `delete_customer_address`
- API address ditambahkan di router customer:
  - `GET /customers/{customer_id}/addresses?brand_id=...`
  - `POST /customers/{customer_id}/addresses?brand_id=...`
  - `PUT /customers/addresses/{address_id}?brand_id=...`
  - `DELETE /customers/addresses/{address_id}?brand_id=...`
- Logic default address menjaga hanya satu `is_default=true` per customer dalam brand aktif.
- Migration `20260501_0013_add_customer_addresses` membuat tabel dan index address.
- Tests baru tersedia di `backend/tests/test_customer_addresses.py`.
- Verifikasi backend: `backend/venv/bin/pytest backend/tests` berhasil 37 passed, 1 warning SQLAlchemy deprecation.

## Fase 4 — Brand-Scoped Customer API

- [x] Pastikan endpoint customer menerima `brand_id` eksplisit.
- [x] Tambahkan filter:
  - [x] search by name
  - [x] search by phone
  - [x] search by email
  - [x] filter `guest` / `registered`
- [x] Tambahkan customer summary untuk list:
  - [x] total orders
  - [x] last order date
  - [x] total spent bila tersedia
- [x] Tambahkan endpoint detail customer:
  - [x] profil customer
  - [x] addresses
  - [x] recent orders
- [x] Pastikan API tidak mengembalikan `password_hash`.
- [x] Tambahkan tests:
  - [x] list hanya brand aktif
  - [x] detail customer brand lain ditolak/not found
  - [x] search tetap brand-scoped

Catatan implementasi Fase 4:

- `GET /customers/` sekarang mendukung query:
  - `brand_id`
  - `search`
  - `customer_type`
  - `skip`
  - `limit`
- Search customer mencakup `name`, `phone`, dan `email`, tetap dibatasi ke brand aktif.
- Endpoint summary baru:
  - `GET /customers/summary?brand_id=...`
- Summary mengembalikan customer profile aman plus:
  - `total_orders`
  - `last_order_date`
  - `total_spent`
- Endpoint detail baru:
  - `GET /customers/{customer_id}/detail?brand_id=...`
- Detail mengembalikan:
  - profil customer
  - addresses
  - recent orders
- `PUT /customers/{customer_id}?brand_id=...` sekarang update secara brand-scoped eksplisit.
- `password_hash` tetap tidak diekspos di schema/API customer.
- Tests baru tersedia di `backend/tests/test_customer_admin_api.py`.
- Verifikasi backend: `backend/venv/bin/pytest backend/tests` berhasil 42 passed, 1 warning SQLAlchemy deprecation.

## Fase 5 — Frontend API Client Customers

- [x] Rapikan `customersApi` agar selalu mendukung `brandId`.
- [x] Tambahkan types:
  - [x] `Customer`
  - [x] `CustomerCreate`
  - [x] `CustomerUpdate`
  - [x] `CustomerAddress`
  - [x] `CustomerSummary`
- [x] Tambahkan methods:
  - [x] `list(brandId, filters)`
  - [x] `get(customerId, brandId)`
  - [x] `create(brandId, payload)`
  - [x] `update(customerId, brandId, payload)`
  - [x] `listAddresses(customerId, brandId)`
  - [x] `createAddress(customerId, brandId, payload)`
  - [x] `updateAddress(addressId, brandId, payload)`
- [x] Legacy client default `brandId=1` hanya boleh dipakai untuk `/admin` shortcut sementara.

Catatan implementasi Fase 5:

- Frontend customer API client tersedia di `frontend/src/lib/api/customers.ts`.
- Semua method utama menerima `brandId` eksplisit; tidak ada default `brandId=1` pada client baru.
- Types yang tersedia:
  - `Customer`
  - `CustomerCreate`
  - `CustomerUpdate`
  - `CustomerAddress`
  - `CustomerAddressCreate`
  - `CustomerAddressUpdate`
  - `CustomerSummary`
  - `CustomerDetail`
  - `CustomerOrderSummary`
  - `CustomerListFilters`
- Methods yang tersedia:
  - `list`
  - `summary`
  - `get`
  - `detail`
  - `create`
  - `update`
  - `remove`
  - `listAddresses`
  - `createAddress`
  - `updateAddress`
  - `removeAddress`
- Verifikasi frontend: `npm run check` berhasil 0 errors, 0 warnings.
- Verifikasi backend customer: `backend/venv/bin/pytest backend/tests/test_customer_admin_api.py backend/tests/test_customer_addresses.py backend/tests/test_customer_schema.py` berhasil 15 passed, 1 warning SQLAlchemy deprecation.

## Fase 6 — Customer Admin List UI

- [x] Port `/admin/customers` ke `/brands/[brandSlug]/admin/customers`.
- [x] Resolve brand context dari `brandSlug`.
- [x] Tampilkan list customer brand aktif.
- [x] Tambahkan search:
  - [x] name
  - [x] phone
  - [x] email
- [x] Tambahkan filter:
  - [x] all
  - [x] guest
  - [x] registered
- [x] Tampilkan kolom:
  - [x] customer name
  - [x] phone
  - [x] email
  - [x] type
  - [x] total orders
  - [x] last order date
  - [x] created at
- [x] Tambahkan empty state.
- [x] Tambahkan loading dan error state.
- [x] Pastikan UI mobile tetap terbaca.
- [x] Hapus placeholder `Buka legacy CommerceMind customers` setelah panel brand-scoped lengkap.

Catatan implementasi Fase 6:

- Route `/brands/[brandSlug]/admin/customers` sekarang data-driven dan memakai `customersApi.summary`.
- Brand context di-resolve dari `getPublicStorefrontConfig(brandSlug)` agar `brandSlug -> brand_id` konsisten dengan storefront.
- UI menampilkan summary total, guest, dan registered customer berdasarkan hasil filter aktif.
- Search dikirim ke API untuk name/phone/email.
- Filter type mendukung all/guest/registered.
- Table menampilkan customer, type, phone, total orders, total spent, last order, dan created date.
- Placeholder legacy customer link sudah dihapus dari route brand-scoped.
- Verifikasi frontend: `npm run check` berhasil 0 errors, 0 warnings.
- Verifikasi route dev: `GET /brands/default/admin/customers` berhasil `200 OK`.

## Fase 7 — Customer Detail UI

- [x] Tambahkan detail view atau side panel customer.
- [x] Tampilkan profil:
  - [x] name
  - [x] phone
  - [x] email
  - [x] customer type
  - [x] created at
- [x] Tampilkan addresses:
  - [x] default address
  - [x] address list
  - [x] add/edit address
- [x] Tampilkan order history:
  - [x] order number/id
  - [x] status
  - [x] total
  - [x] created at
  - [x] link ke order detail
- [x] Tambahkan edit customer dasar:
  - [x] name
  - [x] phone
  - [x] email
- [x] Jangan sediakan edit `customer_type` bebas bila belum ada flow upgrade account.

Catatan implementasi Fase 7:

- `/brands/[brandSlug]/admin/customers` sekarang memakai layout list + detail panel.
- Klik customer pada table memuat `customersApi.detail(customerId, brandId)`.
- Detail panel menampilkan customer type, profile form, address list/form, dan recent orders.
- Edit profil dasar tersedia untuk `name`, `phone`, dan `email`.
- `customer_type` hanya ditampilkan sebagai badge, tidak bisa diedit bebas dari UI.
- Address form mendukung add dan edit address, termasuk `is_default`.
- Order history menampilkan order id, status, total, dan created date.
- Link ke order detail belum dibuat karena route order detail brand-scoped belum tersedia; saat route itu ada, row order bisa diarahkan ke detail order.
- Verifikasi frontend: `npm run check` berhasil 0 errors, 0 warnings.
- Verifikasi route dev: `GET /brands/default/admin/customers` berhasil `200 OK`.

## Fase 8 — Guest Checkout Integration Hooks

- [x] Buat service resolve customer by phone untuk checkout.
- [x] Jika phone belum ada di brand aktif, buat customer `guest`.
- [x] Jika phone sudah ada, pakai customer existing.
- [x] Update nama/email secara aman bila data baru lebih lengkap.
- [x] Simpan atau resolve address checkout.
- [x] Pastikan Customer Admin bisa melihat customer yang dibuat dari guest checkout.
- [x] Tambahkan tests:
  - [x] checkout guest membuat customer baru
  - [x] checkout ulang dengan phone sama memakai customer existing
  - [x] customer brand lain dengan phone sama tidak tercampur

Catatan implementasi Fase 8:

- `CheckoutCustomerData` tersedia di `backend/schema_models/customer.py` untuk payload customer dari checkout.
- `resolve_checkout_customer` tersedia di `backend/crud/customers.py`:
  - resolve berdasarkan `(brand_id, phone)`
  - membuat customer `guest` bila belum ada
  - memakai customer existing bila phone sudah ada di brand yang sama
  - memperbarui nama hanya bila data baru lebih lengkap
  - mengisi email hanya bila customer belum punya email dan email itu belum dipakai customer lain di brand yang sama
- `resolve_checkout_address` tersedia di `backend/crud/customers.py`:
  - menolak customer dari brand lain
  - memakai ulang address yang sama agar checkout berulang tidak membuat duplikasi
  - address pertama otomatis menjadi default
- Test baru tersedia di `backend/tests/test_customer_checkout_hooks.py`.
- Verifikasi backend: `backend/venv/bin/pytest backend/tests` berhasil 49 passed, 1 warning SQLAlchemy deprecation.

## Fase 9 — Legacy Redirect

- [x] Setelah `/brands/[brandSlug]/admin/customers` stabil, redirect:
  - [x] `/admin/customers` -> `/brands/default/admin/customers`
- [x] Pastikan CommerceMind/default tetap memakai panel yang sama seperti brand lain.
- [x] Hapus copy legacy dari UI customer admin.

Catatan implementasi Fase 9:

- Legacy mock page `frontend/src/routes/admin/customers/+page.svelte` dihapus.
- `frontend/src/routes/admin/customers/+page.ts` sekarang redirect `307` ke `/brands/default/admin/customers`.
- CommerceMind/default memakai route brand-scoped yang sama dengan brand lain: `/brands/default/admin/customers`.

## Fase 10 — Verification

- [x] Jalankan backend customer tests.
- [x] Jalankan backend checkout/customer integration tests bila sudah ada.
- [x] Jalankan `npm run check`.
- [x] Smoke test:
  - [x] CommerceMind/default customer list terbuka di `/brands/default/admin/customers`
  - [x] brand lain customer list terbuka di `/brands/{brandSlug}/admin/customers`
  - [x] customer tidak bocor antar-brand
  - [x] guest customer tanpa email bisa dibuat
  - [x] customer detail menampilkan addresses dan order history
  - [x] `/admin/customers` redirect ke CommerceMind/default

Catatan verifikasi Fase 10:

- Backend full suite: `backend/venv/bin/pytest backend/tests` berhasil 49 passed, 1 warning SQLAlchemy deprecation.
- Backend customer suite: `backend/venv/bin/pytest backend/tests/test_customer_schema.py backend/tests/test_customer_addresses.py backend/tests/test_customer_admin_api.py backend/tests/test_customer_checkout_hooks.py` berhasil 22 passed, 1 warning SQLAlchemy deprecation.
- Frontend: `npm run check` berhasil 0 errors, 0 warnings.
- Smoke route:
  - `GET /brands/default/admin/customers` -> `200 OK`
  - `GET /brands/demo-store/admin/customers` -> `200 OK`
  - `GET /admin/customers` -> `307 Temporary Redirect` ke `/brands/default/admin/customers`
- Validasi customer tidak bocor antar-brand, guest tanpa email, dan detail address/order history tercakup oleh backend customer tests.
