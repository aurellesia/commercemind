# Backlog Menuju Customer Checkout

Dokumen ini menyimpan urutan fitur yang perlu dikerjakan agar CommerceMind bergerak dari platform console, storefront catalog, dan merchant admin menuju flow **customer bisa checkout**.

## Posisi Saat Ini

- Platform Console sudah multi-brand untuk brand, storefront, modules, system, dan settings.
- Storefront brand-scoped sudah membaca public config, catalog, dan product detail.
- Merchant Admin brand-scoped sudah tersedia untuk products, inventory, orders, dan customers.
- Inventory lifecycle sudah cukup matang:
  - order create reserve stock
  - cancel release reservation
  - payment paid tidak langsung mengurangi stok fisik
  - fulfill baru commit/deduct stock
- Backend orders dan payments sudah ada.

Gap utama:

- Cart belum ada.
- Guest checkout belum siap.
- Customer/address schema belum cocok untuk checkout ringan.
- Storefront belum punya flow order creation.
- Merchant Admin final belum sepenuhnya brand-scoped; beberapa panel lengkap masih berada di legacy `/admin/*`.

## Keputusan Final Admin Multi-Brand

Desain final yang disepakati:

- `/console` adalah multi-brand control plane untuk platform operator.
- `/brands/{brandSlug}/admin` adalah Merchant Admin untuk satu brand tertentu.
- Merchant Admin tidak boleh menjadi dashboard gabungan lintas brand.
- CommerceMind diperlakukan sama seperti brand lain di storefront dan Merchant Admin.
- CommerceMind adalah brand default/demo yang protected/pinned:
  - brand id: `1`
  - brand slug: `default`
  - storefront: `/brands/default`
  - merchant admin: `/brands/default/admin`
  - boleh diedit seperti brand lain
  - tidak boleh dihapus/archive permanen lewat UI/API normal
- `/admin` adalah legacy shortcut sementara yang nantinya redirect ke `/brands/default/admin`.

Target akhirnya:

```text
/console
  Platform operator mengelola semua brand

/brands/default/admin
  Merchant Admin CommerceMind demo/default, dengan perilaku sama seperti brand lain

/brands/{brandSlug}/admin
  Merchant Admin untuk brand client tertentu

/admin
  Redirect/shortcut legacy ke /brands/default/admin
```

## Backlog Admin Multi-Brand Finalization

### 1. Dokumentasikan Role dan Route Boundary

- Catat bahwa hanya Platform Console yang boleh melihat multi-brand.
- Catat bahwa Merchant Admin selalu terikat ke satu brand.
- Catat bahwa CommerceMind/default adalah brand normal yang protected/pinned.
- Catat bahwa legacy `/admin/*` hanya shortcut sementara ke CommerceMind/default selama transisi.
- Pastikan copy UI tidak menyiratkan merchant bisa melihat semua brand.

### 2. Tambahkan Proteksi Default Brand

- Backend harus menolak delete/archive permanen untuk brand id `1` atau slug `default`.
- Platform Console boleh mengubah settings CommerceMind seperti brand lain.
- Platform Console tidak boleh menyediakan tombol delete untuk CommerceMind/default.
- Jika ada endpoint delete/archive brand, tambahkan guard dan test:
  - brand normal bisa di-archive sesuai rule
  - CommerceMind/default ditolak dengan error jelas
  - penghapusan CommerceMind hanya boleh lewat maintenance database manual

### 3. Buat Helper Brand Admin Context

- Buat helper frontend untuk resolve `brandSlug -> brand context`.
- Context minimal berisi:
  - `brand_id`
  - `brand_slug`
  - `brand_name`
  - public config/module flags bila dibutuhkan UI
- Semua halaman `/brands/[brandSlug]/admin/*` memakai helper ini.
- Jika brand tidak ditemukan, tampilkan state error yang jelas.

### 4. Port Products ke Brand-Scoped Admin

- Pindahkan fitur lengkap dari `/admin/products` ke `/brands/[brandSlug]/admin/products`.
- Semua API call products wajib memakai `brand_id` dari brand context.
- Fitur yang harus tetap ada:
  - list products
  - search/filter
  - create product
  - edit product
  - archive/discontinue/reactivate
  - delete product
  - availability summary
  - link manage images
- Setelah selesai, hapus placeholder `Buka legacy CommerceMind products`.

### 5. Port Product Images ke Brand-Scoped Admin

- Tambahkan route:
  - `/brands/[brandSlug]/admin/products/images`
- Product selector hanya menampilkan product milik brand aktif.
- Link image management dari products harus menuju route brand-scoped.
- Legacy `/admin/products/images` menjadi shortcut sementara ke CommerceMind/default selama transisi.

### 6. Port Inventory ke Brand-Scoped Admin

- Pindahkan fitur lengkap dari `/admin/inventory` ke `/brands/[brandSlug]/admin/inventory`.
- API inventory harus bisa menerima dan menghormati `brand_id`.
- Inventory list, movement, dan reservation hanya menampilkan data brand aktif.
- Setelah selesai, hapus placeholder `Buka legacy CommerceMind inventory`.

### 7. Port Orders ke Brand-Scoped Admin

- Pindahkan fitur lengkap dari `/admin/orders` ke `/brands/[brandSlug]/admin/orders`.
- Orders list hanya menampilkan order brand aktif.
- Detail order harus memuat:
  - order items
  - customer snapshot
  - shipping snapshot
  - payment
  - reservation/stock status
- Aksi admin harus brand-safe:
  - cancel order
  - mark payment paid
  - fulfill order
- Setelah selesai, hapus placeholder `Buka legacy CommerceMind orders`.

### 8. Port Customers ke Brand-Scoped Admin

- Pindahkan fitur customers dari `/admin/customers` ke `/brands/[brandSlug]/admin/customers`.
- Customer list hanya menampilkan customer brand aktif.
- Search/filter harus brand-scoped.
- Detail customer nanti memuat:
  - profil customer
  - alamat
  - histori order brand tersebut
- Setelah selesai, hapus placeholder `Buka legacy CommerceMind customers`.

### 9. Port Payments ke Brand-Scoped Admin

- Tambahkan payments ke brand admin nav bila belum ada.
- Route target:
  - `/brands/[brandSlug]/admin/payments`
- Payments list dan update status harus brand-scoped.
- Legacy `/admin/payments` menjadi shortcut sementara ke CommerceMind/default selama transisi.

### 10. Redirect Legacy `/admin/*`

Setelah semua brand-scoped admin panel stabil:

- `/admin` redirect ke `/brands/default/admin`
- `/admin/products` redirect ke `/brands/default/admin/products`
- `/admin/products/images` redirect ke `/brands/default/admin/products/images`
- `/admin/inventory` redirect ke `/brands/default/admin/inventory`
- `/admin/orders` redirect ke `/brands/default/admin/orders`
- `/admin/customers` redirect ke `/brands/default/admin/customers`
- `/admin/payments` redirect ke `/brands/default/admin/payments`

Tujuan redirect adalah menjaga backward compatibility. CommerceMind tetap memakai route brand-scoped yang sama seperti brand lain.

### 11. Verifikasi Isolasi Multi-Brand Admin

Smoke test wajib:

- Brand A punya produk A.
- Brand B punya produk B.
- `/brands/a/admin/products` hanya melihat produk A.
- `/brands/b/admin/products` hanya melihat produk B.
- `/brands/default/admin/products` membuka CommerceMind/default dengan perilaku yang sama seperti brand lain.
- `/admin/products` redirect/shortcut ke `/brands/default/admin/products`.
- Order, customer, inventory, dan payment tidak bocor antar-brand.
- `/console` tetap bisa melihat dan mengelola semua brand.
- CommerceMind/default tidak bisa dihapus/archive permanen lewat UI/API normal.

## Urutan Fitur

### 1. Rapikan Customer Foundation

- Jadikan `email` nullable.
- Jadikan `phone` identitas utama guest customer.
- Tambahkan `customer_type`: `guest` / `registered`.
- Tambahkan `password_hash` nullable untuk upgrade akun nanti.
- Pastikan checkout pertama tidak memaksa customer membuat akun.

### 2. Tambah Customer Address dan Order Snapshot

- Tambahkan tabel `customer_addresses`.
- Tambahkan snapshot customer di `orders`:
  - nama
  - phone
  - email
- Tambahkan snapshot alamat pengiriman di `orders`:
  - recipient name
  - phone
  - address line
  - district
  - city
  - province
  - postal code
  - notes
- Pastikan histori order tidak berubah ketika data customer/address diperbarui.

### 3. Bangun Cart Backend/Frontend

- Untuk MVP, cart boleh disimpan di `localStorage` storefront.
- Item cart minimal:
  - `product_id`
  - `quantity`
  - snapshot display ringan dari catalog
- Server tetap harus melakukan validasi ulang harga, stok, status produk, dan module flags saat checkout.
- Tambahkan route storefront:
  - `/brands/[brandSlug]/cart`

### 4. Buat Guest Checkout Endpoint

- Tambahkan endpoint, misalnya:
  - `POST /storefront/{brand_slug}/checkout`
- Payload:
  - customer name
  - phone
  - email optional
  - shipping address
  - cart/order items
  - payment method
  - shipping method
- Service checkout harus:
  - resolve/create guest customer by phone
  - simpan/resolve address
  - create order
  - reserve stock
  - create pending payment
  - return order dan payment instruction

### 5. Buat Checkout UI Storefront

- Tambahkan route:
  - `/brands/[brandSlug]/checkout`
- UI harus menampilkan:
  - ringkasan cart
  - form nama
  - form nomor WhatsApp
  - form email optional
  - form alamat pengiriman
  - pilihan metode pembayaran
  - pilihan metode pengiriman
- Validasi frontend:
  - nama wajib
  - phone wajib
  - alamat wajib
  - email optional tetapi harus valid bila diisi
- Hormati module/settings flags:
  - `cart_enabled`
  - `allow_checkout`
  - `payments_enabled`
  - `shipping_enabled`
  - `guest_checkout_enabled`

### 6. Buat Checkout Success Page

- Tambahkan route, misalnya:
  - `/brands/[brandSlug]/checkout/success/[orderId]`
- Tampilkan:
  - nomor order
  - status order
  - ringkasan produk
  - subtotal
  - ongkir bila tersedia
  - total bayar
  - instruksi pembayaran
  - alamat pengiriman
  - nomor WhatsApp customer
- Tambahkan tombol:
  - konfirmasi via WhatsApp
  - lanjut belanja
  - lihat pesanan
- MVP payment bisa manual dulu via instruksi dan WhatsApp.

### 7. Rapikan Admin Order Workflow

- Admin orders harus bisa melihat detail lengkap:
  - order items
  - customer snapshot
  - shipping snapshot
  - payment
  - reservation/stock status
- Tambahkan aksi admin:
  - mark payment paid
  - cancel order
  - fulfill order
- Pastikan aksi ini memakai lifecycle inventory yang sudah ada.

### 8. Payment MVP Manual

- Mulai dari payment method:
  - `manual`
  - `bank_transfer`
  - `cash`
- Tambahkan tempat menyimpan instruksi pembayaran publik per brand.
- Jangan masuk payment gateway sebelum flow manual stabil.
- Credential/integrasi payment gateway nanti harus memakai secret storage/encryption, bukan plain text.

### 9. Shipping MVP

- Mulai dari shipping method manual:
  - pickup
  - flat rate
  - manual confirmation
- Jika belum menghitung ongkir otomatis, checkout tetap bisa jalan dengan copy bahwa ongkir dikonfirmasi admin.
- Integrasi kurir/ongkir otomatis dikerjakan setelah checkout manual stabil.

### 10. Order Tracking Customer

- Tambahkan route publik ringan untuk melihat order.
- Opsi MVP:
  - link success page cukup dulu
  - atau lookup by order id/code + phone
- Customer account dan login bisa menjadi fase setelah checkout guest stabil.

## Prioritas MVP Paling Cepat

Jika targetnya adalah customer bisa checkout secepat mungkin, urutan paling tipis adalah:

1. Customer schema guest + phone.
2. Order snapshot alamat/customer.
3. LocalStorage cart.
4. Guest checkout endpoint.
5. Checkout page.
6. Success page + WhatsApp confirmation.
7. Admin order detail + mark paid + fulfill.

## Jangan Dikerjakan Terlalu Awal

- Payment gateway.
- Customer login/account.
- Voucher/promo.
- Ongkir otomatis.
- Customer account dashboard.
- Upload bukti pembayaran.

Fitur-fitur itu penting, tetapi bukan blocker untuk checkout MVP.
