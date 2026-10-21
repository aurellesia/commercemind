# Todo Products Architecture

Tujuan dokumen ini adalah menyimpan backlog refactor modul products agar naik dari CRUD catalog sederhana menjadi domain product ecommerce yang siap terhubung ke inventory, pricing, storefront, dan order lifecycle.

## Kondisi Saat Ini

Modul products saat ini sudah memiliki:

- `products.id`
- `products.name`
- `products.description`
- `products.base_price`
- `products.status`
- `created_at`
- `updated_at`

Status product yang tersedia:

- `draft`
- `active`
- `archived`
- `discontinued`

Relasi yang sudah ada:

- product 1 -> 1 inventory item
- product 1 -> many price sets
- product 1 -> many order items
- product 1 -> many inventory reservations
- product 1 -> many inventory movements

Gap utama:

- product belum punya `slug` / SKU public-friendly
- product belum punya detail skincare seperti BPOM, cara pakai, dan komposisi
- product belum punya `cost_price` untuk margin/profit internal
- product image masih belum dimodelkan
- hard delete product masih tersedia
- product status belum mengontrol purchasability
- products admin belum menampilkan inventory summary
- storefront products masih placeholder
- order creation belum menghitung harga server-side dari product/pricing

## Prinsip Desain

- `Product.id` tetap menjadi identifier internal dan foreign key database.
- `Product.slug` menjadi identifier publik untuk URL storefront.
- `Product.base_price` tetap menjadi fallback harga jual.
- `Product.cost_price` menjadi harga modal internal dan tidak boleh tampil di storefront.
- Harga jual final nantinya dipilih dari `PriceSet` bila ada, fallback ke `base_price`.
- Product yang sudah punya histori order/inventory tidak boleh hard delete.
- Product status harus memengaruhi apakah item bisa ditampilkan dan dipesan.
- Inventory tetap menjadi source of truth stok; product hanya menampilkan ringkasan availability.

## Fase 1 — Product Schema Enrichment

- [x] Tambahkan field product detail:
  - [x] `slug`
  - [x] `sku`
  - [x] `bpom_number`
  - [x] `usage_instructions`
  - [x] `ingredients`
  - [x] `storage_instructions`
  - [x] `warnings`
  - [x] `net_weight`
- [x] Tambahkan field pricing internal:
  - [x] `cost_price`
  - [x] pastikan `base_price` tetap menjadi harga jual fallback
- [x] Tambahkan constraint/index:
  - [x] `slug` unique
  - [x] `sku` unique
  - [x] `cost_price >= 0`
  - [x] `base_price >= 0` tetap aktif
- [x] Buat Alembic migration untuk field baru
- [x] Update SQLAlchemy model `Product`
- [x] Update Pydantic schema `ProductCreate`, `ProductUpdate`, dan `Product`
- [x] Update frontend type `Product`, `ProductCreate`, dan `ProductUpdate`

## Fase 2 — Product Images

- [x] Tambahkan tabel `product_images`
  - [x] `id`
  - [x] `product_id`
  - [x] `image_url`
  - [x] `alt_text`
  - [x] `sort_order`
  - [x] `is_primary`
  - [x] `created_at`
  - [x] `updated_at`
- [x] Tambahkan constraint/index:
  - [x] foreign key ke `products.id`
  - [x] index `product_id`
  - [x] index `is_primary`
  - [x] `sort_order >= 0`
- [x] Tambahkan model SQLAlchemy `ProductImage`
- [x] Tambahkan Pydantic schema:
  - [x] `ProductImageCreate`
  - [x] `ProductImageUpdate`
  - [x] `ProductImage`
- [x] Tambahkan CRUD product images
- [x] Tambahkan API product images:
  - [x] list images by product
  - [x] add image
  - [x] update image
  - [x] delete image
  - [x] set primary image
- [x] Pastikan hanya satu primary image per product secara logic/service

Catatan verifikasi Fase 2:

- Migration `20260425_0005_add_product_images` sukses dijalankan.
- Smoke test API lokal sukses: tambah dua image, set primary image kedua, delete image pertama, dan tersisa satu primary image.
- `backend/venv/bin/pytest backend/tests/test_inventory_lifecycle.py` sukses.
- `npm run check` sukses tanpa error/warning.

## Fase 3 — Product Lifecycle Guard

- [x] Audit hard delete product
- [x] Cegah hard delete bila product punya:
  - [x] order items
  - [x] inventory item
  - [x] inventory movements
  - [x] inventory reservations
  - [x] price sets
- [x] Tambahkan lifecycle actions:
  - [x] archive product
  - [x] discontinue product
  - [x] reactivate product
- [x] Hard delete hanya diizinkan untuk product aman/draft tanpa dependency
- [x] Update API response error agar jelas saat delete ditolak
- [x] Update admin products UI agar delete tidak menjadi workflow utama untuk product yang sudah punya histori

Catatan verifikasi Fase 3:

- Hard delete product draft tanpa dependency sukses.
- Hard delete product dengan inventory item/movement ditolak `409 Conflict` dengan detail blocker.
- Lifecycle actions `archive`, `discontinue`, dan `reactivate` sukses via API.
- Admin products UI menampilkan archive/discontinue/reactivate sebagai workflow utama; hard delete hanya ditampilkan untuk draft.
- `backend/venv/bin/pytest backend/tests/test_inventory_lifecycle.py` sukses.
- `npm run check` sukses tanpa error/warning.

## Fase 4 — Product Availability Read Model

- [x] Buat read model product availability
- [x] Include data:
  - [x] product id
  - [x] name
  - [x] slug
  - [x] sku
  - [x] status
  - [x] base_price
  - [x] effective sell price bila pricing sudah tersedia
  - [x] primary image
  - [x] inventory `on_hand_quantity`
  - [x] inventory `reserved_quantity`
  - [x] inventory `available_quantity`
  - [x] `is_low_stock`
  - [x] `is_purchasable`
  - [x] `not_purchasable_reason`
- [x] Buat endpoint:
  - [x] `GET /products/catalog`
  - [x] `GET /products/{product_id}/availability`
  - [x] `GET /products/by-slug/{slug}`
- [x] Rule awal `is_purchasable`:
  - [x] product status harus `active`
  - [x] available quantity harus lebih dari `0`
  - [x] harga jual valid harus tersedia
- [x] Pastikan product tanpa inventory aggregate mengembalikan availability `0`

Catatan verifikasi Fase 4:

- Product tanpa inventory aggregate mengembalikan availability `0` dan `not_purchasable_reason = Product is out of stock`.
- Setelah receive stock, product active dengan available quantity `4` menjadi purchasable.
- Primary image tampil pada read model availability.
- `GET /products/by-slug/{slug}` sukses mengembalikan product availability.
- Product discontinued menjadi tidak purchasable dengan reason `Product status is discontinued`.
- `backend/venv/bin/pytest backend/tests/test_inventory_lifecycle.py` sukses.
- `npm run check` sukses tanpa error/warning.

## Fase 5 — Admin Products UI Upgrade

- [x] Update form create/edit product:
  - [x] slug
  - [x] sku
  - [x] BPOM
  - [x] cara pakai
  - [x] komposisi
  - [x] storage instructions
  - [x] warnings
  - [x] net weight
  - [x] cost price
  - [x] base sell price
- [x] Tambahkan helper/copy jelas:
  - [x] cost price hanya internal
  - [x] base price adalah harga jual fallback
- [x] Tambahkan auto-generate slug dari name
- [x] Tambahkan inventory summary di tabel products:
  - [x] available quantity
  - [x] low stock badge
  - [x] tracked / not tracked indicator
- [x] Tambahkan image management sederhana:
  - [x] list image URLs
  - [x] add image URL
  - [x] mark primary
  - [x] remove image
- [x] Pisahkan image management ke submenu Products:
  - [x] `Product List`
  - [x] `Product Images`
- [x] Tambahkan product detail panel/page admin:
  - [x] catalog info
  - [x] inventory summary
  - [x] primary image summary
  - [x] price summary
  - [x] recent inventory movements
  - [x] active reservations

Catatan verifikasi Fase 5:

- Admin products UI memakai read model availability untuk menampilkan purchasability dan stok.
- Form create/edit sudah mencakup detail skincare, slug/SKU, cost price internal, dan base sell price.
- Detail panel admin sudah memuat catalog info, price summary, inventory summary, primary image summary, recent movements, dan active reservations.
- Image management sederhana dipisah ke `/admin/products/images`: add URL, set primary, dan remove.
- `npm run check` sukses tanpa error/warning.

## Fase 6 — Storefront Catalog

- [x] Ganti placeholder `frontend/src/routes/storefront/products/+page.svelte`
- [x] Tampilkan hanya product yang purchasable atau minimal active
- [x] Tampilkan product card:
  - [x] primary image
  - [x] name
  - [x] short description
  - [x] effective sell price
  - [x] availability / stock label
- [x] Tambahkan product detail route by slug:
  - [x] `/storefront/products/[slug]`
- [x] Product detail menampilkan:
  - [x] image gallery
  - [x] BPOM
  - [x] cara pakai
  - [x] komposisi
  - [x] warnings
  - [x] price
  - [x] availability
- [x] Jangan tampilkan `cost_price` di storefront

Catatan verifikasi Fase 6:

- Storefront catalog membaca `ProductAvailability` dari `/products/catalog`.
- Storefront detail memakai read model khusus `ProductStorefrontDetail` dari `/products/by-slug/{slug}/detail`.
- `ProductStorefrontDetail` membawa detail skincare dan gallery, tetapi tidak mengekspos `cost_price`.
- `npm run check` sukses tanpa error/warning.
- `backend/venv/bin/pytest backend/tests/test_inventory_lifecycle.py` sukses.

## Fase 7 — Order Lifecycle Integration

- [x] Validasi order creation terhadap product lifecycle:
  - [x] product harus ada
  - [x] product harus `active`
  - [x] product harus purchasable
  - [x] available stock cukup
- [x] Jangan percaya `unit_price` dari payload public storefront
- [x] Hitung order item price server-side:
  - [x] pakai effective price dari `PriceSet` bila ada
  - [x] fallback ke `Product.base_price`
- [x] Simpan snapshot product di order item:
  - [x] product name saat order dibuat
  - [x] sku saat order dibuat
  - [x] slug saat order dibuat
  - [x] price source
- [x] Pertimbangkan pemisahan endpoint admin order manual dan storefront checkout

Catatan verifikasi Fase 7:

- Migration `20260425_0006_add_order_item_product_snapshots` menambahkan snapshot product dan `price_source` di `order_items`.
- `create_order` menghitung `unit_price`, `subtotal`, dan `total_amount` server-side; nilai harga dari payload client diabaikan.
- Harga order memakai active `PriceSetItem` bila tersedia, fallback ke `Product.base_price`.
- Product non-active ditolak saat order creation.
- Insufficient stock tetap rollback order dan reservation.
- Endpoint order item manual ikut memakai server-side product price, tetapi belum dijadikan flow utama checkout.
- `backend/venv/bin/alembic upgrade head` sukses.
- `backend/venv/bin/pytest backend/tests/test_inventory_lifecycle.py` sukses.
- `npm run check` sukses tanpa error/warning.

## Fase 8 — Reporting Foundation

- [x] Tambahkan data yang cukup untuk margin:
  - [x] order item sell price snapshot
  - [x] product cost price snapshot
- [x] Siapkan query/report:
  - [x] gross revenue per product
  - [x] estimated gross margin per product
  - [x] slow moving products
  - [x] low stock active products
  - [x] discontinued products with remaining stock

Catatan verifikasi Fase 8:

- Migration `20260425_0007_add_order_item_cost_snapshot` menambahkan `product_cost_price_snapshot` di `order_items`.
- Report revenue dan margin memakai snapshot `unit_price`, `subtotal`, dan `product_cost_price_snapshot`.
- Endpoint reporting tersedia:
  - `GET /reports/products`
  - `GET /reports/products/summary`
  - `GET /reports/products/revenue`
  - `GET /reports/products/slow-moving`
  - `GET /reports/products/low-stock-active`
  - `GET /reports/products/discontinued-with-stock`
- `backend/venv/bin/alembic upgrade head` sukses.
- `backend/venv/bin/pytest backend/tests/test_inventory_lifecycle.py backend/tests/test_product_reporting.py` sukses.
- `npm run check` sukses tanpa error/warning.

## Fase 9 — Polish dan Verifikasi

- [x] Jalankan backend tests
- [x] Jalankan `npm run check`
- [x] Smoke test manual:
  - [x] create product dengan detail skincare
  - [x] slug unik dan bisa dipakai fetch product
  - [x] add multiple images
  - [x] set primary image
  - [x] receive stock untuk product baru
  - [x] product muncul di catalog bila active dan available
  - [x] product tidak purchasable bila discontinued
  - [x] order creation menolak product non-active
  - [x] order price dihitung server-side
- [x] Dokumentasikan final lifecycle product

Catatan verifikasi Fase 9:

- `backend/venv/bin/pytest backend/tests` sukses.
- `npm run check` sukses tanpa error/warning.
- Smoke test lokal sukses dengan output `SMOKE_OK product_id=1 slug=smoke-glow-serum images=2 order_total=158000.00`.

## Final Lifecycle Product

- Admin membuat product dengan catalog identity:
  - `name`
  - `slug`
  - `sku`
  - skincare details seperti BPOM, cara pakai, komposisi, storage, warnings, dan net weight
  - `cost_price` internal
  - `base_price` sebagai fallback harga jual
- Product image dikelola terpisah di submenu `Products > Product Images`.
- Product storefront menggunakan `slug`, bukan `id`.
- Product yang bisa dibeli harus:
  - status `active`
  - punya available stock lebih dari `0`
  - punya harga jual valid dari active `PriceSetItem` atau fallback `base_price`
- Inventory menjadi source of truth stok.
- Storefront catalog membaca product availability dan tidak pernah mengekspos `cost_price`.
- Order creation tidak mempercayai harga dari client.
- Order item price dihitung server-side:
  - active `PriceSetItem` bila ada
  - fallback ke `Product.base_price`
- Order item menyimpan snapshot:
  - sell price snapshot di `unit_price`
  - product cost snapshot di `product_cost_price_snapshot`
  - product name, SKU, slug, dan price source
- Product yang sudah punya histori order, inventory, reservation, movement, atau price set tidak boleh hard delete.
- Untuk lifecycle operasional gunakan:
  - `archive` untuk menyembunyikan product dari operasi aktif tanpa menghentikan histori
  - `discontinue` untuk menghentikan penjualan product
  - `reactivate` untuk mengaktifkan kembali product
- Reporting product memakai snapshot order item agar revenue dan margin historis tidak berubah ketika master product berubah.

## Catatan Keputusan

- `base_price` tidak diganti nama menjadi `sell_price` untuk menjaga kompatibilitas dan karena sudah diposisikan sebagai fallback harga jual.
- `cost_price` ditambahkan sebagai field internal untuk margin/reporting.
- Product images dibuat sebagai tabel terpisah, bukan string/list di `products`, agar storefront gallery dan primary image lebih mudah dikontrol.
- `slug` dipakai untuk URL publik; `id` tetap dipakai untuk relasi internal.
