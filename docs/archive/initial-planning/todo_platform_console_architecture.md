# Todo Platform Console Architecture

Tujuan dokumen ini adalah menyimpan backlog **Platform Console** untuk CommerceMind. Platform Console adalah area khusus platform operator, yaitu kamu/tim CommerceMind, untuk mengelola banyak brand/client dan mengatur kemampuan sistem yang tidak boleh diubah bebas oleh merchant/client.

Nama yang dipakai:

- **Brand/Tenant**: satu client/business yang memakai CommerceMind.
- **Storefront**: area public/customer untuk satu brand.
- **Merchant Admin**: area operasional satu brand untuk produk, inventory, order, customer, payment, dan report.
- **Platform Console**: area platform operator untuk mengelola banyak brand, module flags, template storefront, security, plan, dan maintenance.

Route awal yang disarankan:

```text
/console
```

Route multi-brand yang disarankan:

```text
/console/brands
/console/brands/{brand_id}
/console/brands/{brand_id}/settings

/brands/{brand_slug}
/brands/{brand_slug}/products
/brands/{brand_slug}/admin
```

Custom domain bisa ditambahkan belakangan:

```text
brand-a.com -> tenant brand-a storefront
brand-b.com -> tenant brand-b storefront
```

## Prinsip Desain

- Platform Console bukan panel harian merchant.
- Merchant/client juga bisa disebut owner bisnis, jadi hindari istilah `owner panel`.
- Platform Console adalah control plane multi-brand untuk CommerceMind.
- Setiap brand punya data, Merchant Admin, Storefront, settings, dan module flags sendiri.
- Platform Console hanya untuk setting yang berdampak ke sistem, template, tenant/brand, module availability, plan, dan operasional platform.
- Setting yang berpengaruh ke customer journey harus bisa dibaca oleh frontend/storefront secara aman dan berdasarkan brand aktif.
- Setting yang sensitif hanya boleh dibaca/diubah oleh platform operator.
- Struktur data awal sebaiknya eksplisit, bukan key-value terlalu bebas, agar mudah dipahami saat produk masih tumbuh.
- CommerceMind harus bergerak ke tenant-first. Single-brand implementation yang sudah ada diperlakukan sebagai baseline sementara, bukan arsitektur final.

## Role Boundary

### Customer

- Melihat storefront milik satu brand.
- Melihat product catalog milik brand tersebut.
- Nanti: cart, guest checkout, order tracking.

### Merchant Admin

- Mengelola operasi satu brand/toko:
  - products
  - images
  - inventory
  - orders
  - customers
  - payments
  - reports
- Tidak boleh mengubah module availability global.
- Tidak boleh mengubah system maintenance mode.
- Tidak boleh mengubah tenant/client plan.
- Tidak boleh melihat data brand lain.

### Platform Operator

- Mengelola platform:
  - brand/tenant/client
  - brand status dan plan
  - brand/storefront template settings
  - feature/module flags
  - global SEO defaults
  - maintenance mode
  - system health
  - role/permission baseline
  - integration credentials placeholder

## Fase 1 — Platform Console Scope dan Navigation

- [x] Buat route frontend:
  - [x] `/console`
  - [x] `/console/settings`
  - [x] `/console/storefront`
  - [x] `/console/modules`
  - [x] `/console/system`
- [x] Buat layout console terpisah dari admin:
  - [x] brand `CommerceMind Console`
  - [x] nav khusus platform
  - [x] visual lebih system/operator, bukan storefront/customer
- [x] Tambahkan entry point sementara dari homepage/internal root bila perlu
- [x] Dokumentasikan perbedaan `/admin` dan `/console`
- [x] Pastikan route console belum tampil ke customer storefront

Catatan verifikasi Fase 1:

- Route `/console` dan sub-route awal sudah tersedia dengan layout terpisah dari Merchant Admin.
- Console memakai visual gelap/system-operator dan nav khusus platform.
- Entry point sementara tersedia dari root app chooser dan dari `/console` ke `/admin` dan `/storefront`, tetapi tidak ditampilkan dari storefront customer.
- Dokumentasi role boundary membedakan Storefront, Merchant Admin, dan Platform Console.

## Fase 2 — Settings Schema Foundation

- [x] Buat tabel `brand_settings`:
  - [x] `id`
  - [x] `brand_name`
  - [x] `tagline`
  - [x] `logo_url`
  - [x] `contact_whatsapp`
  - [x] `support_email`
  - [x] `business_address`
  - [x] `created_at`
  - [x] `updated_at`
- [x] Buat tabel `storefront_settings`:
  - [x] `id`
  - [x] `storefront_enabled`
  - [x] `homepage_headline`
  - [x] `homepage_description`
  - [x] `featured_product_limit`
  - [x] `show_out_of_stock_products`
  - [x] `show_sku`
  - [x] `created_at`
  - [x] `updated_at`
- [x] Buat tabel `seo_settings`:
  - [x] `id`
  - [x] `site_url`
  - [x] `default_title`
  - [x] `default_description`
  - [x] `social_image_url`
  - [x] `created_at`
  - [x] `updated_at`
- [x] Buat tabel `module_settings`:
  - [x] `id`
  - [x] `products_enabled`
  - [x] `inventory_enabled`
  - [x] `cart_enabled`
  - [x] `guest_checkout_enabled`
  - [x] `customer_accounts_enabled`
  - [x] `payments_enabled`
  - [x] `shipping_enabled`
  - [x] `reports_enabled`
  - [x] `created_at`
  - [x] `updated_at`
- [x] Buat tabel `system_settings`:
  - [x] `id`
  - [x] `maintenance_mode`
  - [x] `test_mode`
  - [x] `public_catalog_enabled`
  - [x] `allow_checkout`
  - [x] `created_at`
  - [x] `updated_at`
- [x] Buat Alembic migration untuk settings foundation
- [x] Seed default settings agar app bisa jalan tanpa konfigurasi manual

Catatan verifikasi Fase 2:

- Model settings tersedia di `backend/models/settings.py` dan diekspor dari `backend/models/__init__.py`.
- Migration `20260430_0008_add_platform_settings` membuat lima tabel settings dan seed row default `id = 1`.
- Default awal menjaga cart/checkout disabled, public catalog enabled, storefront enabled, dan CommerceMind sebagai fallback brand.
- `backend/venv/bin/alembic upgrade head` sukses menerapkan migration ke DB lokal.
- Seed settings lokal terverifikasi: brand `CommerceMind`, storefront enabled, cart disabled, public catalog enabled.

## Fase 3 — Backend Settings API

- [x] Tambahkan schema Pydantic:
  - [x] `BrandSettings`
  - [x] `BrandSettingsUpdate`
  - [x] `StorefrontSettings`
  - [x] `StorefrontSettingsUpdate`
  - [x] `SeoSettings`
  - [x] `SeoSettingsUpdate`
  - [x] `ModuleSettings`
  - [x] `ModuleSettingsUpdate`
  - [x] `SystemSettings`
  - [x] `SystemSettingsUpdate`
- [x] Tambahkan CRUD/service settings:
  - [x] get current settings
  - [x] update settings
  - [x] ensure default row exists
- [x] Tambahkan API platform/private:
  - [x] `GET /platform/settings`
  - [x] `PUT /platform/settings/brand`
  - [x] `PUT /platform/settings/storefront`
  - [x] `PUT /platform/settings/seo`
  - [x] `PUT /platform/settings/modules`
  - [x] `PUT /platform/settings/system`
- [x] Tambahkan API public-safe storefront config:
  - [x] `GET /storefront/config`
- [x] Pastikan public config hanya mengembalikan data aman:
  - [x] brand name
  - [x] tagline
  - [x] logo URL
  - [x] storefront enabled
  - [x] homepage copy
  - [x] featured product limit
  - [x] show out of stock
  - [x] show SKU
  - [x] SEO public fields
  - [x] module flags yang aman untuk UI
- [x] Jangan expose:
  - [x] internal system flags sensitif
  - [x] credentials
  - [x] platform-only notes

Catatan verifikasi Fase 3:

- Schema settings tersedia di `backend/schema_models/settings.py`.
- CRUD/service settings tersedia di `backend/crud/settings.py` dengan `ensure_platform_settings`.
- Router platform dan public storefront config tersedia di `backend/api/settings.py` dan didaftarkan ke FastAPI.
- Public config mengekspos field aman untuk storefront dan tidak mengekspos `support_email`, `maintenance_mode`, atau `reports_enabled`.
- Access control belum diterapkan; endpoint platform akan diberi guard di Fase 7 sesuai rencana security.

## Fase 4 — Frontend Console Settings UI

- [x] Buat API client platform settings
- [x] Buat halaman `/console/settings` sebagai overview
- [x] Buat halaman `/console/storefront`:
  - [x] brand name
  - [x] tagline
  - [x] logo URL
  - [x] homepage headline
  - [x] homepage description
  - [x] featured product limit
  - [x] show out of stock products
  - [x] show SKU
- [x] Buat halaman `/console/modules`:
  - [x] products
  - [x] inventory
  - [x] cart
  - [x] guest checkout
  - [x] customer accounts
  - [x] payments
  - [x] shipping
  - [x] reports
- [x] Buat halaman `/console/system`:
  - [x] maintenance mode
  - [x] test mode
  - [x] public catalog enabled
  - [x] allow checkout
- [x] Tambahkan save state:
  - [x] saving
  - [x] success
  - [x] validation error
  - [x] API error
- [x] Pastikan perubahan setting tidak membutuhkan redeploy frontend

Catatan verifikasi Fase 4:

- API client platform settings tersedia di `frontend/src/lib/api/platform-settings.ts`.
- `/console/settings` memuat overview settings dari backend.
- `/console/storefront` dapat mengubah brand, storefront, dan SEO settings.
- `/console/modules` dapat mengubah module flags.
- `/console/system` dapat mengubah system flags.
- Semua form memiliki loading, saving, success, dan error states.
- Perubahan tersimpan via API runtime sehingga tidak butuh redeploy frontend.

## Catatan Revisi Multi-Brand

- Fase 1-4 yang sudah selesai membangun baseline single-brand agar console dan settings API cepat hidup.
- Arah produk yang benar adalah multi-brand: satu Platform Console mengelola banyak brand, dan tiap brand punya Merchant Admin + Storefront sendiri.
- Sebelum storefront membaca dynamic config secara final, settings harus dipindah dari global single-row menjadi brand-scoped.
- Fase berikutnya adalah Brand/Tenant Foundation, bukan langsung melanjutkan runtime config global.

## Fase 5 — Brand/Tenant Foundation

- [x] Buat tabel `brands`:
  - [x] `id`
  - [x] `name`
  - [x] `slug`
  - [x] `status`: `draft` / `active` / `suspended` / `archived`
  - [x] `plan`
  - [x] `primary_domain`
  - [x] `created_at`
  - [x] `updated_at`
- [x] Tambahkan `brand_id` ke settings:
  - [x] `brand_settings.brand_id`
  - [x] `storefront_settings.brand_id`
  - [x] `seo_settings.brand_id`
  - [x] `module_settings.brand_id`
  - [x] `system_settings.brand_id`
- [x] Tambahkan unique constraint:
  - [x] `brands.slug`
  - [x] satu settings row per brand untuk tiap settings table
- [x] Seed default brand dari existing single-brand settings:
  - [x] brand name `CommerceMind`
  - [x] slug `default`
  - [x] status `active`
  - [x] existing settings dipindah ke brand default
- [x] Update model SQLAlchemy untuk relationship brand -> settings
- [x] Update CRUD settings agar menerima `brand_id` atau `brand_slug`
- [x] Tambahkan CRUD brands:
  - [x] list brands
  - [x] get brand
  - [x] get brand by slug
  - [x] create brand
  - [x] update brand
  - [x] archive/suspend brand
- [x] Tambahkan API Platform Console:
  - [x] `GET /platform/brands`
  - [x] `POST /platform/brands`
  - [x] `GET /platform/brands/{brand_id}`
  - [x] `PUT /platform/brands/{brand_id}`
  - [x] `GET /platform/brands/{brand_id}/settings`
  - [x] `PUT /platform/brands/{brand_id}/settings/brand`
  - [x] `PUT /platform/brands/{brand_id}/settings/storefront`
  - [x] `PUT /platform/brands/{brand_id}/settings/seo`
  - [x] `PUT /platform/brands/{brand_id}/settings/modules`
  - [x] `PUT /platform/brands/{brand_id}/settings/system`
- [x] Tambahkan API public-safe brand storefront config:
  - [x] `GET /storefront/{brand_slug}/config`
  - [x] fallback custom-domain resolver nanti
- [x] Update frontend Platform Console:
  - [x] `/console/brands`
  - [x] `/console/brands/[brandId]`
  - [x] `/console/brands/[brandId]/settings`
  - [x] brand switcher di console
- [x] Tandai endpoint global lama sebagai transitional:
  - [x] `GET /platform/settings`
  - [x] `GET /storefront/config`
  - [x] tetap membaca default brand sementara

Catatan verifikasi Fase 5:

- Migration `20260430_0009_add_brand_foundation` menambahkan tabel `brands` dan `brand_id` pada semua settings table.
- Default brand `CommerceMind` dengan slug `default` dibuat dan settings existing di-scope ke brand tersebut.
- Endpoint brand-scoped tersedia untuk Platform Console dan public storefront config.
- Endpoint global lama tetap membaca default brand sebagai compatibility layer sementara.
- Frontend console memiliki halaman `/console/brands`, `/console/brands/[brandId]`, dan `/console/brands/[brandId]/settings`.
- Panel `/console`, `/console/settings`, `/console/storefront`, `/console/modules`, dan `/console/system` sekarang memakai brand scope aktif dan endpoint `/platform/brands/{brand_id}/settings/*`, bukan endpoint global transitional.
- Regression test memastikan settings brand baru terisolasi dari default brand.

## Fase 6 — Brand-Scoped Storefront dan Merchant Admin

- [x] Update route storefront agar brand-scoped:
  - [x] `/brands/{brand_slug}`
  - [x] `/brands/{brand_slug}/products`
  - [x] `/brands/{brand_slug}/products/{product_slug}`
- [x] Update route merchant admin agar brand-scoped:
  - [x] `/brands/{brand_slug}/admin`
  - [x] `/brands/{brand_slug}/admin/products`
  - [x] `/brands/{brand_slug}/admin/inventory`
  - [x] `/brands/{brand_slug}/admin/orders`
- [x] Tentukan strategi kompatibilitas route lama:
  - [x] `/storefront` redirect ke default brand storefront
  - [x] `/admin` redirect ke default brand admin
- [x] Tambahkan brand resolver frontend:
  - [x] dari route param `brand_slug`
  - [x] nanti dari custom domain
- [x] Pastikan Merchant Admin hanya bekerja dalam konteks brand aktif

Catatan verifikasi Fase 6:

- Brand-scoped storefront routes tersedia di `/brands/[brandSlug]`, `/brands/[brandSlug]/products`, dan `/brands/[brandSlug]/products/[slug]`.
- Brand-scoped storefront layout membaca public config via `GET /storefront/{brand_slug}/config`.
- Brand-scoped merchant admin shell tersedia di `/brands/[brandSlug]/admin` dengan subroute products, inventory, orders, dan customers.
- Route lama `/storefront` redirect ke `/brands/default`.
- Route lama `/admin` redirect ke `/brands/default/admin`.
- Custom domain resolver belum dibuat; resolver saat ini memakai route param `brandSlug`.
- Business data utama sudah mulai `brand_id` scoped di Fase 7. Brand-scoped admin module pages masih menjadi compatibility bridge sampai UI admin lama dipindahkan penuh ke konteks brand.

## Fase 7 — Brand-Scoped Commerce Data

- [x] Tambahkan `brand_id` ke core business tables:
  - [x] products
  - [x] product_images, lewat product
  - [x] inventory_items
  - [x] inventory_movements
  - [x] inventory_reservations
  - [x] customers
  - [x] orders
  - [x] order_items
  - [x] payments
  - [x] price_sets
  - [x] channels
  - [x] regions
- [x] Update unique constraints agar scoped per brand:
  - [x] product slug unique per brand
  - [x] SKU unique per brand
  - [x] customer email strategy per brand
  - [ ] customer phone strategy per brand
- [x] Update CRUD query utama agar filter `brand_id`
- [x] Update report query agar scoped per brand
- [x] Tambahkan tests:
  - [x] brand A tidak bisa melihat product brand B
  - [x] brand A slug sama dengan brand B diperbolehkan
  - [ ] admin brand A tidak bisa mutate data brand B

Catatan verifikasi Fase 7:

- Migrasi `20260430_0010` menambahkan `brand_id` ke data commerce inti dan mengganti unique index global product/customer/channel/region menjadi constraint per brand.
- Public config sekarang mengembalikan `brand_id` dan `brand_slug`, sehingga storefront brand route bisa meminta catalog/detail dengan brand yang benar.
- Catalog/detail product backend menerima `brand_id` dan slug lookup sudah scoped per brand.
- CRUD dasar customer, order, inventory item, price set, channel, region, dan report product sudah memiliki filter brand default `1`.
- Mutasi admin lintas brand masih butuh access-control guard di Fase 10; Fase 7 baru menyiapkan data boundary dan query boundary.

## Fase 8 — Storefront Reads Dynamic Brand Config

- [x] Ganti hardcoded `storefrontConfig` menjadi config runtime:
  - [x] fallback local default tetap ada
  - [x] fetch dari `GET /storefront/{brand_slug}/config`
  - [x] cache sederhana di frontend
- [x] Storefront home memakai dynamic:
  - [x] brand name
  - [x] tagline
  - [x] homepage headline
  - [x] homepage description
  - [x] featured product limit
  - [x] SEO defaults
- [x] Product catalog memakai dynamic:
  - [x] show SKU
  - [x] show out of stock
  - [x] public catalog enabled
- [x] Bila `storefront_enabled = false`:
  - [x] tampilkan maintenance/coming soon page public
  - [x] jangan tampilkan catalog
- [x] Bila `public_catalog_enabled = false`:
  - [x] sembunyikan product catalog public
  - [x] tampilkan pesan ramah

Catatan verifikasi Fase 8:

- Runtime config frontend ada di `frontend/src/lib/api/storefront-config.ts`, dengan fallback lokal dan cache per `brandSlug`.
- Brand storefront home memakai headline, deskripsi, SEO, dan featured limit dari config.
- Brand product catalog memakai `show_sku`, `show_out_of_stock_products`, dan `public_catalog_enabled`.
- Product detail ikut menghormati `public_catalog_enabled` dan memakai SEO/product image metadata.
- Layout brand storefront menahan public page bila `storefront_enabled = false`.

## Fase 9 — Module Flags Integration

- [x] Gunakan module flags untuk menyembunyikan fitur belum aktif:
  - [x] cart icon/link
  - [x] checkout button
  - [x] customer account link
  - [x] payment options
  - [x] shipping options
- [x] Pastikan feature flag hanya menyembunyikan UI, bukan satu-satunya proteksi backend
- [ ] Backend tetap harus validasi:
  - [ ] checkout disabled, dipasang saat endpoint checkout/cart dibuat
  - [x] payment disabled
  - [x] public catalog disabled
- [ ] Tambahkan test module flag:
  - [ ] cart disabled membuat endpoint cart ditolak nanti, menunggu cart endpoint
  - [ ] checkout disabled membuat checkout ditolak nanti, menunggu checkout endpoint
  - [x] public catalog disabled membuat catalog public ditolak

Catatan verifikasi Fase 9:

- Brand storefront header menyembunyikan cart/account links berdasarkan `cart_enabled` dan `customer_accounts_enabled`.
- Product detail menyembunyikan checkout/cart CTA, payment option, dan shipping option berdasarkan `allow_checkout`, `cart_enabled`, `payments_enabled`, dan `shipping_enabled`.
- Backend public catalog endpoint menolak request public saat `public_catalog_enabled = false` atau products module disabled, sementara admin preview `include_non_public=true` tetap bisa dipakai.
- Backend payments endpoint menolak akses saat `payments_enabled = false`.
- Cart/checkout backend guard belum bisa dipasang penuh karena endpoint cart/checkout belum dibuat; ini menjadi syarat saat masuk modul cart.

## Fase 10 — Security dan Access Control

- [x] Rancang role:
  - [x] `platform_operator`
  - [x] `merchant_admin`
  - [x] `merchant_staff`
  - [x] `customer`
- [x] Console hanya boleh diakses `platform_operator`
- [x] Merchant admin hanya boleh akses brand yang dimilikinya
- [x] Merchant admin tidak boleh akses `/console`
- [x] Public/customer tidak boleh akses `/console`
- [x] Tambahkan auth guard placeholder bila auth belum dibangun
- [x] Tambahkan audit log untuk setting penting:
  - [x] siapa mengubah
  - [x] setting apa
  - [x] value lama
  - [x] value baru
  - [x] timestamp
- [x] Jangan simpan credentials integrasi sebagai plain text di fase final

Catatan verifikasi Fase 10:

- Placeholder auth memakai header sementara:
  - `x-cm-role`: `platform_operator`, `merchant_admin`, `merchant_staff`, atau `customer`
  - `x-cm-actor`: identitas operator sementara
  - `x-cm-brand-id`: brand context untuk merchant role
- Endpoint `/platform/*` sekarang membutuhkan role `platform_operator`.
- Merchant brand-access helper sudah tersedia untuk dipasang ke endpoint merchant/admin brand-scoped berikutnya.
- Frontend Platform Console mengirim header dev `platform_operator` via API helper sementara.
- Audit log tersimpan di tabel `audit_logs` untuk perubahan brand/settings penting, termasuk actor, role, target, before value, after value, dan timestamp.
- Tidak ada credential integrasi baru yang disimpan; fase integrasi final harus memakai secret storage/encryption, bukan plain text.

## Fase 11 — Verification

- [x] Jalankan backend tests
- [x] Jalankan `npm run check`
- [x] Smoke test:
  - [x] console settings page load
  - [x] update brand name
  - [x] storefront membaca brand name baru
  - [x] update homepage headline
  - [x] storefront membaca headline baru
  - [x] disable storefront
  - [x] storefront menampilkan maintenance/coming soon
  - [x] enable storefront kembali
  - [x] module flag cart disabled membuat cart UI tidak tampil
  - [x] public config tidak mengekspos field sensitif

Catatan verifikasi Fase 11:

- `backend/venv/bin/pytest backend/tests` berhasil: 27 passed, 1 warning SQLAlchemy deprecation.
- `npm run check` berhasil: 0 errors, 0 warnings.
- `npm run build` berhasil dan route console/storefront ter-compile.
- Smoke settings dijalankan dengan database SQLite in-memory melalui CRUD/settings:
  - brand name baru terbaca di public storefront config.
  - homepage headline baru terbaca di public storefront config.
  - `storefront_enabled=false` terbaca untuk state maintenance/coming soon.
  - storefront berhasil di-enable kembali.
  - `cart_enabled=false` terbaca di public modules config, sehingga UI cart tetap tersembunyi berdasarkan guard frontend.
  - public config tidak mengekspos `support_email`, `maintenance_mode`, atau `reports_enabled`.
- Smoke API berbasis FastAPI `TestClient` belum dijalankan karena venv backend belum memasang dependency `httpx`; coverage endpoint platform/security tetap terverifikasi oleh existing pytest.

## Final Lifecycle Platform Console

- Platform operator membuka `/console`.
- Platform operator mengelola banyak brand/client dari `/console/brands`.
- Platform operator membuat atau mengubah brand, storefront, SEO, module, dan system settings per brand.
- Backend menyimpan settings secara eksplisit dan brand-scoped.
- Storefront membaca public-safe config berdasarkan brand slug/domain.
- Merchant admin memakai admin area milik brand-nya sendiri.
- Customer hanya melihat storefront dan data milik brand yang sedang dibuka.
- Module seperti cart dan checkout nantinya membaca feature flags sebelum tampil atau menerima request.

## Catatan Keputusan

- Nama yang dipakai adalah **Platform Console**, bukan owner panel, karena merchant/client juga bisa disebut owner bisnis.
- Route awal yang disarankan adalah `/console`.
- Settings dibuat eksplisit per domain agar tidak menjadi key-value bebas yang sulit dirawat.
- CommerceMind harus menjadi multi-brand control plane; single-brand settings yang sudah dibuat hanya baseline/transitional.
- Brand default/demo adalah **CommerceMind** dengan slug `default` dan id `1`; semua legacy `/admin/*` sementara dianggap bekerja di scope brand default ini.
- Brand/Tenant memakai istilah **Brand** di UI agar lebih natural untuk client ecommerce.
- Config storefront hardcoded saat ini akan menjadi fallback saja setelah endpoint dynamic brand config tersedia.
