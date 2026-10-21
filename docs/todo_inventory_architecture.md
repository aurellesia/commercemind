# TODO Inventory Architecture

Tanggal dibuat: 2026-04-22

Tujuan dokumen ini adalah menyimpan backlog refactor modul inventory agar sesuai dengan lifecycle ecommerce: order create → reservation → payment outcome → fulfillment/shipping → return/refund.

## Ringkasan masalah saat ini

Modul inventory yang ada masih berupa CRUD sederhana pada `inventory_items` dengan field utama:

- `product_id`
- `quantity`
- `reserved_quantity`
- `low_stock_threshold`

Gap terhadap lifecycle ecommerce:

- stok masih diubah sebagai angka langsung, belum lewat aksi domain
- belum ada reservation per order
- belum ada movement ledger untuk audit perubahan stok
- belum ada pemisahan jelas antara stok fisik dan stok yang bisa dijual
- belum ada titik commit stock saat fulfillment/shipping
- payment dan order lifecycle belum terhubung ke inventory lifecycle

## Prinsip arsitektur target

- jadikan inventory sebagai domain, bukan sekadar tabel angka
- pisahkan aggregate stok saat ini dari log pergerakan stok
- simpan reservation per order agar bisa di-release / di-commit secara presisi
- deduct stok fisik saat fulfillment, bukan otomatis saat payment paid
- return/restock harus diproses terpisah dari refund payment

## Todo utama

- [x] Refactor `InventoryItem`
  - [x] Rename `quantity` menjadi `on_hand_quantity`
  - [x] Pertahankan `reserved_quantity`
  - [x] Pertahankan `low_stock_threshold`
  - [x] Tambahkan konsep `available_quantity` sebagai derived value
  - [x] Pastikan invariant tetap berlaku:
    - [x] `on_hand_quantity >= 0`
    - [x] `reserved_quantity >= 0`
    - [x] `reserved_quantity <= on_hand_quantity`

- [x] Tambahkan model `InventoryReservation`
  - [x] Relasi ke `product_id`
  - [x] Relasi ke `order_id`
  - [x] Relasi ke `order_item_id` jika diperlukan
  - [x] Simpan `quantity`
  - [x] Tambahkan status:
    - [x] `active`
    - [x] `released`
    - [x] `committed`
    - [x] `expired`
  - [x] Tambahkan `expires_at` bila reservation ingin punya TTL
  - [x] Tambahkan timestamp audit (`created_at`, `updated_at`)

- [x] Tambahkan model `InventoryMovement`
  - [x] Relasi ke `product_id`
  - [x] Simpan `quantity`
  - [x] Tambahkan tipe movement:
    - [x] `inbound`
    - [x] `reservation`
    - [x] `release`
    - [x] `deduction`
    - [x] `adjustment`
    - [x] `return`
  - [x] Simpan `reference_type`
  - [x] Simpan `reference_id`
  - [x] Simpan `notes`
  - [x] Tambahkan timestamp audit (`created_at`, `updated_at`)

- [x] Tambahkan schema Pydantic untuk inventory domain
  - [x] Update schema `InventoryItemBase`, `InventoryItemCreate`, `InventoryItemUpdate`, `InventoryItem`
  - [x] Tambahkan enum reservation status
  - [x] Tambahkan enum movement type
  - [x] Tambahkan schema `InventoryReservationCreate/Update/Read`
  - [x] Tambahkan schema `InventoryMovementRead`
  - [x] Tambahkan command payload untuk:
    - [x] receive stock
    - [x] adjust stock
    - [x] reserve stock
    - [x] release reservation
    - [x] commit reservation

- [x] Buat service layer inventory
  - [x] Buat file service baru, misalnya `backend/crud/inventory_service.py`
  - [x] Implementasikan `reserve_stock_for_order(order_id)`
  - [x] Implementasikan `release_stock_for_order(order_id, reason)`
  - [x] Implementasikan `commit_stock_for_order(order_id)`
  - [x] Implementasikan `receive_stock(product_id, quantity, reason)`
  - [x] Implementasikan `adjust_stock(product_id, delta, reason)`
  - [x] Pastikan semua method:
    - [x] update aggregate inventory
    - [x] membuat row reservation bila relevan
    - [x] membuat row movement
    - [x] menjaga invariant stok
    - [x] gagal bila stok tidak cukup

- [x] Integrasikan inventory ke lifecycle order
  - [x] Saat `create_order`, validasi `available_to_sell`
  - [x] Saat order dibuat, reserve stock
  - [x] Saat order dibatalkan, release reservation
  - [x] Hindari update stok manual langsung dari endpoint order

- [x] Integrasikan inventory ke lifecycle payment
  - [x] Saat payment `paid`, order pindah ke state yang tepat tanpa langsung mengurangi stok fisik
  - [x] Saat payment `failed`, release reservation bila bisnis rule mengharuskan
  - [x] Saat `refunded`, jangan otomatis restock tanpa proses return barang
  - [x] Samakan decision point payment dengan rule inventory yang dipilih

- [x] Tambahkan lifecycle fulfillment
  - [x] Tambahkan status order/fulfillment yang menandai barang benar-benar keluar gudang
  - [x] Saat fulfillment/shipping:
    - [x] kurangi `reserved_quantity`
    - [x] kurangi `on_hand_quantity`
    - [x] ubah reservation menjadi `committed`
    - [x] buat movement `deduction`
  - [x] Pisahkan event “payment sukses” dari event “barang keluar gudang”

- [x] Revisi status domain agar lebih cocok untuk ecommerce lifecycle
  - [x] Evaluasi perluasan `OrderStatus`, misalnya:
    - [x] `pending`
    - [x] `awaiting_payment`
    - [x] `paid`
    - [x] `processing`
    - [x] `fulfilled`
    - [x] `completed`
    - [x] `cancelled`
  - [x] Evaluasi perluasan `PaymentStatus`, misalnya:
    - [x] `pending`
    - [x] `paid`
    - [x] `failed`
    - [x] `refunded`
  - [x] Pertimbangkan `FulfillmentStatus` terpisah bila dibutuhkan

- [x] Tambahkan endpoint / API berbasis aksi domain
  - [x] `receive stock`
  - [x] `adjust stock`
  - [x] `reserve stock`
  - [x] `release reservation`
  - [x] `commit reservation`
  - [x] Hindari menjadikan admin update angka stok sebagai jalur utama bisnis

- [x] Tambahkan observability untuk admin
  - [x] Riwayat movement per product
  - [x] Active reservation per product
  - [x] Active reservation per order
  - [x] Low stock indicator
  - [x] Derived field `available_quantity`

- [x] Tambahkan validasi dan proteksi data
  - [x] Cek stok cukup sebelum reservation
  - [x] Cegah commit jika reservation tidak aktif
  - [x] Cegah release ganda
  - [x] Cegah deduction langsung tanpa referensi domain yang jelas
  - [x] Pastikan rollback transaksi saat salah satu langkah domain gagal

- [x] Tambahkan test coverage
  - [x] Test create order dengan stok cukup
  - [x] Test create order dengan stok tidak cukup
  - [x] Test cancel order me-release reservation
  - [x] Test payment failed sesuai rule reservation
  - [x] Test fulfillment mengurangi `on_hand_quantity`
  - [x] Test refund tidak otomatis restock
  - [x] Test return menambah stok kembali
  - [x] Test invariant inventory aggregate

- [x] Dokumentasikan lifecycle inventory
  - [x] Tambahkan flow order → reserve
  - [x] Tambahkan flow cancel/payment fail → release
  - [x] Tambahkan flow fulfill → commit/deduct
  - [x] Tambahkan flow refund vs return
  - [x] Jelaskan perbedaan:
    - [x] `on_hand_quantity`
    - [x] `reserved_quantity`
    - [x] `available_quantity`

## Urutan implementasi yang disarankan

### Fase 1 — Fondasi model
- [x] Refactor `InventoryItem`
- [x] Tambahkan `InventoryReservation`
- [x] Tambahkan `InventoryMovement`
- [x] Tambahkan schema dan enum yang dibutuhkan

### Fase 2 — Domain service
- [x] Buat `inventory_service`
- [x] Implementasikan receive / adjust / reserve / release / commit
- [x] Pastikan semua path membuat movement log

### Fase 3 — Integrasi lifecycle
- [x] Integrasikan ke `create_order`
- [x] Integrasikan ke `cancel_order`
- [x] Integrasikan ke payment flow
- [x] Tambahkan fulfillment step

### Fase 4 — API, observability, dan testing
- [x] Tambahkan endpoint domain commands
- [x] Tambahkan query riwayat movement dan reservation
- [x] Tambahkan test
- [x] Dokumentasikan lifecycle final

## Catatan keputusan bisnis yang perlu dipastikan nanti

- [ ] Apakah stock di-reserve saat order dibuat atau saat payment paid?
- [ ] Apakah reservation punya expiry?
- [ ] Apakah payment failed langsung release reservation?
- [ ] Apakah refund tanpa return boleh mempengaruhi stok?
- [ ] Apakah fulfillment status dipisah dari order status?

## Backlog UI Admin Inventory

Tujuan backlog ini adalah membuat backend inventory lifecycle yang sudah ada bisa dipakai admin secara bertahap lewat UI.

### Fase UI 1 — API client frontend

- [x] Buat `frontend/src/lib/api/inventory.ts`
- [x] Tambahkan type frontend untuk:
  - [x] `InventoryItem`
  - [x] `InventoryMovement`
  - [x] `InventoryReservation`
  - [x] command payload `ReceiveStockCommand`
  - [x] command payload `AdjustStockCommand`
  - [x] command payload `ReserveStockCommand`
  - [x] command payload `ReleaseReservationCommand`
  - [x] command payload `CommitReservationCommand`
- [x] Implementasikan API method:
  - [x] list inventory items
  - [x] get inventory by product
  - [x] get low-stock items
  - [x] get product movement history
  - [x] get active reservations by product
  - [x] get active reservations by order
  - [x] receive stock
  - [x] adjust stock
  - [x] reserve stock
  - [x] release reservation
  - [x] commit reservation

### Fase UI 2 — Inventory overview page

- [x] Ganti placeholder `frontend/src/routes/admin/inventory/+page.svelte`
- [x] Tampilkan summary cards:
  - [x] total SKU tracked
  - [x] total `on_hand_quantity`
  - [x] total `reserved_quantity`
  - [x] total `available_quantity`
  - [x] low stock count
- [x] Tampilkan tabel inventory:
  - [x] product id / product name bila tersedia
  - [x] `on_hand_quantity`
  - [x] `reserved_quantity`
  - [x] `available_quantity`
  - [x] `low_stock_threshold`
  - [x] low stock indicator
- [x] Tambahkan search/filter sederhana
- [x] Tambahkan loading, empty, dan error states

### Fase UI 3 — Domain action controls

- [x] Tambahkan action modal `receive stock`
  - [x] pilih product / inventory item
  - [x] input quantity
  - [x] input notes/reference
  - [x] refresh list setelah sukses
- [x] Tambahkan action modal `adjust stock`
  - [x] pilih product / inventory item
  - [x] input delta positif/negatif
  - [x] input reason wajib
  - [x] tampilkan error bila adjustment melanggar invariant
- [x] Hindari menjadikan edit angka stok langsung sebagai workflow utama
- [x] Pertahankan update manual aggregate hanya untuk kebutuhan admin/debug yang jelas

### Fase UI 4 — Observability detail panel

- [x] Tambahkan detail drawer/panel per inventory item
- [x] Tampilkan movement history per product:
  - [x] movement type
  - [x] quantity
  - [x] reference type/id
  - [x] notes
  - [x] timestamp
- [x] Tampilkan active reservation per product:
  - [x] reservation id
  - [x] order id
  - [x] order item id
  - [x] quantity
  - [x] status
  - [x] expires_at
- [x] Tambahkan empty state untuk produk tanpa movement/reservation

### Fase UI 5 — Reservation operation controls

- [x] Tambahkan action `release reservation` dari active reservation list
- [x] Tambahkan action `commit reservation` dari active reservation list
- [x] Tampilkan konfirmasi sebelum release/commit
- [x] Refresh inventory aggregate, movement history, dan reservation list setelah action
- [x] Tampilkan error domain:
  - [x] reservation tidak aktif
  - [x] stok tidak cukup
  - [x] reservation tidak ditemukan

### Fase UI 6 — Polish dan verifikasi

- [x] Pastikan UI konsisten dengan admin products style
- [x] Pastikan layout responsif desktop/mobile
- [x] Pastikan angka inventory tidak menyebabkan layout shift
- [x] Tambahkan smoke test manual:
  - [x] receive stock menaikkan `on_hand_quantity`
  - [x] adjust stock mengubah `on_hand_quantity`
  - [x] reserve stock menaikkan `reserved_quantity`
  - [x] release reservation menurunkan `reserved_quantity`
  - [x] commit reservation menurunkan `reserved_quantity` dan `on_hand_quantity`
- [x] Pertimbangkan test UI/API client setelah dependency test frontend siap

Catatan verifikasi 2026-04-25:

- `npm run check` sukses tanpa error/warning.
- Smoke test API lokal sukses pada product test `Inventory Smoke Product #3`.
- Final aggregate smoke test: `on_hand_quantity=6`, `reserved_quantity=0`, `available_quantity=6`.
- Dependency test frontend khusus UI/API client belum tersedia; sementara verifikasi dilakukan dengan `svelte-check` dan smoke test API manual.

## File yang kemungkinan akan disentuh saat implementasi

- `backend/models/inventory.py`
- `backend/models/orders.py`
- `backend/models/payments.py`
- `backend/schemas.py`
- `backend/crud/inventory_items.py`
- `backend/crud/orders.py`
- `backend/crud/payments.py`
- `backend/api/inventory_items.py`
- file baru seperti:
  - `backend/crud/inventory_service.py`
  - model/schema/api tambahan untuk reservation dan movement bila dipisah

## Definisi singkat target akhir

Source of truth inventory yang sehat untuk ecommerce:

- aggregate stok saat ini
- reservation records per order
- movement ledger untuk audit
- hook lifecycle:
  - order create → reserve
  - order cancel / payment fail → release
  - fulfillment / shipping → deduct
  - return received → restock

## Lifecycle inventory final

### 1. Order dibuat → reserve stock

Saat order dibuat melalui `create_order`:

- sistem menghitung `total_amount` dari order items
- sistem memvalidasi stok melalui `available_quantity`
- jika stok cukup, sistem membuat `InventoryReservation` berstatus `active`
- `InventoryItem.reserved_quantity` naik sebesar quantity order item
- `InventoryMovement` bertipe `reservation` dibuat sebagai audit log
- status order berubah dari `pending` menjadi `awaiting_payment`

Jika stok tidak cukup:

- order tidak disimpan
- reservation tidak dibuat
- movement reservation tidak dibuat
- transaksi rollback

### 2. Order dibatalkan / payment failed → release reservation

Saat order dibatalkan atau payment berubah menjadi `failed`:

- reservation aktif milik order diubah menjadi `released`
- `InventoryItem.reserved_quantity` turun
- `InventoryMovement` bertipe `release` dibuat
- status order menjadi `cancelled`

Release hanya mengembalikan stok yang sebelumnya ditahan. Release tidak mengubah `on_hand_quantity` karena barang belum keluar dari gudang.

### 3. Payment paid → order paid, stok fisik belum berkurang

Saat payment berubah menjadi `paid`:

- `Payment.paid_at` diisi bila belum ada
- status order menjadi `paid`
- reservation tetap aktif
- `reserved_quantity` tetap menahan stok untuk order tersebut
- `on_hand_quantity` tidak berkurang
- movement `deduction` tidak dibuat

Keputusan ini memisahkan event “uang berhasil dibayar” dari event “barang benar-benar keluar gudang”.

### 4. Fulfillment / shipping → commit reservation dan deduct stock

Saat order di-fulfill melalui fulfillment workflow:

- reservation aktif milik order diubah menjadi `committed`
- `InventoryItem.reserved_quantity` turun
- `InventoryItem.on_hand_quantity` turun
- `InventoryMovement` bertipe `deduction` dibuat
- status order menjadi `fulfilled`

Ini adalah titik resmi ketika stok fisik dianggap keluar dari gudang.

### 5. Refund vs return

Refund dan return dipisahkan:

- `PaymentStatus.refunded` hanya berarti uang dikembalikan
- refund tidak otomatis menambah stok
- stok hanya bertambah jika barang benar-benar diterima kembali dan layak direstock
- return/restock dilakukan lewat aksi receive stock dengan referensi domain yang jelas, misalnya `reference_type = return`

Dengan aturan ini, refund tanpa barang kembali tidak membuat stok menjadi fiktif.

### 6. Arti field quantity

`on_hand_quantity`

- jumlah stok fisik/logis yang dimiliki toko
- bertambah saat receive stock / return received
- berkurang saat fulfillment/shipping commit

`reserved_quantity`

- bagian dari `on_hand_quantity` yang sedang ditahan untuk order aktif
- bertambah saat reservation dibuat
- berkurang saat reservation release atau commit

`available_quantity`

- stok yang masih bisa dijual
- dihitung dari:

```text
available_quantity = on_hand_quantity - reserved_quantity
```

Contoh:

```text
on_hand_quantity = 10
reserved_quantity = 3
available_quantity = 7
```

Artinya toko punya 10 unit, 3 unit sedang ditahan untuk order, dan 7 unit masih bisa dijual.
