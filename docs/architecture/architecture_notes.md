# CommerceMind Architecture Notes

## Project Identity

**CommerceMind** adalah platform ecommerce yang dikembangkan secara bertahap untuk pembelajaran, dimulai sebagai sistem CRUD yang tertata dan berkembang menjadi platform commerce dengan analytics serta Decision Engine.

Proyek ini bukan hanya storefront. CommerceMind menjadi sarana pembelajaran teknis untuk membangun kapabilitas ecommerce secara bertahap: catalog, inventory, customers, orders, payments, fulfillment, analytics, dan pada akhirnya decision automation.

## Product Direction

Posisi produk CommerceMind dirumuskan sebagai:

> Platform ecommerce modular yang mengolah data operasional commerce menjadi keputusan bisnis yang lebih baik.

Dalam jangka panjang, arahnya adalah beralih dari **mencatat aktivitas commerce** menjadi **menalar aktivitas commerce**.

Pertanyaan bisnis yang diharapkan dapat dijawab platform pada masa mendatang:

- Produk mana yang perlu di-restock?
- Produk mana yang performanya di bawah harapan?
- Customer mana yang kemungkinan akan membeli kembali?
- Diskon atau bundle mana yang sesuai?
- Keputusan operasional mana yang sebaiknya direkomendasikan secara otomatis?

Setiap fitur cerdas harus didasarkan pada data commerce yang dapat diandalkan. Sistem tidak seharusnya menambahkan AI atau fitur rekomendasi sebelum model operasionalnya dapat dipercaya.

## Default Brand Policy

CommerceMind juga menjadi brand default untuk instalasi lokal/demo.

- Nama default brand: `CommerceMind`
- Slug default brand: `default`
- ID default brand: `1`
- Legacy admin routes di bawah `/admin/*` diperlakukan sebagai panel sementara untuk default brand CommerceMind.
- Brand-scoped merchant admin routes di bawah `/brands/{brandSlug}/admin/*` merupakan arah jangka panjang.
- Sebelum setiap legacy admin panel selesai dipindahkan, tautan dari placeholder brand-scoped ke `/admin/*` sengaja membuka data demo/default CommerceMind.
- Pengembangan brand-scoped baru sebaiknya menggunakan `brand_id` atau `brand_slug` secara eksplisit dan tidak diam-diam mengubah data non-default brand melalui legacy routes.

## Current Architecture

Proyek saat ini merupakan **aplikasi ecommerce modular monolith**.

```text
ecommerce/
├── backend/                 FastAPI, SQLAlchemy, Pydantic
├── frontend/                SvelteKit, TypeScript, Tailwind CSS
├── docs/                    architecture notes and implementation backlog
├── docker-compose.yml       local PostgreSQL service
└── README.md
```

Proyek ini sengaja belum dipisah menjadi microservices. Batas domain terlihat di codebase, tetapi seluruh backend module masih berjalan di dalam satu aplikasi FastAPI dan satu database PostgreSQL.

## Runtime Components

### Backend

Backend entry point:

```text
backend/main.py
```

Tanggung jawab:

- Membuat aplikasi FastAPI.
- Mengonfigurasi CORS untuk frontend SvelteKit lokal.
- Mendaftarkan API routers.
- Membuat tabel SQLAlchemy saat startup untuk fase local-development saat ini.

Backend stack saat ini:

- FastAPI untuk HTTP API.
- SQLAlchemy untuk ORM models dan akses database.
- Pydantic untuk request dan response schemas.
- PostgreSQL sebagai database.

Konfigurasi database:

```text
backend/database.py
```

Koneksi lokal default:

```text
postgresql://myuser:mypassword@localhost:5432/mydb
```

Konfigurasi PostgreSQL lokal didefinisikan di:

```text
docker-compose.yml
```

### Frontend

Frontend app:

```text
frontend/
```

Frontend stack saat ini:

- SvelteKit
- TypeScript
- Tailwind CSS
- lucide-svelte
- local UI components for button, card, badge, and input

Area routes:

```text
/
/admin
/admin/products
/admin/inventory
/admin/customers
/admin/orders
/admin/payments
/storefront
/storefront/products
```

Area admin merupakan bagian frontend yang paling berkembang. Product management telah mendukung daftar, pencarian, pembuatan, pengeditan, penghapusan, toast feedback, dan alur modal.

Storefront saat ini masih berupa placeholder dan direncanakan berkembang setelah workflow inti backend menjadi lebih andal.

## Backend Layering

Backend saat ini mengikuti alur berikut:

```text
API route -> CRUD layer -> SQLAlchemy model -> PostgreSQL
              ^
              |
        Pydantic schema
```

Tanggung jawab layer saat ini:

- `backend/api/`: HTTP route handlers, penghubung request validation, dan API errors.
- `backend/crud/`: operasi database dan workflow sederhana pada tingkat tabel.
- `backend/models/`: definisi tabel SQLAlchemy dan relationships.
- `backend/schema_models/`: request dan response models Pydantic.
- `backend/schemas.py`: compatibility export layer untuk schema models.
- `backend/database.py`: engine, session factory, dan database dependency.

Ketika workflow semakin kompleks pada level domain, routes sebaiknya tetap tipis dan mendelegasikan proses ke service modules. CRUD modules sesuai untuk master data sederhana, sedangkan lifecycle behavior seperti reservation, cancellation, payment outcome, dan fulfillment sebaiknya berada di service-layer functions.

## Domain Boundaries

Current backend domains:

```text
Catalog
- Product

Inventory
- InventoryItem
- InventoryReservation
- InventoryMovement

Customer
- Customer

Order
- Order
- OrderItem

Payment
- Payment

Pricing
- PriceSet
- PriceSetItem
- Channel
- Region
```

Expected future domains:

```text
Fulfillment
- shipment/fulfillment state
- stock deduction trigger

Returns
- return intake
- restock decision

Decision Engine
- rules
- signals
- recommendations
- decision history
```

## Database Relationship Summary

Current core relationships:

```text
products 1 -> 1 inventory_items
products 1 -> many price_sets
price_sets 1 -> many price_set_items
channels 1 -> many price_set_items
regions 1 -> many price_set_items

customers 1 -> many orders
orders 1 -> many order_items
products 1 -> many order_items
orders 1 -> 1 payments

products 1 -> many inventory_reservations
orders 1 -> many inventory_reservations
order_items 1 -> many inventory_reservations
products 1 -> many inventory_movements
```

## Catalog

Tabel `products` merepresentasikan item catalog yang dapat dijual.

```text
products
- id: integer, primary key
- name: string, required, indexed
- description: text, nullable
- base_price: numeric, required
- status: string, required, default draft at database level
- created_at: datetime, required
- updated_at: datetime, required
```

Status product yang diperbolehkan:

```text
draft
active
archived
discontinued
```

Aturan:

- `base_price` menjadi harga fallback sebelum aturan channel, region, atau price set diterapkan.
- Field uang menggunakan nilai numeric dengan presisi tetap.
- Status product sebaiknya merepresentasikan lifecycle tanpa menghapus data historis order.
- Penghapusan permanen sebaiknya dihindari setelah product direferensikan oleh order.

## Pricing

Pricing telah dipisahkan dari model catalog dasar.

```text
price_sets
- id
- product_id
- name
- starts_at
- ends_at
- is_active
- created_at
- updated_at

price_set_items
- id
- price_set_id
- channel_id
- region_id
- price
- currency
- priority
- is_active
- created_at
- updated_at
```

Arahan pricing:

- `Product.base_price` tetap menjadi fallback.
- `PriceSet` mengelompokkan harga alternatif.
- `PriceSetItem` dapat ditujukan ke channel dan region.
- Priority memungkinkan sistem memilih satu harga dari beberapa harga yang cocok nantinya.

## Inventory

Inventory sedang berkembang dari CRUD sederhana menjadi domain ecommerce yang sesungguhnya.

### Inventory Aggregate

Tabel `inventory_items` menyimpan agregat stok terkini untuk setiap product.

```text
inventory_items
- id: integer, primary key
- product_id: integer, required, foreign key -> products.id, unique
- on_hand_quantity: integer, required, default 0
- reserved_quantity: integer, required, default 0
- low_stock_threshold: integer, required, default 0
- created_at: datetime, required
- updated_at: datetime, required
```

Nilai turunan:

```text
available_quantity = on_hand_quantity - reserved_quantity
```

Aturan:

- Untuk saat ini, satu product memiliki satu inventory aggregate.
- `on_hand_quantity` berarti stok yang secara fisik atau logis dimiliki toko.
- `reserved_quantity` berarti stok yang sedang terikat pada active reservations.
- `available_quantity` berarti stok yang masih tersedia untuk dijual.
- `on_hand_quantity` tidak boleh bernilai negatif.
- `reserved_quantity` tidak boleh bernilai negatif.
- `reserved_quantity` tidak boleh melebihi `on_hand_quantity`.

### Inventory Reservations

Tabel `inventory_reservations` mencatat stok yang ditahan untuk order atau order item.

```text
inventory_reservations
- id
- product_id
- order_id
- order_item_id
- quantity
- status
- expires_at
- created_at
- updated_at
```

Status reservation yang diperbolehkan:

```text
active
released
committed
expired
```

Aturan:

- Quantity reservation harus lebih besar dari nol.
- Active reservations menambah `InventoryItem.reserved_quantity`.
- Released atau expired reservations sebaiknya mengurangi `reserved_quantity`.
- Committed reservations merepresentasikan stok yang telah keluar melalui fulfillment.
- Record reservation sebaiknya memungkinkan release atau commit secara tepat per order.

### Inventory Movements

Tabel `inventory_movements` merupakan audit ledger untuk perubahan stok.

```text
inventory_movements
- id
- product_id
- quantity
- movement_type
- reference_type
- reference_id
- notes
- created_at
- updated_at
```

Jenis movement yang diperbolehkan:

```text
inbound
reservation
release
deduction
adjustment
return
```

Aturan:

- Quantity movement harus lebih besar dari nol.
- Setiap aksi stok pada domain sebaiknya membuat row movement.
- `reference_type` dan `reference_id` sebaiknya menunjuk alasan bisnis bila memungkinkan.
- Movement ledger digunakan untuk audit dan observability; agregat tetap berada di `inventory_items`.

## Customers

Tabel `customers` merepresentasikan pembeli.

```text
customers
- id: integer, primary key
- name: string, required
- email: string, required, unique, indexed
- phone: string, nullable
- address: text, nullable
- created_at: datetime, required
- updated_at: datetime, required
```

Aturan:

- Email bersifat unik pada fase single-store saat ini.
- Untuk sementara, address disimpan langsung pada customer.
- Versi mendatang sebaiknya mendukung beberapa address untuk setiap customer.

## Orders

Tabel `orders` merepresentasikan niat pembelian dan status transaksi komersial.

```text
orders
- id: integer, primary key
- customer_id: integer, required, foreign key -> customers.id
- status: string, required, indexed
- total_amount: numeric, required, default 0
- created_at: datetime, required
- updated_at: datetime, required
```

Status order saat ini:

```text
pending
awaiting_payment
paid
processing
fulfilled
completed
cancelled
```

Perilaku saat ini:

- Pembuatan order memvalidasi keberadaan customer.
- Pembuatan order memvalidasi keberadaan setiap product.
- `total_amount` dihitung dari subtotal order items.
- Pembuatan order mereservasi inventory dan mengubah status order menjadi `awaiting_payment`.
- Pembatalan order melepaskan active inventory reservations.
- Payment berstatus `paid` mengubah status order menjadi `paid` tanpa mengurangi stok fisik.
- Fulfillment mengubah status order menjadi `fulfilled` dan mengurangi stok fisik.

Perilaku yang dituju:

- Perubahan status order sebaiknya melalui workflow functions, bukan pembaruan field secara langsung.
- Model fulfillment mendatang dapat memisahkan status shipment dari status order bila workflow membutuhkan detail lebih lanjut.

## Order Items

Tabel `order_items` menyimpan product yang dibeli dalam suatu order.

```text
order_items
- id: integer, primary key
- order_id: integer, required, foreign key -> orders.id
- product_id: integer, required, foreign key -> products.id
- quantity: integer, required
- unit_price: numeric, required
- subtotal: numeric, required
- created_at: datetime, required
- updated_at: datetime, required
```

Aturan:

- `quantity` harus lebih besar dari nol.
- `unit_price` sebaiknya menyalin harga product terpilih pada saat pembelian.
- `subtotal` harus sama dengan `quantity * unit_price`.
- Riwayat order tidak boleh berubah jika harga product berubah kemudian.

## Payments

Tabel `payments` menyimpan payment records untuk order.

```text
payments
- id: integer, primary key
- order_id: integer, required, foreign key -> orders.id, unique
- status: string, required, indexed
- method: string, required
- amount: numeric, required
- paid_at: datetime, nullable
- created_at: datetime, required
- updated_at: datetime, required
```

Status payment saat ini:

```text
pending
paid
failed
refunded
```

Metode payment saat ini:

```text
manual
bank_transfer
cash
```

Perilaku saat ini:

- Satu order dapat memiliki satu payment record.
- Mengubah status payment menjadi `paid` mengisi `paid_at` bila masih kosong.
- Payment `paid` mengubah status order menjadi `paid` tanpa mengurangi stok fisik.
- Payment `failed` melepaskan active reservation dan membatalkan order.
- Payment `refunded` tidak mengisi ulang inventory.

Perilaku yang dituju:

- Restock sebaiknya dilakukan melalui proses return/receiving yang terpisah.

## Ecommerce Lifecycle Target

The target lifecycle separates payment, reservation, fulfillment, refund, and return.

```text
order create
-> validate available stock
-> create order and order items
-> create active reservations
-> increase reserved_quantity
-> create reservation movements

order cancel
-> release active reservations
-> decrease reserved_quantity
-> create release movements
-> mark order cancelled

payment paid
-> mark payment paid
-> set paid_at
-> move order to paid
-> do not deduct on_hand_quantity yet

payment failed
-> mark payment failed
-> release active reservations
-> mark order cancelled

fulfillment/shipping
-> commit active reservations
-> decrease reserved_quantity
-> decrease on_hand_quantity
-> create deduction movements

refund
-> mark payment refunded
-> do not restock automatically

return received
-> receive stock back if item is resellable
-> increase on_hand_quantity
-> create return movement
```

Lifecycle ini dijelaskan lebih lanjut dalam:

```text
docs/archive/initial-planning/todo_inventory_architecture.md
```

## API Surface

Backend routers yang terdaftar saat ini:

```text
/products
/inventory-items
/customers
/orders
/order-items
/payments
```

Gaya API saat ini:

- Master data menggunakan CRUD routes biasa.
- Orders menyediakan routes untuk create, read, update, update status, cancel, dan delete.
- Payments menyediakan routes untuk create, read, update, update status, dan delete.
- Inventory masih menyediakan CRUD untuk aggregate item.

Gaya API yang dituju:

- Pertahankan CRUD sederhana untuk master data seperti products, customers, regions, dan channels.
- Tambahkan action-based inventory endpoints untuk domain commands:
  - receive stock
  - adjust stock
  - reserve stock
  - release reservation
  - commit reservation
- Hindari menjadikan perubahan angka stok secara manual sebagai jalur bisnis utama.

## Frontend Architecture

Struktur routes frontend:

```text
frontend/src/routes/
├── +page.svelte                 application area selector
├── admin/
│   ├── +layout.svelte           admin shell and navigation
│   ├── +page.svelte             dashboard overview
│   ├── products/+page.svelte    product management
│   ├── inventory/+page.svelte
│   ├── customers/+page.svelte
│   ├── orders/+page.svelte
│   └── payments/+page.svelte
└── storefront/
    ├── +layout.svelte
    ├── +page.svelte
    └── products/+page.svelte
```

Struktur library frontend:

```text
frontend/src/lib/
├── api/                         API clients
├── components/ui/               shared UI primitives
├── admin/                       admin-specific helpers, currently minimal
├── storefront/                  storefront-specific helpers, currently minimal
└── utils.ts
```

Kondisi frontend saat ini:

- Navigasi admin telah tersedia.
- Admin products merupakan workflow yang paling lengkap.
- Halaman admin lainnya dan halaman storefront direncanakan berkembang setelah workflow backend stabil.

## Service Layer Direction

Langkah arsitektur backend besar berikutnya adalah menambahkan service functions untuk business workflows.

Service module yang direkomendasikan untuk jangka dekat:

```text
backend/crud/inventory_service.py
```

Service functions awal:

```text
receive_stock(product_id, quantity, reference, notes)
adjust_stock(product_id, delta, reference, notes)
reserve_stock_for_order(order_id)
release_stock_for_order(order_id, reason)
commit_stock_for_order(order_id)
```

Setiap service function sebaiknya:

- Memperbarui inventory aggregate.
- Membuat reservations bila relevan.
- Membuat inventory movement rows.
- Menjaga stock invariants.
- Gagal bila stok tidak mencukupi.
- Berjalan di dalam transaction agar pembaruan workflow yang parsial tidak tersimpan.

Seiring waktu, service modules dapat dipindahkan dari `backend/crud/` ke folder domain yang lebih jelas, misalnya:

```text
backend/inventory/service.py
backend/orders/service.py
backend/payments/service.py
```

Pemindahan tersebut sebaiknya dilakukan ketika logika workflow sudah cukup besar untuk membenarkan batas package baru.

## Engineering Principles

CommerceMind sebaiknya dibangun dengan prinsip berikut:

- **Sederhana dahulu, modular sejak awal**: hindari microservices prematur, tetapi pertahankan batas domain agar terlihat.
- **Akurasi data sebelum intelligence**: recommendations hanya berguna bila source data dapat dipercaya.
- **Business logic di luar routes**: API routes sebaiknya tetap tipis saat workflow berkembang.
- **CRUD sesuai untuk master data**: transaction workflows memerlukan orkestrasi service-layer.
- **Schema changes direncanakan dengan cermat**: terapkan migrations sebelum data model menjadi penting.
- **Tests mengikuti risiko**: prioritaskan inventory invariants, order lifecycle, payment behavior, dan API contracts.
- **Setiap abstraction harus punya alasan kuat**: tambahkan layer bila mengurangi kompleksitas nyata.

## Current Gaps

Gap arsitektur yang diketahui:

- Storefront pages sebagian besar masih berupa placeholder.
- Admin inventory/order/payment pages masih memerlukan pekerjaan UI untuk backend workflows yang sudah tersedia.
- Return handling saat ini direpresentasikan oleh receive-stock commands dengan return references; returns domain yang lebih lengkap dapat ditambahkan kemudian.

## Near-Term Roadmap

Urutan implementasi yang direkomendasikan:

1. Kembangkan halaman admin inventory, orders, dan payments berdasarkan domain command endpoints.
2. Bangun product browsing storefront berdasarkan active products dan inventory yang tersedia.
3. Tambahkan returns domain khusus bila proses penerimaan return memerlukan inspeksi, penentuan kondisi, atau hasil selain restock.
4. Perkenalkan Decision Engine berbasis rules pertama hanya setelah tersedia cukup data operasional.

## Decision Engine Definition

Decision Engine merupakan intelligence layer CommerceMind pada masa mendatang.

Tugasnya menghasilkan recommendations atau decisions dari data commerce. Versi awal sebaiknya berbasis rules. Versi berikutnya dapat menggunakan scoring, statistical signals, atau keputusan yang dibantu model.

Contoh keputusan awal:

- Merekomendasikan restock saat stok turun di bawah threshold.
- Menandai products dengan penjualan rendah dan inventory tinggi.
- Menyarankan kandidat discount berdasarkan usia, stok, dan sales velocity.
- Mengurutkan products terlaris dalam suatu periode.

Decision Engine sebaiknya menyimpan decision outputs agar sistem dapat menjelaskan rekomendasi yang diberikan beserta alasannya.

Decision Engine sebaiknya dibangun di atas commerce workflows yang andal. Komponen ini tidak boleh menjadi pengganti data catalog, inventory, order, payment, fulfillment, dan return yang akurat.

## Non-Goals For Now

CommerceMind belum perlu memprioritaskan hal-hal berikut:

- Microservices.
- Distributed event streaming.
- Fitur AI kompleks sebelum data commerce dapat diandalkan.
- Integrasi payment gateway sebelum order model stabil.
- Kompleksitas marketplace atau multi-tenant sebelum single-store domain kokoh.
- Promotion engines sebelum pricing, inventory, dan order lifecycle andal.

Hal-hal tersebut mungkin relevan di kemudian hari, tetapi bukan batasan awal yang tepat.
