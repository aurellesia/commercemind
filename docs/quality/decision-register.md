# CommerceMind Decision Register

## Purpose and Use

Register ini mencatat pertanyaan yang memerlukan pilihan bermakna tentang arah produk, aturan bisnis, arsitektur, keamanan, AI, integrasi, atau operasi. Dokumen ini melengkapi docs/product/features-tree.md, docs/quality/flow-register.md, dan docs/quality/risk-register.md; bukan pengganti ketiganya dan bukan bukti bahwa capability telah diimplementasikan.

Semua entri adalah kandidat awal berdasarkan dokumentasi yang tersedia. Status Open berarti keputusan belum ditetapkan. Kolom Decision, Rationale, dan Decision Date sengaja belum diisi. Opsi dan rekomendasi bukan persetujuan. Product Owner/pemilik proyek menentukan keputusan produk; owner teknis atau operasional perlu dilibatkan sesuai area.

## Summary

| Category | Open | Total |
|---|---:|---:|
| Product | 2 | 2 |
| Business Rules | 5 | 5 |
| Security & Authorization | 3 | 3 |
| Architecture | 1 | 1 |
| AI Governance / Data Management | 3 | 3 |
| Integration | 1 | 1 |
| Operations | 1 | 1 |
| **Total** | **16** | **16** |

Seluruh 16 kandidat berstatus Open; belum ada keputusan final yang tercatat.

## Candidate Decisions

### CM-DEC-001 — Commit the Initial Product Scope

| Field | Detail |
|---|---|
| Decision ID | CM-DEC-001 |
| Decision Title | Commit the Initial Product Scope |
| Category | Product |
| Context | Arah yang telah dikonfirmasi dalam diskusi pemilik proyek: visi CommerceMind adalah Business Operations & Intelligence Partner for UMKM dengan dua pillar, Business Operations Platform dan AI Business Partner. Tujuan strategisnya mencakup portfolio project untuk menunjukkan engineering capability dan mendukung tujuan memperoleh klien Upwork, sekaligus membangun fondasi yang kredibel bagi kemungkinan SaaS jangka panjang. Target awal adalah UMKM mikro dan UMKM dengan tim di industri online retail. Pada scope awal CommerceMind berperan sebagai primary business management system; arah jangka panjang dapat berkembang menjadi Hybrid Business Management & Intelligence Hub yang mengelola workflow terpilih dan terintegrasi dengan external tools. Order intake awal dilakukan manual; external channel integrations menjadi kemampuan mendatang, dengan arah centralized order management. Batas operasi awal berfokus pada Product Management, Inventory Management, Customer Management, Sales & Order Management, Payment Recording, dan Fulfillment Management. Procurement, supplier management, dan advanced financial management belum termasuk scope awal yang ditetapkan. |
| Decision Question | Apa daftar MVP yang tepat dan pemetaan Feature ID-nya di dalam arah yang telah dikonfirmasi, termasuk kemampuan awal AI Business Partner, reporting dasar, aturan order, CSV import, prioritas, dan urutan pengembangan? |
| Options | Tentukan subset capability dan Feature ID untuk MVP melalui analisis lanjutan; atau tetapkan tahap awal bertahap dengan daftar capability/Feature ID yang disetujui per tahap. Daftar dan batas tiap alternatif belum ditetapkan. |
| Recommendation | Belum diberikan; perlu analisis MVP dan keputusan eksplisit pemilik proyek. |
| Decision Owner | Product Owner / pemilik proyek |
| Status | Open |
| Decision |  |
| Rationale |  |
| Related Feature IDs | CM-BO-007, CM-BO-011, CM-BO-012, CM-BO-015, CM-BO-018, CM-BO-022, CM-BO-023, CM-BO-030, CM-AI-001–CM-AI-017 |
| Related Flow IDs | CM-PF-002, CM-PF-003, CM-PF-004, CM-PF-005, CM-PF-006, CM-PF-007, CM-PF-010, CM-PF-011, CM-PF-012 |
| Related Risk IDs | CM-RK-008 |
| Decision Date |  |
| Notes | Arah diskusi di Context adalah arah produk yang dikonfirmasi, bukan persetujuan daftar MVP atau keputusan final atas seluruh scope. Hal yang masih terbuka: daftar MVP dan Feature ID mapping; capability AI awal; apakah business reporting dasar termasuk MVP; detail order lifecycle/business rules; cakupan CSV import; integrasi/provider spesifik; prioritas dan urutan implementasi. Fitur/flow yang dirujuk bukan bukti telah diimplementasikan atau disetujui. Customer self-service journey tetap pertanyaan terpisah; CM-RK-008 relevan bila journey tersebut masuk scope. |

### CM-DEC-002 — Define Business Workspace and Brand Isolation

| Field | Detail |
|---|---|
| Decision ID | CM-DEC-002 |
| Decision Title | Define Business Workspace and Brand Isolation |
| Category | Security & Authorization |
| Context | Dokumentasi menyebut brand sebagai konteks tenant/workspace pada sebagian implementasi, tetapi cakupan brand pada route belum konsisten. Hubungan workspace dan brand belum didefinisikan tuntas. |
| Decision Question | Apa batas tenant kanonis, bagaimana hubungan workspace dengan brand, dan apakah setiap operasi bisnis wajib membawa konteks tenant tervalidasi? |
| Options | Brand menjadi tenant boundary; workspace menjadi boundary dan brand entitas di dalamnya; atau model lain yang ditentukan domain. |
| Recommendation | Belum diberikan; definisi domain dan dukungan multi-brand perlu dikonfirmasi. |
| Decision Owner | Product Owner bersama Technical Lead / Security Owner |
| Status | Open |
| Decision |  |
| Rationale |  |
| Related Feature IDs | CM-BO-001, CM-BO-004, CM-BO-006, CM-CP-007 |
| Related Flow IDs | CM-PF-014, CM-PF-017, CM-AF-044, CM-AF-051 |
| Related Risk IDs | CM-RK-002, CM-RK-013 |
| Decision Date |  |
| Notes | Risiko lintas brand tercatat, tetapi sumber tidak menetapkan model data atau mekanisme isolasi. |

### CM-DEC-003 — Define Authentication and Authorization Boundaries

| Field | Detail |
|---|---|
| Decision ID | CM-DEC-003 |
| Decision Title | Define Authentication and Authorization Boundaries |
| Category | Security & Authorization |
| Context | Risk Register mencatat autentikasi menyeluruh tidak ditemukan pada route bisnis yang diperiksa. Guard berbasis role tidak membuktikan identitas akun/token tervalidasi. Permission matrix internal juga belum final. |
| Decision Question | Bagaimana identitas, session/token, business roles, platform roles, dan otorisasi tiap aksi dibedakan serta ditegakkan? |
| Options | Identity provider eksternal; autentikasi aplikasi; atau pendekatan lain. Provider dan detail belum ditentukan sumber. |
| Recommendation | Belum diberikan; perlu dipilih sesuai kebutuhan produk dan deployment. |
| Decision Owner | Product Owner bersama Technical Lead / Security Owner |
| Status | Open |
| Decision |  |
| Rationale |  |
| Related Feature IDs | CM-BO-006, CM-PA-003, CM-CP-006 |
| Related Flow IDs | CM-PF-016, CM-PF-018, CM-AF-049, CM-AF-052 |
| Related Risk IDs | CM-RK-001, CM-RK-016 |
| Decision Date |  |
| Notes | Selaraskan dengan CM-DEC-002; role platform_operator bukan permission matrix lengkap. |

### CM-DEC-004 — Set the Customer Purchase Journey Scope

| Field | Detail |
|---|---|
| Decision ID | CM-DEC-004 |
| Decision Title | Set the Customer Purchase Journey Scope |
| Category | Product |
| Context | Storefront catalog ditemukan, tetapi cart, public checkout, customer login/account, payment gateway, shipping workflow, dan public tracking tidak ditemukan atau belum terkonfirmasi sebagai journey end-to-end. |
| Decision Question | Apakah customer harus dapat membeli mandiri dari katalog sampai fulfillment/tracking, atau storefront hanya menyediakan katalog sementara order ditangani staff? |
| Options | Katalog saja; katalog dengan inquiry/manual order; atau self-service purchase journey. Rincian tahap belum ditetapkan. |
| Recommendation | Belum diberikan; model penjualan dan tanggung jawab storefront perlu dikonfirmasi. |
| Decision Owner | Product Owner / pemilik proyek |
| Status | Open |
| Decision |  |
| Rationale |  |
| Related Feature IDs | CM-BO-017, CM-BO-020, CM-BO-021, CM-BO-023, CM-BO-027, CM-BO-030, CM-BO-031 |
| Related Flow IDs | CM-PF-026, CM-AF-070, CM-AF-071, CM-AF-072, CM-AF-073 |
| Related Risk IDs | CM-RK-008, CM-RK-018 |
| Decision Date |  |
| Notes | Flow Register menyatakan customer journey Blocked; order CRUD internal tidak membuktikan public checkout. |

### CM-DEC-005 — Define Order Request Idempotency

| Field | Detail |
|---|---|
| Decision ID | CM-DEC-005 |
| Decision Title | Define Order Request Idempotency |
| Category | Business Rules |
| Context | Risk Register mengidentifikasi kemungkinan duplicate order ketika request diulang setelah timeout; kebijakan idempotency belum ditetapkan. |
| Decision Question | Bagaimana sistem mengenali retry dari intent order yang sama dan berapa lama kunci idempotency berlaku? |
| Options | Client-supplied key; deduplication berbasis business/session key; atau tidak melakukan deduplication dan mengandalkan proses manual. Retention dan payload mismatch belum ditetapkan. |
| Recommendation | Belum diberikan; kebutuhan bergantung pada channel order dan pola retry. |
| Decision Owner | Product Owner bersama Technical Lead |
| Status | Open |
| Decision |  |
| Rationale |  |
| Related Feature IDs | CM-BO-018, CM-BO-019, CM-BO-021 |
| Related Flow IDs | CM-PF-005, CM-PF-026, CM-AF-020 |
| Related Risk IDs | CM-RK-005 |
| Decision Date |  |
| Notes | Kebutuhan public checkout bergantung CM-DEC-004; kebijakan order internal dapat dinilai tersendiri. |

### CM-DEC-006 — Define Order States and Transitions

| Field | Detail |
|---|---|
| Decision ID | CM-DEC-006 |
| Decision Title | Define Order States and Transitions |
| Category | Business Rules |
| Context | Risk Register mencatat request pembuatan order dapat membawa status enum selain pending; status awal yang boleh dipilih dan transisi sah belum jelas. |
| Decision Question | Status apa yang boleh dibuat langsung, transisi apa yang sah, dan actor/service mana yang berwenang? |
| Options | Caller hanya membuat status awal tertentu; status ditentukan server dari proses/channel; atau lifecycle lain yang dirinci. |
| Recommendation | Belum diberikan; selaraskan lifecycle dengan payment, cancellation, dan fulfillment yang masuk scope. |
| Decision Owner | Product Owner / Business Operations Owner bersama Technical Lead |
| Status | Open |
| Decision |  |
| Rationale |  |
| Related Feature IDs | CM-BO-018, CM-BO-019, CM-BO-023, CM-BO-030 |
| Related Flow IDs | CM-PF-005, CM-PF-006, CM-PF-007, CM-AF-020, CM-AF-021, CM-AF-022 |
| Related Risk IDs | CM-RK-006 |
| Decision Date |  |
| Notes | Selaraskan dengan CM-DEC-007 dan CM-DEC-008. |

### CM-DEC-007 — Set Inventory Reservation Timing and Release Rules

| Field | Detail |
|---|---|
| Decision ID | CM-DEC-007 |
| Decision Title | Set Inventory Reservation Timing and Release Rules |
| Category | Business Rules |
| Context | Order creation berhubungan dengan inventory reservation pada kode yang ditinjau, tetapi perilaku concurrency/rollback PostgreSQL dan kebijakan masa berlaku reservation belum diverifikasi atau ditetapkan. |
| Decision Question | Kapan stok di-reserve, kapan reservation dikonfirmasi/dilepas, dan bagaimana expiry/cancellation ditangani? |
| Options | Reserve saat order dibuat; reserve setelah konfirmasi/pembayaran; atau aturan berbeda menurut channel. |
| Recommendation | Belum diberikan; bergantung pada journey, payment timing, dan fulfillment. |
| Decision Owner | Business Operations Owner bersama Technical Lead |
| Status | Open |
| Decision |  |
| Rationale |  |
| Related Feature IDs | CM-BO-011, CM-BO-018, CM-BO-019, CM-BO-030 |
| Related Flow IDs | CM-PF-003, CM-PF-005, CM-PF-006, CM-AF-012, CM-AF-020, CM-AF-028 |
| Related Risk IDs | CM-RK-003 |
| Decision Date |  |
| Notes | Kebijakan proses bisnis berbeda dari verifikasi teknis atomicity/concurrency yang dirujuk CM-DEC-016. |

### CM-DEC-008 — Define Payment Completion and Amount Policy

| Field | Detail |
|---|---|
| Decision ID | CM-DEC-008 |
| Decision Title | Define Payment Completion and Amount Policy |
| Category | Business Rules / Financial |
| Context | Risk Register mencatat amount payment berasal dari request dan lifecycle yang diperiksa tidak membandingkannya dengan total order. Apakah partial payment diperbolehkan belum diketahui. |
| Decision Question | Apakah pembayaran parsial diperbolehkan, bagaimana status paid ditetapkan, dan bagaimana amount/currency direkonsiliasi dengan order? |
| Options | Pembayaran penuh saja; partial payment dengan outstanding balance; atau aturan berbeda per metode/channel. |
| Recommendation | Belum diberikan; aturan finansial perlu disepakati sebelum payment workflow diandalkan. |
| Decision Owner | Product Owner bersama Business/Finance Owner |
| Status | Open |
| Decision |  |
| Rationale |  |
| Related Feature IDs | CM-BO-018, CM-BO-023, CM-BO-024, CM-BO-025, CM-CP-008 |
| Related Flow IDs | CM-PF-006, CM-PF-007, CM-PF-026, CM-AF-022, CM-AF-071 |
| Related Risk IDs | CM-RK-004, CM-RK-018 |
| Decision Date |  |
| Notes | Hubungan gateway eksternal berlaku bila integrasi tersebut dipilih melalui CM-DEC-015. |

### CM-DEC-009 — Define Pricing Context and Precedence

| Field | Detail |
|---|---|
| Decision ID | CM-DEC-009 |
| Decision Title | Define Pricing Context and Precedence |
| Category | Business Rules |
| Context | Risk Register mencatat query price quote yang ditinjau belum memfilter seluruh konteks channel/region/currency/periode. Belum diketahui konteks mana yang wajib menurut aturan bisnis. |
| Decision Question | Konteks apa yang menentukan harga efektif dan bagaimana prioritas dipilih bila beberapa price set/item cocok? |
| Options | Satu harga aktif per produk; precedence berdasarkan konteks; atau aturan lain yang ditentukan bisnis. |
| Recommendation | Belum diberikan; konfirmasi kompleksitas pricing yang dibutuhkan. |
| Decision Owner | Business Operations / Pricing Owner |
| Status | Open |
| Decision |  |
| Rationale |  |
| Related Feature IDs | CM-BO-010, CM-BO-019, CM-BO-027 |
| Related Flow IDs | CM-PF-002, CM-PF-005, CM-PF-026, CM-AF-008, CM-AF-020, CM-AF-026 |
| Related Risk IDs | CM-RK-007 |
| Decision Date |  |
| Notes | Ini kebutuhan klarifikasi, bukan bukti harga yang ada telah salah. |

### CM-DEC-010 — Set Evidence and Data Freshness Rules for AI

| Field | Detail |
|---|---|
| Decision ID | CM-DEC-010 |
| Decision Title | Set Evidence and Data Freshness Rules for AI |
| Category | AI Governance |
| Context | Target-state menekankan evidence-based intelligence, tetapi standar evidence, freshness, provenance, confidence, dan penanganan data kurang belum dirinci. AI Business Partner belum ditemukan pada implementasi yang didiscovery. |
| Decision Question | Evidence, kualitas/freshness data, provenance, uncertainty, dan batas output minimum apa yang wajib sebelum AI menyajikan insight/rekomendasi? |
| Options | Batasi output pada data terstruktur tervalidasi; izinkan data dengan peringatan freshness/uncertainty; atau tunda tipe insight yang sumbernya belum memadai. |
| Recommendation | Belum diberikan; kriteria perlu ditentukan bersama owner data dan product owner. |
| Decision Owner | Product Owner bersama Business/Data Owner dan AI Technical Lead |
| Status | Open |
| Decision |  |
| Rationale |  |
| Related Feature IDs | CM-AI-001, CM-AI-005, CM-AI-006, CM-AI-007, CM-AI-008, CM-AI-009, CM-CP-001, CM-CP-002 |
| Related Flow IDs | CM-PF-010, CM-PF-011, CM-PF-027, CM-AF-035, CM-AF-037, CM-AF-038, CM-AF-074 |
| Related Risk IDs | CM-RK-012, CM-RK-013 |
| Decision Date |  |
| Notes | Bergantung pada tenant isolation CM-DEC-002. Sumber belum menetapkan threshold atau metode evaluasi. |

### CM-DEC-011 — Define Human Approval for AI Actions

| Field | Detail |
|---|---|
| Decision ID | CM-DEC-011 |
| Decision Title | Define Human Approval for AI Actions |
| Category | AI Governance |
| Context | Flow CM-PF-012 menggambarkan human-approved action assistance, tetapi batas tindakan berdampak dan approval policy masih TBD. Risk Register menyebutnya concern target-state, bukan kontrol runtime yang tersedia. |
| Decision Question | Tindakan AI apa yang hanya boleh disarankan, disiapkan sebagai draft, atau dieksekusi setelah approval? Siapa approver yang berwenang? |
| Options | AI hanya memberi saran; AI menyiapkan draft tetapi manusia mengeksekusi; atau AI mengeksekusi subset setelah approval eksplisit. |
| Recommendation | Belum diberikan; klasifikasi tindakan dan approval authority perlu disepakati. |
| Decision Owner | Product Owner / Business Owner bersama AI Governance/Security Owner |
| Status | Open |
| Decision |  |
| Rationale |  |
| Related Feature IDs | CM-AI-009, CM-AI-015, CM-AI-017, CM-BO-036, CM-CP-010 |
| Related Flow IDs | CM-PF-012, CM-PF-028, CM-AF-040, CM-AF-076 |
| Related Risk IDs | CM-RK-014 |
| Decision Date |  |
| Notes | Human-in-the-loop adalah prinsip, belum policy lengkap. Selaraskan dengan authorization CM-DEC-003 dan evidence CM-DEC-010. |

### CM-DEC-012 — Set AI Data Use and Provider Constraints

| Field | Detail |
|---|---|
| Decision ID | CM-DEC-012 |
| Decision Title | Set AI Data Use and Provider Constraints |
| Category | AI Governance / Data Management |
| Context | Provider/model AI, data yang dikirim, retention, usage limits, dan costing belum menjadi keputusan final. Flow konteks AI menandai sumber/izin penggunaan dan retention sebagai TBD. |
| Decision Question | Data bisnis apa yang boleh diproses, apakah data dapat keluar dari sistem, serta aturan retention, logging, provider, dan biaya apa yang berlaku? |
| Options | Provider eksternal dengan pembatasan data; model yang dikelola sendiri; atau tunda pemrosesan AI atas data sensitif. |
| Recommendation | Belum diberikan; nilai privasi, biaya, kualitas, dan deployment sebelum memilih provider. |
| Decision Owner | Product Owner bersama Security/Data Owner dan Technical Lead |
| Status | Open |
| Decision |  |
| Rationale |  |
| Related Feature IDs | CM-AI-001, CM-AI-002, CM-PA-009, CM-CP-006, CM-CP-010 |
| Related Flow IDs | CM-PF-014, CM-PF-021, CM-AF-035, CM-AF-045, CM-AF-060, CM-AF-061 |
| Related Risk IDs | CM-RK-013, CM-RK-015 |
| Decision Date |  |
| Notes | AI provider belum terkonfirmasi pada Discovery; entri ini bukan klaim bahwa data telah dikirim ke provider. |

### CM-DEC-013 — Define Internal Platform Roles and Data Inspection Limits

| Field | Detail |
|---|---|
| Decision ID | CM-DEC-013 |
| Decision Title | Define Internal Platform Roles and Data Inspection Limits |
| Category | Security & Authorization |
| Context | Features Tree membedakan Platform Owner, Platform Administrator, Customer Support, dan Technical Operator, tetapi model role masih awal dan permission detail TBD. |
| Decision Question | Permission apa yang dimiliki tiap role, kapan akses ke data workspace/customer diizinkan, dan apakah aksi sensitif memerlukan approval tambahan? |
| Options | Permission berbasis role; akses berbasis tugas/case dan terbatas waktu; atau kombinasi. Rincian belum ditetapkan. |
| Recommendation | Belum diberikan; tentukan kebutuhan tugas internal sebelum permission dirinci. |
| Decision Owner | Platform Owner bersama Security/Operations Owner |
| Status | Open |
| Decision |  |
| Rationale |  |
| Related Feature IDs | CM-PA-003, CM-PA-004, CM-PA-005, CM-PA-010, CM-PA-011, CM-CP-006, CM-CP-008 |
| Related Flow IDs | CM-PF-016, CM-PF-017, CM-PF-018, CM-PF-022, CM-PF-024, CM-AF-049, CM-AF-053, CM-AF-066 |
| Related Risk IDs | CM-RK-016 |
| Decision Date |  |
| Notes | Selaraskan dengan identity dan tenant boundaries pada CM-DEC-002 dan CM-DEC-003. |

### CM-DEC-014 — Decide Platform Admin Console Deployment Boundary

| Field | Detail |
|---|---|
| Decision ID | CM-DEC-014 |
| Decision Title | Decide Platform Admin Console Deployment Boundary |
| Category | Architecture |
| Context | Architecture Notes menyebut aplikasi modular monolith. Features Tree menyatakan Platform Admin Console memiliki access boundary berbeda dari Business Workspace, tetapi codebase/deployment terpisah belum diputuskan. |
| Decision Question | Apakah platform administration berada di aplikasi/deployment yang sama dengan access control terpisah, frontend terpisah dengan backend bersama, atau deployment terpisah? |
| Options | Satu modular monolith; frontend terpisah dengan backend bersama; atau deployment/backend terpisah. |
| Recommendation | Belum diberikan; pertimbangkan threat model, skala tim, dan kebutuhan operasi. |
| Decision Owner | Technical Lead bersama Platform Owner |
| Status | Open |
| Decision |  |
| Rationale |  |
| Related Feature IDs | CM-PA-001, CM-PA-003, CM-CP-006 |
| Related Flow IDs | CM-PF-015, CM-PF-016, CM-PF-024 |
| Related Risk IDs | CM-RK-016 |
| Decision Date |  |
| Notes | Kebutuhan access boundary dinyatakan; pemisahan codebase/deployment bukan keputusan. |

### CM-DEC-015 — Select External Integration Scope and Failure Policy

| Field | Detail |
|---|---|
| Decision ID | CM-DEC-015 |
| Decision Title | Select External Integration Scope and Failure Policy |
| Category | Integration |
| Context | Flow Register menyebut provider/channel, credentials, sync, notification, dan kegagalan sebagai TBD. Discovery tidak mengonfirmasi payment gateway atau shipping integration. |
| Decision Question | Integrasi mana yang masuk committed scope, provider/channel apa yang didukung, dan bagaimana pending, retry, reconciliation, serta provider failure ditangani? |
| Options | Tidak ada integrasi pada scope awal; provider tertentu per domain; atau abstraction untuk beberapa provider. Provider belum ditentukan sumber. |
| Recommendation | Belum diberikan; pilih provider setelah kebutuhan purchase/fulfillment dan wilayah bisnis dikonfirmasi. |
| Decision Owner | Product Owner bersama Integration/Technical Lead dan Business Operations Owner |
| Status | Open |
| Decision |  |
| Rationale |  |
| Related Feature IDs | CM-BO-024, CM-BO-028, CM-BO-031, CM-BO-034, CM-CP-003, CM-CP-004, CM-CP-009 |
| Related Flow IDs | CM-PF-013, CM-PF-023, CM-PF-026, CM-AF-042, CM-AF-043, CM-AF-065, CM-AF-071 |
| Related Risk IDs | CM-RK-018 |
| Decision Date |  |
| Notes | Terkait dengan CM-DEC-004 dan CM-DEC-008. Flow Register tidak mengasumsikan provider telah terintegrasi. |

### CM-DEC-016 — Establish Recovery Objectives and Database Verification Target

| Field | Detail |
|---|---|
| Decision ID | CM-DEC-016 |
| Decision Title | Establish Recovery Objectives and Database Verification Target |
| Category | Operations / Architecture |
| Context | Risk Register menyatakan backup/restoration belum diketahui dan testing terdokumentasi memakai SQLite in-memory, sedangkan aplikasi menggunakan PostgreSQL. Flow backup menyebut retention/recovery objectives TBD. |
| Decision Question | Recovery objectives apa yang dibutuhkan, bagaimana backup/restore diverifikasi, dan database apa yang wajib menjadi compatibility test target sebelum rilis? |
| Options | Tetapkan target pemulihan dan uji restore berkala; tentukan target bertahap menurut environment; atau nyatakan target tidak diperlukan untuk demo lokal tanpa data persisten. PostgreSQL testing dapat diwajibkan sebelum deployment yang menggunakannya. |
| Recommendation | Belum diberikan; kebutuhan bergantung pada apakah sistem menangani data bisnis nyata atau hanya demo. |
| Decision Owner | Platform Owner bersama Technical Operator / Technical Lead |
| Status | Open |
| Decision |  |
| Rationale |  |
| Related Feature IDs | CM-PA-008, CM-PA-013, CM-CP-009 |
| Related Flow IDs | CM-PF-020, CM-PF-025, CM-AF-058, CM-AF-067, CM-AF-068, CM-AF-069 |
| Related Risk IDs | CM-RK-003, CM-RK-017, CM-RK-019, CM-RK-020 |
| Decision Date |  |
| Notes | Ini pertanyaan target/standar verifikasi, bukan klaim backup saat ini gagal. |

## Dependencies

| Decision | Depends on | Reason |
|---|---|---|
| CM-DEC-003 | CM-DEC-002 | Authorization harus memakai definisi tenant/workspace konsisten. |
| CM-DEC-004 | CM-DEC-001 | Journey harus masuk committed scope sebelum detailnya ditetapkan. |
| CM-DEC-005 | CM-DEC-004 | Channel dan cara request dibuat memengaruhi kebutuhan idempotency. |
| CM-DEC-006 | CM-DEC-004, CM-DEC-008 | Lifecycle berkaitan dengan channel order dan payment. |
| CM-DEC-007 | CM-DEC-004, CM-DEC-006, CM-DEC-008 | Reservation berkaitan dengan checkout, lifecycle, dan payment timing. |
| CM-DEC-009 | CM-DEC-004 | Konteks harga storefront bergantung pada channel yang dipilih. |
| CM-DEC-010 | CM-DEC-002 | AI context harus mempertahankan tenant scope. |
| CM-DEC-011 | CM-DEC-003, CM-DEC-010 | Approval membutuhkan authorization dan evidence yang memadai. |
| CM-DEC-012 | CM-DEC-010 | Batas data/provider mengikuti data yang akan digunakan AI. |
| CM-DEC-014 | CM-DEC-003, CM-DEC-013 | Deployment boundary tidak menggantikan identity dan permission. |
| CM-DEC-015 | CM-DEC-004, CM-DEC-008 | Integrasi payment/shipping bergantung pada journey dan payment policy. |

Dependencies adalah analisis urutan, bukan constraint yang telah disetujui.

## Decisions to Prioritize Before Implementation

1. **CM-DEC-001 — Product scope:** cegah target-state Under Review diperlakukan sebagai komitmen.
2. **CM-DEC-002 dan CM-DEC-003 — Tenant boundary and access control:** berdampak pada pemisahan data dan seluruh route bisnis.
3. **CM-DEC-004 — Customer journey:** tetapkan apakah self-service purchase termasuk scope sebelum membangun cart, checkout, payment, atau shipping.
4. **CM-DEC-006 sampai CM-DEC-008 — Order, inventory, payment rules:** ketidakjelasan status, reservation, dan nominal berdampak pada konsistensi transaksi/data finansial.
5. **CM-DEC-013 — Internal permissions:** tetapkan batas akses operator sebelum menyediakan administrative workflow sensitif.
6. **CM-DEC-010 sampai CM-DEC-012 — AI evidence, approval, and data use:** putuskan sebelum AI memakai data bisnis atau menyiapkan tindakan; AI Business Partner belum ditemukan pada implementasi yang didiscovery.

Keputusan policy tidak menggantikan runtime verification PostgreSQL, transaction/concurrency, backup, dan restore yang tercakup pada CM-DEC-016.

## Decisions That Can Be Deferred

Selama capability terkait belum menjadi committed scope dan tidak digunakan pada operasi nyata, keputusan berikut dapat ditunda:

- Detail provider/model AI, costing, usage limits, dan failover pada CM-DEC-012.
- Provider/channel notifikasi, shipping, dan strategi multi-provider pada CM-DEC-015.
- Pemisahan deployment Platform Admin Console pada CM-DEC-014, selama akses internal tetap dibatasi dan belum ada kebutuhan deployment yang mengharuskan pemisahan.
- Recovery objectives rinci pada CM-DEC-016 untuk demo lokal tanpa data bisnis persisten; tetapkan sebelum menangani data nyata.
- Pricing context lanjutan pada CM-DEC-009 jika belum menjadi scope tahap awal.

Penundaan bukan berarti keputusan selesai atau risiko diterima; catat pemicu untuk membahasnya kembali sebelum capability dikerjakan.

## Source Ambiguities and Notes

- Features Tree adalah target-state map; semua feature tercatat Under Review. Pencantuman tidak dianggap komitmen produk.
- Flow Register menyatakan pemetaan feature bukan bukti implementasi atau pengujian; sejumlah precondition, outcome, dan policy masih TBD/Not Defined.
- CM-PF-026 dan AI flows CM-PF-027/CM-PF-028 berstatus Blocked dalam Flow Register; status tersebut bukan keputusan bahwa semuanya harus dibangun.
- Risk Register membedakan Confirmed Finding, Documented Concern, Potential Risk, dan Requires Investigation. Risiko potensial bukan insiden/defect yang sudah terjadi.
- Sumber belum menentukan apakah brand adalah tenant boundary atau berada di dalam workspace.
- Opsi ditulis sebagai alternatif untuk dibahas; area yang belum didukung sumber dinyatakan belum ditentukan, bukan diisi asumsi.

## Change Management

- Gunakan ID berikutnya dalam format CM-DEC-NNN dan jangan gunakan ulang ID.
- Setelah owner berwenang memutuskan, isi Decision, Rationale, Decision Date, dan Notes; ubah status menjadi Decided hanya setelah persetujuan eksplisit.
- Jika ditunda atau diganti, gunakan Deferred atau Superseded dan rujuk keputusan pengganti bila ada.
- Perubahan pada Features Tree, Flow Register, atau Risk Register harus dilakukan secara terpisah; register ini tidak mengubahnya dengan sendirinya.
