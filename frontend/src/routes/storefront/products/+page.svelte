<script lang="ts">
	import { onMount } from 'svelte';
	import { ArrowRight, Leaf, Loader2, PackageX, Search, Sparkles } from 'lucide-svelte';
	import {
		availabilityBadgeLabel,
		friendlyStorefrontError,
		isPubliclyVisibleProduct,
		productImageAlt,
		stockLabel,
		storefrontConfig,
		storefrontPrice,
		storefrontProductsApi,
		type StorefrontProduct
	} from '$lib/storefront';

	type AvailabilityFilter = 'all' | 'available' | 'low-stock' | 'out-of-stock';
	type SortMode = 'newest' | 'name-asc' | 'price-asc' | 'price-desc';

	const availabilityFilters: { label: string; value: AvailabilityFilter }[] = [
		{ label: 'Semua', value: 'all' },
		{ label: 'Tersedia', value: 'available' },
		{ label: 'Stok rendah', value: 'low-stock' },
		{ label: 'Habis', value: 'out-of-stock' }
	];

	let products = $state<StorefrontProduct[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let searchQuery = $state('');
	let availabilityFilter = $state<AvailabilityFilter>('all');
	let sortMode = $state<SortMode>('newest');
	let failedImageIds = $state<Set<number>>(new Set());

	const visibleProducts = $derived(products.filter(isPubliclyVisibleProduct));

	const searchedProducts = $derived(
		visibleProducts.filter((product) => {
			const query = searchQuery.trim().toLowerCase();
			return (
				!query ||
				product.name.toLowerCase().includes(query) ||
				(product.description ?? '').toLowerCase().includes(query) ||
				(product.sku ?? '').toLowerCase().includes(query)
			);
		})
	);

	const filteredProducts = $derived(
		searchedProducts.filter((product) => {
			if (availabilityFilter === 'available') return product.is_purchasable;
			if (availabilityFilter === 'low-stock') return product.is_low_stock;
			if (availabilityFilter === 'out-of-stock') {
				return product.status === 'active' && !product.is_purchasable;
			}
			return true;
		})
	);

	const sortedProducts = $derived(
		[...filteredProducts].sort((a, b) => {
			if (sortMode === 'name-asc') return a.name.localeCompare(b.name, 'id-ID');
			if (sortMode === 'price-asc') return priceValue(a) - priceValue(b);
			if (sortMode === 'price-desc') return priceValue(b) - priceValue(a);
			return b.id - a.id;
		})
	);

	const resultSummary = $derived(
		`${sortedProducts.length} dari ${visibleProducts.length} produk aktif`
	);

	const emptyMessage = $derived(getEmptyMessage());

	function priceValue(product: StorefrontProduct): number {
		const raw = product.effective_price ?? product.base_price;
		const value = typeof raw === 'string' ? parseFloat(raw) : raw;
		return Number.isFinite(value) ? value : Number.POSITIVE_INFINITY;
	}

	async function loadCatalog() {
		loading = true;
		error = null;
		try {
			products = await storefrontProductsApi.catalog();
		} catch (e) {
			error = friendlyStorefrontError(e, 'Katalog belum bisa dimuat. Coba lagi beberapa saat lagi.');
		} finally {
			loading = false;
		}
	}

	function getEmptyMessage(): string {
		if (visibleProducts.length === 0) return 'Produk aktif belum tersedia.';
		if (searchQuery.trim()) return 'Produk tidak ditemukan untuk pencarian ini.';
		if (availabilityFilter !== 'all') return 'Tidak ada produk untuk filter ini.';
		return 'Produk aktif tidak ditemukan.';
	}

	function markImageFailed(imageId: number) {
		failedImageIds = new Set([...failedImageIds, imageId]);
	}

	onMount(loadCatalog);
</script>

<svelte:head>
	<title>Produk | {storefrontConfig.brandName}</title>
	<meta
		name="description"
		content={`Lihat katalog produk ${storefrontConfig.brandName} dengan harga, stok, gambar, dan detail produk yang siap dicek.`}
	/>
	<meta property="og:title" content={`Produk | ${storefrontConfig.brandName}`} />
	<meta
		property="og:description"
		content={`Lihat katalog produk ${storefrontConfig.brandName} dengan harga, stok, gambar, dan detail produk yang siap dicek.`}
	/>
	<meta property="og:type" content="website" />
	<meta property="og:url" content={`${storefrontConfig.siteUrl}/storefront/products`} />
	<meta name="twitter:card" content="summary" />
</svelte:head>

<section class="hero">
	<div class="hero-copy">
		<p class="eyebrow"><Sparkles size={16} /> Katalog produk</p>
		<h1>Produk aktif dengan harga dan stok yang siap dicek.</h1>
		<p>
			Jelajahi katalog publik dari brand ini. Setiap produk membaca harga dan ketersediaan dari sistem, jadi tampilan storefront tetap cocok untuk berbagai kategori.
		</p>
	</div>
	<div class="search-card">
		<Search size={18} />
		<input bind:value={searchQuery} placeholder="Cari produk atau SKU..." aria-label="Cari produk" />
	</div>
</section>

<section class="catalog-toolbar" aria-label="Filter dan urutan produk">
	<div class="filter-group" aria-label="Filter ketersediaan">
		{#each availabilityFilters as filter}
			<button
				type="button"
				class:active={availabilityFilter === filter.value}
				onclick={() => (availabilityFilter = filter.value)}
			>
				{filter.label}
			</button>
		{/each}
	</div>

	<div class="sort-group">
		<span>{resultSummary}</span>
		<label>
			Urutan
			<select bind:value={sortMode}>
				<option value="newest">Terbaru</option>
				<option value="name-asc">Nama A-Z</option>
				<option value="price-asc">Harga terendah</option>
				<option value="price-desc">Harga tertinggi</option>
			</select>
		</label>
	</div>
</section>

{#if loading}
	<div class="state-card"><Loader2 size={22} class="spin" /> Memuat katalog...</div>
{:else if error}
	<div class="state-card state-card--error">
		<PackageX size={22} />
		<p>{error}</p>
		<button type="button" onclick={loadCatalog}>Coba Lagi</button>
	</div>
{:else if sortedProducts.length === 0}
	<div class="state-card">
		<PackageX size={22} />
		<p>{emptyMessage}</p>
		<a href="/storefront/products">Lihat semua produk</a>
	</div>
{:else}
	<section class="product-grid" aria-label="Katalog produk">
		{#each sortedProducts as product (product.id)}
			<a class="product-card" href={`/storefront/products/${product.slug}`}>
				<div class="image-wrap">
					{#if product.primary_image && !failedImageIds.has(product.primary_image.id)}
						<img
							src={product.primary_image.image_url}
							alt={productImageAlt(product.primary_image, product.name)}
							onerror={() => product.primary_image && markImageFailed(product.primary_image.id)}
						/>
					{:else}
						<div class="image-placeholder"><Leaf size={34} /></div>
					{/if}
					<span class:muted={!product.is_purchasable}>{availabilityBadgeLabel(product)}</span>
				</div>
				<div class="product-body">
					<p class="sku">{product.sku ?? product.slug}</p>
					<h2>{product.name}</h2>
					<p class="description">{product.description ?? 'Detail produk sedang dilengkapi.'}</p>
					<div class="product-footer">
						<div>
							<strong>{storefrontPrice(product)}</strong>
							<small>{stockLabel(product)}</small>
						</div>
						<span class="detail-cta">
							Lihat Detail
							<ArrowRight size={16} />
						</span>
					</div>
				</div>
			</a>
		{/each}
	</section>
{/if}

<style>
	.hero {
		display: grid;
		grid-template-columns: minmax(0, 1.2fr) minmax(18rem, 0.8fr);
		gap: 2rem;
		align-items: end;
		margin-bottom: 2rem;
	}
	.eyebrow { display: inline-flex; align-items: center; gap: 0.5rem; color: #65735f; font-weight: 800; text-transform: uppercase; letter-spacing: 0; font-size: 0.78rem; }
	.hero h1 { max-width: 48rem; margin: 0.75rem 0; color: #17211e; font-size: clamp(2.3rem, 6vw, 4.8rem); line-height: 0.98; letter-spacing: 0; overflow-wrap: anywhere; }
	.hero p { max-width: 38rem; color: #5d665f; font-size: 1.05rem; line-height: 1.7; }
	.search-card { display: flex; align-items: center; gap: 0.75rem; border: 1px solid #d9d3c4; border-radius: 999px; background: #fffdf6; padding: 0.9rem 1rem; box-shadow: 0 18px 50px rgba(37, 45, 38, 0.08); }
	.search-card input { width: 100%; border: 0; background: transparent; color: #17211e; font-size: 0.95rem; outline: none; }

	.catalog-toolbar { display: flex; align-items: center; justify-content: space-between; gap: 1rem; margin-bottom: 1.25rem; }
	.filter-group { display: flex; flex-wrap: wrap; gap: 0.5rem; }
	.filter-group button { min-height: 2.5rem; border: 1px solid #d8d1c0; border-radius: 999px; background: #fffdf8; color: #46534d; padding: 0 0.9rem; font-weight: 800; cursor: pointer; }
	.filter-group button.active { border-color: #1f3c33; background: #1f3c33; color: #fff; }
	.sort-group { display: flex; align-items: center; gap: 1rem; color: #657064; font-size: 0.9rem; font-weight: 800; }
	.sort-group label { display: flex; align-items: center; gap: 0.55rem; }
	.sort-group select { min-height: 2.5rem; border: 1px solid #d8d1c0; border-radius: 8px; background: #fffdf8; color: #17211e; padding: 0 0.7rem; font-weight: 800; }

	.product-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1.25rem; }
	.product-card { display: flex; min-width: 0; overflow: hidden; border: 1px solid #e1dac9; border-radius: 8px; background: #fffdf8; color: inherit; flex-direction: column; text-decoration: none; box-shadow: 0 18px 45px rgba(36, 42, 35, 0.07); transition: transform 0.18s ease, box-shadow 0.18s ease; }
	.product-card:hover { transform: translateY(-4px); box-shadow: 0 24px 70px rgba(36, 42, 35, 0.12); }
	.image-wrap { position: relative; aspect-ratio: 4 / 3; background: #e6ecdf; }
	.image-wrap img { width: 100%; height: 100%; object-fit: cover; }
	.image-placeholder { display: flex; height: 100%; align-items: center; justify-content: center; color: #65735f; }
	.image-wrap span { position: absolute; left: 1rem; top: 1rem; border-radius: 999px; background: #173f2f; color: #fff; padding: 0.4rem 0.7rem; font-size: 0.75rem; font-weight: 800; }
	.image-wrap span.muted { background: #f7ead0; color: #765d24; }
	.product-body { display: flex; min-height: 14.5rem; flex: 1; flex-direction: column; gap: 0.75rem; padding: 1.15rem; }
	.sku { overflow: hidden; color: #7b806f; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 0.75rem; text-overflow: ellipsis; white-space: nowrap; }
	h2 { color: #17211e; font-size: 1.28rem; line-height: 1.18; overflow-wrap: anywhere; }
	.description { display: -webkit-box; overflow: hidden; color: #657064; line-height: 1.55; line-clamp: 3; -webkit-line-clamp: 3; -webkit-box-orient: vertical; }
	.product-footer { display: flex; align-items: end; justify-content: space-between; gap: 1rem; margin-top: auto; }
	.product-footer strong { display: block; color: #17211e; font-size: 1.1rem; }
	.product-footer small { display: block; margin-top: 0.25rem; color: #6d7469; }
	.detail-cta { display: inline-flex; align-items: center; gap: 0.35rem; color: #1f3c33; font-size: 0.85rem; font-weight: 900; white-space: nowrap; }
	.state-card { display: flex; min-height: 16rem; align-items: center; justify-content: center; gap: 0.75rem; border: 1px dashed #cfc8b8; border-radius: 8px; background: #fffdf8; color: #687163; padding: 1rem; text-align: center; }
	.state-card p { margin: 0; }
	.state-card button,
	.state-card a { border: 1px solid #cbd7c3; border-radius: 8px; background: #fffdf8; color: #1f3c33; padding: 0.65rem 0.85rem; font-weight: 900; text-decoration: none; cursor: pointer; }
	.state-card--error { color: #9f3b2f; }
	.state-card :global(.spin) { animation: spin 1s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }

	@media (max-width: 1100px) {
		.product-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
	}

	@media (max-width: 900px) {
		.hero { grid-template-columns: 1fr; }
		.catalog-toolbar,
		.sort-group { align-items: stretch; flex-direction: column; }
		.sort-group label { justify-content: space-between; }
		.sort-group select { flex: 1; }
	}

	@media (max-width: 640px) {
		.product-grid { grid-template-columns: 1fr; }
		.filter-group button { flex: 1 1 auto; }
		.product-footer { align-items: start; flex-direction: column; }
		.detail-cta { min-height: 2.5rem; }
	}
</style>
