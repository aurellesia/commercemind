# TASK 6.1 — Order Creation Flow

## 1. Flow Overview

Endpoint `POST /orders/` menerima `schemas.OrderCreate`, memeriksa customer dengan kombinasi `customer_id` dan `brand_id`, lalu memanggil `crud.create_order`. CRUD membangun order dan item dari data produk di database, menghitung total server-side, meminta reservasi stok untuk seluruh item, menetapkan status `awaiting_payment` jika status awal `pending`, lalu melakukan commit.

**Batas verifikasi:** laporan ini berasal dari pembacaan kode dan test yang tersedia. Tidak ada endpoint atau database yang dijalankan pada investigasi ini.

## 2. Files and Functions Involved

| Location | Function/Symbol | Role |
|---|---|---|
| `backend/api/orders.py:10-24` | `router`, `create_order` | Mendefinisikan `POST /orders/`, memeriksa customer sesuai brand, memetakan exception CRUD menjadi HTTP error. |
| `backend/schema_models/order.py:30-36` | `OrderItemCreate` | Input item: `product_id`, `quantity`; `unit_price` dan `subtotal` opsional untuk kompatibilitas. |
| `backend/schema_models/order.py:59-68` | `OrderBase`, `OrderCreate` | Input order: `brand_id`, `customer_id`, `status`, `total_amount`, dan daftar `items`. |
| `backend/crud/customers.py:9-13` | `get_customer` | Mencari customer berdasar ID, dengan filter `brand_id` bila diberikan. |
| `backend/crud/orders.py:47-77` | `create_order` | Membuat order/item, menjumlah subtotal, mereservasi inventory, dan menangani commit/rollback. |
| `backend/crud/orders.py:167-198` | `_build_order_item` | Memastikan produk berada pada brand order, mengambil harga, memeriksa status/stok, dan menyusun snapshot item. |
| `backend/crud/orders.py:201-215` | `_get_order_price_quote` | Memilih price set aktif berprioritas tertinggi, atau menggunakan `base_price`. |
| `backend/crud/inventory_service.py:185-258` | `reserve_stock_for_order` | Memeriksa stok seluruh item, menaikkan reservasi, mencatat movement, dan flush/commit atau rollback. |
| `backend/crud/products.py:146-197`, `280-308` | `build_product_availability`, `_get_effective_price`, `_not_purchasable_reason` | Mengambil inventory/harga efektif dan membentuk data availability yang digunakan saat item dibangun. |
| `backend/models/orders.py:8-62` | `Order`, `OrderItem` | Kolom, foreign key, constraint, dan relasi ORM order/item. |
| `backend/models/inventory.py:8-70` | `InventoryItem`, `InventoryReservation` | Stok on-hand/reserved, constraint, serta data reservasi. |
| `backend/database.py:14-19` | `get_db` | Membuat session per dependency dan menutup session setelah request; tidak melakukan commit otomatis. |

## 3. Execution Sequence

1. FastAPI menerima `POST /orders/` dengan body `OrderCreate`; schema memvalidasi tipe dan batas field. `brand_id` default `1` dan minimal `1`, `customer_id` minimal `1`, status berupa `OrderStatus`, quantity minimal `1`, dan nilai uang non-negatif (`backend/schema_models/order.py:11-21`, `59-68`; `backend/schema_models/common.py:10-18`). `items` memiliki default daftar kosong.
2. `api.orders.create_order` memanggil `crud.get_customer(customer_id, brand_id)`. Customer tidak ditemukan pada brand tersebut menghasilkan HTTP 404 `Customer not found` (`backend/api/orders.py:14-17`; `backend/crud/customers.py:9-13`).
3. Endpoint memanggil `crud.create_order`. CRUD membuat objek `Order` dengan `brand_id` dan `customer_id` dari request, status request, dan `total_amount=0.00`; nilai total dari request tidak dipakai (`backend/crud/orders.py:47-54`).
4. Untuk setiap item, `_build_order_item` mengambil produk yang ID-nya cocok dan `Product.brand_id == order.brand_id`; jika tidak ada, melempar `InventoryProductNotFoundError` (`backend/crud/orders.py:56-59`, `167-175`).
5. `_get_order_price_quote` memilih `PriceSetItem` yang item dan parent `PriceSet`-nya aktif, dengan urutan `priority DESC`, lalu ID turun. Bila tidak ada, memakai `product.base_price` (`backend/crud/orders.py:201-215`). Harga yang dikirim client tidak digunakan; schema sendiri menyebutnya kompatibilitas (`backend/schema_models/order.py:30-36`).
6. CRUD membangun availability, lalu menolak produk yang statusnya bukan `active`, quantity yang melampaui `available_quantity`, atau harga yang `None` (`backend/crud/orders.py:176-184`).
7. Subtotal dihitung server-side sebagai `price * quantity`; item menyimpan harga, subtotal, harga pokok/nama/SKU/slug sebagai snapshot, serta `price_source` (`backend/crud/orders.py:186-198`). `total_amount` order adalah penjumlahan subtotal setiap item (`backend/crud/orders.py:56-60`).
8. CRUD menambahkan order, melakukan flush agar ID order/item tersedia, lalu menjalankan `reserve_stock_for_order(..., commit=False)` (`backend/crud/orders.py:61-68`). Inventory service membuat reservasi aktif per item dan movement `reservation` (`backend/crud/inventory_service.py:212-247`).
9. Bila status awal tepat `pending`, CRUD menggantinya menjadi `awaiting_payment`. Status awal lain yang lolos schema dibiarkan seperti dikirim (`backend/crud/orders.py:69-70`).
10. CRUD commit, refresh order, dan mengembalikannya; FastAPI menyajikan response schema `Order` dengan HTTP 201 (`backend/crud/orders.py:72-74`; `backend/api/orders.py:13-14`).

## 4. Database Operations and Transaction Boundaries

- Satu `Session` dari dependency `get_db` diteruskan dari endpoint ke CRUD. `get_db` menutup session pada akhir request dan tidak meng-commit otomatis (`backend/database.py:14-19`).
- Pada jalur sukses, pembuatan order, flush order/item, perubahan jumlah reserved, baris `InventoryReservation`, dan `InventoryMovement` berada pada transaksi session yang sama. Inventory helper dipanggil dengan `commit=False`, sehingga helper melakukan `flush`, sementara `create_order` melakukan commit akhir (`backend/crud/orders.py:61-73`; `backend/crud/inventory_service.py:249-255`).
- `create_order` menangkap `Exception`, memanggil `db.rollback()`, kemudian melempar ulang (`backend/crud/orders.py:75-77`). `reserve_stock_for_order` juga menangkap exception dan rollback sebelum melempar ulang (`backend/crud/inventory_service.py:256-258`). Dengan alur session yang sama, kegagalan saat reservasi membatalkan perubahan order/item dan reservasi yang belum di-commit.
- `reserve_stock_for_order` iterasi semua item dan baru flush ketika seluruh item berhasil bila `commit=False` (`backend/crud/inventory_service.py:212-255`). Jika item berikutnya gagal, helper melakukan rollback atas transaksi session, termasuk perubahan yang sudah dilakukan untuk item sebelumnya pada pemanggilan tersebut.
- Untuk setiap produk, service mengambil `InventoryItem` dengan `with_for_update()` sebelum memeriksa available stock dan mengubah reserved quantity (`backend/crud/inventory_service.py:214-224`, `462-483`). Efektivitas locking di database yang digunakan tidak diuji dalam tugas ini; terutama perilaku SQLite versus PostgreSQL **Perlu Verifikasi Runtime**.
- Jika order tidak memiliki item, reservation helper melempar `InvalidInventoryOperationError("order has no items to reserve")`; transaksi kemudian rollback. Endpoint menangkapnya sebagai `InventoryServiceError` umum dan memetakan ke HTTP 400 (`backend/crud/inventory_service.py:193-198`; `backend/api/orders.py:19-22`, `105-110`).

## 5. Validation and Error Handling

| Condition | Observed Code Behavior |
|---|---|
| Body/schema tidak valid | Pydantic/FastAPI memvalidasi field. Contoh: ID/quantity minimal 1, uang tidak negatif, status harus enum. Detail HTTP aktual tidak diverifikasi melalui request runtime. |
| Customer tidak ditemukan atau beda brand | Pencarian customer memfilter kedua ID; endpoint mengembalikan 404 sebelum membuat order (`backend/api/orders.py:15-17`; `backend/crud/customers.py:9-13`). |
| Produk tidak ada atau bukan milik brand order | Query produk memfilter `id` dan `brand_id`; kondisi tidak ditemukan melempar `InventoryProductNotFoundError`, yang ditangkap sebagai `InventoryServiceError` dan dipetakan ke 404 (`backend/crud/orders.py:167-175`; `backend/api/orders.py:19-24`, `105-110`). |
| Produk bukan `active` | `_build_order_item` melempar `ProductNotOrderableError`; endpoint memetakannya ke HTTP 400 (`backend/crud/orders.py:179-180`; `backend/api/orders.py:23-24`, `113-114`). |
| Stok kurang saat membentuk item | Perbandingan `available_quantity < quantity` melempar `InsufficientStockError` (`backend/crud/orders.py:181-182`). |
| Inventory row tidak ada | Saat reservasi, `_require_inventory_item_for_update` melempar `InventoryItemNotFoundError`; sebagai `InventoryServiceError` umum dipetakan ke HTTP 400 (`backend/crud/inventory_service.py:474-483`; `backend/api/orders.py:105-110`). Namun bila availability awal bernilai 0, sering kali pemeriksaan stok item lebih dahulu menghasilkan insufficient stock; status response spesifik belum diuji untuk semua variasi. |
| Stok berubah/tidak cukup saat reservasi | Service memeriksa `available_quantity` lagi dan melempar `InsufficientStockError`; helper dan CRUD rollback. Endpoint memetakannya ke HTTP 400 (`backend/crud/inventory_service.py:214-224`, `256-258`; `backend/crud/orders.py:75-77`; `backend/api/orders.py:105-110`). |
| Harga tidak tersedia | `_build_order_item` menolak hanya bila harga quote `None`; exception dipetakan ke HTTP 400 (`backend/crud/orders.py:183-184`; `backend/api/orders.py:113-114`). Model product saat ini mendefinisikan `base_price` non-null, tetapi kondisi price-set spesifik tetap mengikuti query yang disebut di atas. |
| Beberapa item dan satu item gagal | Seluruh item dibangun sebelum order ditambahkan ke session. Untuk kegagalan pada tahap reservasi, rollback mencakup order/item dan reservasi dalam transaksi yang sama. Tidak ditemukan test multi-item yang membuktikan kasus partial failure secara langsung; efek transaksi tersebut adalah pembacaan statis kode. |

Error yang diketahui dipetakan oleh endpoint: customer 404; inventory order/product tidak ditemukan 404; exception inventory lain 400; `ProductOrderingError` 400. Exception database lain tidak ditangkap khusus oleh endpoint ini dan alur response-nya **Belum Diketahui** tanpa pengujian HTTP/runtime.

## 6. Existing Test Coverage

Test berikut memanggil CRUD secara langsung menggunakan SQLite in-memory, bukan `POST /orders/` melalui HTTP. Fixture dan payload ada di `backend/tests/test_inventory_lifecycle.py:22-67`.

| Test | Behavior Actually Tested |
|---|---|
| `test_create_order_with_enough_stock_reserves_inventory` (`backend/tests/test_inventory_lifecycle.py:79-112`) | Order sukses, status `awaiting_payment`, on-hand tetap, reserved naik, available turun, reservasi aktif, total/subtotal, harga dasar, dan snapshot nama/slug. |
| `test_create_order_ignores_client_price_and_uses_price_set` (`backend/tests/test_inventory_lifecycle.py:115-155`) | Harga/subtotal/total client diabaikan; price set aktif menjadi sumber harga dan tercatat sebagai `price_set`. |
| `test_create_order_rejects_non_active_product` (`backend/tests/test_inventory_lifecycle.py:158-170`) | Produk discontinued memunculkan `ProductNotOrderableError`; setelah exception tidak ada order tersimpan. |
| `test_create_order_with_insufficient_stock_rolls_back` (`backend/tests/test_inventory_lifecycle.py:173-197`) | Quantity lebih besar dari stok memunculkan `InsufficientStockError`; order/reservation tidak tersimpan, reserved tetap nol, movement inbound tetap satu. |
| `test_inventory_aggregate_invariant_blocks_invalid_adjustment` (`backend/tests/test_inventory_lifecycle.py:352-373`) | Secara tidak langsung membuat order yang mereservasi stok lalu memastikan adjustment tidak menurunkan on-hand di bawah reserved. Bukan test kegagalan multi-item order. |
| `test_payment_module_flag_blocks_payment_creation` (`backend/tests/test_module_flags.py:86-107`) | Membuat order untuk persiapan test payment; assertion berfokus pada payment yang ditolak saat module flag off, bukan kontrak endpoint order. |
| Test reporting (`backend/tests/test_product_reporting.py:55-66`, `103`) | Membuat order sebagai fixture/domain input untuk laporan; assertion terkait reporting, bukan semua aturan pembuatan order. |

Belum ditemukan test langsung untuk endpoint HTTP order, customer invalid/beda brand pada create endpoint, produk beda brand pada create endpoint, produk tanpa harga, order kosong, beberapa item ketika satu item gagal, duplicate product lines, atau perilaku concurrency. Ketiadaan itu adalah gap bukti test, bukan bukti bahwa fungsi tersebut gagal.

## 7. Potential Failure Scenarios

- **Customer invalid/beda brand:** endpoint berhenti sebelum CRUD dan mengembalikan 404; kode tidak membedakan “ID tidak ada” dari “customer ada di brand lain”. Tidak ada order/inventory mutation yang dipanggil pada jalur tersebut berdasarkan urutan kode.
- **Product beda brand/tidak ditemukan:** product lookup menghasilkan hasil kosong dan melempar exception sebelum item dibuat. Endpoint memetakannya ke 404. Ini mencegah item lintas brand pada jalur endpoint/CRUD tersebut.
- **Product tidak aktif:** penolakan eksplisit sebelum order di-add/flush. CRUD exception handler tetap rollback session.
- **Insufficient stock pada item tunggal:** penolakan eksplisit dan rollback; ini juga dicakup test CRUD.
- **Multi-item, kegagalan saat membangun item:** semua `_build_order_item` dijalankan sebelum `db.add(db_order)`, jadi order belum dimasukkan oleh fungsi ini saat validasi salah satu item melempar. Rollback tetap dipanggil.
- **Multi-item, kegagalan saat reservasi:** order/item sudah di-flush, dan service dapat telah mengubah item/reservasi sebelumnya sebelum item berikutnya gagal. Service menangkap exception dan rollback session sebelum keluar; outer CRUD juga rollback. Secara kode, perubahan dalam transaksi belum di-commit dan dibatalkan. Test multi-item belum membuktikan hasil database untuk skenario ini.
- **Dua baris item untuk product yang sama:** pemeriksaan awal tiap item membaca availability sebelum reservation dilakukan; reservation service kemudian memeriksa stok berurutan setelah perubahan reserved dalam session. Jika gabungan quantity melebihi stok, kode mengarah ke exception dan rollback di reservation. Ini inferensi dari urutan loop, belum diuji langsung.
- **Transaksi gagal pada commit/database constraint:** CRUD rollback dan melempar ulang. Status HTTP final serta apakah seluruh backend driver/database membatalkan transaksi seperti diharapkan **Perlu Verifikasi Runtime** pada database yang dituju.

## 8. Open Questions and Unknowns

- **Status customer lintas brand:** secara eksplisit dicek oleh endpoint melalui query yang memfilter `brand_id`; proteksi ini tidak ada di dalam `crud.create_order` bila CRUD dipanggil langsung. Apakah hanya endpoint ini yang dianggap boundary resmi belum dikonfirmasi.
- **Kepercayaan terhadap `brand_id`:** nilai berasal dari body `OrderCreate`; file endpoint yang ditinjau tidak menunjukkan dependency autentikasi/otorisasi pada route ini. Siapa yang berwenang menentukan brand pada request dan bagaimana middleware/router lain mengatur akses **Belum Diketahui** di cakupan investigasi ini.
- **Makna status awal:** schema menerima seluruh `OrderStatus`, sedangkan create hanya mengganti `pending` ke `awaiting_payment`. Apakah caller memang boleh membuat order langsung berstatus `paid`, `fulfilled`, atau status lain **Belum Diketahui**.
- **Harga price set:** query memilih price set/item aktif dengan priority tertinggi, tetapi tidak memfilter mata uang, tanggal berlaku, channel, atau wilayah (`backend/crud/orders.py:201-215`). Apakah atribut tersebut bagian aturan bisnis yang harus membatasi quote **Belum Diketahui**.
- **Keterkaitan price set:** pemilihan order price menggunakan query yang sama bentuk dasarnya dengan effective price product (`backend/crud/products.py:280-294`), namun tidak ada runtime verification bahwa hasilnya konsisten untuk semua data.
- **Inventory row hilang:** tidak ditemukan kebijakan untuk membuat inventory row otomatis saat order. Service mensyaratkan row ada saat reservasi (`backend/crud/inventory_service.py:474-483`). HTTP/error yang tampak saat item gagal lebih awal karena availability perlu diverifikasi.
- **Multi-item dan locking:** rollback parsial serta penguncian row dapat dijelaskan dari kode, tetapi transaksi multi-item serta konkurensi pada PostgreSQL belum diuji runtime dalam task ini.
- **Order tanpa item:** schema membolehkan daftar kosong secara default, tetapi reservasi menolaknya. Apakah order kosong harus ditolak di schema/API atau selalu menjadi HTTP 400 merupakan perilaku yang ada, bukan aturan bisnis yang terkonfirmasi selain exception tersebut.
- **Pembulatan uang/kuantitas desimal:** field uang memakai `Decimal`, kolom model memakai `Numeric(12,2)`, quantity integer. Kebijakan pembulatan/currency selain fakta tersebut **Belum Diketahui**.
- **Runtime endpoint:** status code, request parsing, response serialization, dan efek transaksi ketika request gagal **Perlu Verifikasi Runtime** melalui test HTTP terisolasi; tidak dilakukan di task ini.

### Summary of Key Questions

| Question | Answer Based on Code |
|---|---|
| Apa yang terjadi saat berhasil? | Order dan snapshot item dibuat, total dihitung dari harga database, stok direservasi dan movement dicatat, status `pending` menjadi `awaiting_payment`, lalu perubahan di-commit. |
| Customer tidak valid? | Endpoint menghasilkan HTTP 404 sebelum membuat order. |
| Produk beda brand? | Tidak ditemukan oleh query product yang memfilter brand; exception inventory product not found dipetakan ke HTTP 404. |
| Produk tidak aktif? | Ditolak dengan `ProductNotOrderableError`; endpoint memetakan ke HTTP 400. |
| Stok tidak cukup? | Ditolak dengan `InsufficientStockError`; transaksi rollback, dan endpoint memetakan ke HTTP 400. |
| Beberapa item, salah satunya gagal? | Kegagalan validasi terjadi sebelum `db.add`; kegagalan reservasi setelah flush memicu rollback dalam shared session. Tidak ditemukan order/reservasi parsial yang di-commit oleh jalur normal ini sebelum final commit. Multi-item failure perlu test/runtime verification untuk memastikan perilaku aktual DB. |
| Apakah reservasi dapat terbentuk sebagian? | Helper dapat memproses item lebih awal sebelum item selanjutnya gagal, tetapi belum ada commit per item saat dipanggil dengan `commit=False`; kode menjalankan rollback. Persistensi partial reservation tidak diharapkan pada transaksi DB yang rollback-nya berlaku, namun perlu verifikasi runtime terutama pada driver/database target. |
| Apa yang dijamin eksplisit kode? | Filter brand untuk customer dan product pada jalur endpoint/CRUD; status product active; harga dan subtotal dihitung server-side; reservasi diminta sebelum commit; exception memicu rollback. Ini klaim perilaku kode statis, bukan jaminan runtime lintas database. |

