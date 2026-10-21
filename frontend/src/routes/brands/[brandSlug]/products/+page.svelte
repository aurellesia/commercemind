<script lang="ts">
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { ArrowRight, Leaf, Loader2, PackageX, Search } from 'lucide-svelte';
	import {
		availabilityBadgeLabel,
		friendlyStorefrontError,
		isPubliclyVisibleProduct,
		productImageAlt,
		stockLabel,
		storefrontPrice,
		storefrontProductsApi,
		type StorefrontProduct
	} from '$lib/storefront';
	import {
		getPublicStorefrontConfig,
		type PublicStorefrontConfig
	} from '$lib/api/storefront-config';

	let products = $state<StorefrontProduct[]>([]);
	let config = $state<PublicStorefrontConfig | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let searchQuery = $state('');
	const brandSlug = $derived(page.params.brandSlug ?? 'default');

	const filteredProducts = $derived(
		products
			.filter(isPubliclyVisibleProduct)
			.filter((product) => {
				const query = searchQuery.trim().toLowerCase();
				return (
					!query ||
					product.name.toLowerCase().includes(query) ||
					(product.description ?? '').toLowerCase().includes(query) ||
					(product.sku ?? '').toLowerCase().includes(query)
				);
			})
	);

	async function loadCatalog() {
		loading = true;
		error = null;
		try {
			config = await getPublicStorefrontConfig(brandSlug);
			if (!config.storefront_enabled) {
				products = [];
				error = 'Storefront brand ini sedang belum tersedia.';
				return;
			}
			if (!config.public_catalog_enabled) {
				products = [];
				error = 'Katalog publik brand ini sedang tidak tersedia.';
				return;
			}
			const catalog = await storefrontProductsApi.catalog(0, 100, false, config.brand_id);
			products = config.show_out_of_stock_products
				? catalog
				: catalog.filter((product) => product.is_purchasable);
		} catch (e) {
			error = friendlyStorefrontError(e, 'Katalog belum bisa dimuat.');
		} finally {
			loading = false;
		}
	}

	onMount(loadCatalog);
</script>

<svelte:head>
	<title>{config?.default_title ? `${config.default_title} | Produk` : 'Katalog Produk'}</title>
	<meta name="description" content={config?.default_description ?? config?.tagline ?? ''} />
</svelte:head>

<section class="hero">
	<div>
		<p class="eyebrow">{config?.brand_name ?? 'Katalog produk'}</p>
		<h1>{config?.public_catalog_enabled === false ? 'Katalog sedang ditutup sementara.' : 'Produk aktif dengan harga dan stok yang siap dicek.'}</h1>
	</div>
	<div class="search-card">
		<Search size={18} />
		<input bind:value={searchQuery} placeholder="Cari produk atau SKU..." aria-label="Cari produk" />
	</div>
</section>

{#if loading}
	<div class="state-card"><Loader2 size={22} class="spin" /> Memuat katalog...</div>
{:else if error}
	<div class="state-card state-card--error"><PackageX size={22} /> {error}</div>
{:else if filteredProducts.length === 0}
	<div class="state-card"><PackageX size={22} /> Produk aktif tidak ditemukan.</div>
{:else}
	<section class="product-grid" aria-label="Katalog produk">
		{#each filteredProducts as product}
			<a class="product-card" href={`/brands/${brandSlug}/products/${product.slug}`}>
				<div class="image-wrap">
					{#if product.primary_image}
						<img src={product.primary_image.image_url} alt={productImageAlt(product.primary_image, product.name)} />
					{:else}
						<div class="image-placeholder"><Leaf size={34} /></div>
					{/if}
					<span class:muted={!product.is_purchasable}>{availabilityBadgeLabel(product)}</span>
				</div>
				<div class="product-body">
					{#if config?.show_sku}
						<p class="sku">{product.sku ?? product.slug}</p>
					{/if}
					<h2>{product.name}</h2>
					<p class="description">{product.description ?? 'Detail produk sedang dilengkapi.'}</p>
					<div class="product-footer">
						<div>
							<strong>{storefrontPrice(product)}</strong>
							<small>{stockLabel(product)}</small>
						</div>
						<span class="detail-cta">Lihat Detail <ArrowRight size={16} /></span>
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
	.eyebrow {
		color: #65735f;
		font-size: 0.78rem;
		font-weight: 900;
		text-transform: uppercase;
	}
	h1 {
		max-width: 48rem;
		margin: 0.75rem 0;
		color: #17211e;
		font-size: clamp(2.3rem, 6vw, 4.8rem);
		line-height: 0.98;
	}
	.search-card {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		border: 1px solid #d9d3c4;
		border-radius: 999px;
		background: #fffdf6;
		padding: 0.9rem 1rem;
	}
	.search-card input {
		width: 100%;
		border: 0;
		background: transparent;
		outline: none;
	}
	.product-grid {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 1.25rem;
	}
	.product-card {
		display: flex;
		overflow: hidden;
		border: 1px solid #e1dac9;
		border-radius: 8px;
		background: #fffdf8;
		color: inherit;
		flex-direction: column;
		text-decoration: none;
	}
	.image-wrap {
		position: relative;
		aspect-ratio: 4 / 3;
		background: #e6ecdf;
	}
	.image-wrap img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}
	.image-placeholder,
	.state-card {
		display: flex;
		align-items: center;
		justify-content: center;
	}
	.image-placeholder {
		height: 100%;
		color: #65735f;
	}
	.image-wrap span {
		position: absolute;
		left: 1rem;
		top: 1rem;
		border-radius: 999px;
		background: #173f2f;
		color: white;
		padding: 0.4rem 0.7rem;
		font-size: 0.75rem;
		font-weight: 900;
	}
	.image-wrap span.muted {
		background: #f7ead0;
		color: #765d24;
	}
	.product-body {
		display: flex;
		min-height: 14rem;
		flex: 1;
		flex-direction: column;
		gap: 0.75rem;
		padding: 1.15rem;
	}
	.sku {
		overflow: hidden;
		color: #7b806f;
		font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
		font-size: 0.75rem;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	h2 {
		color: #17211e;
		font-size: 1.28rem;
		font-weight: 900;
	}
	.description {
		color: #657064;
		line-height: 1.55;
	}
	.product-footer {
		display: flex;
		align-items: end;
		justify-content: space-between;
		gap: 1rem;
		margin-top: auto;
	}
	.detail-cta {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		color: #1f3c33;
		font-size: 0.85rem;
		font-weight: 900;
		white-space: nowrap;
	}
	.state-card {
		min-height: 16rem;
		gap: 0.75rem;
		border: 1px dashed #cfc8b8;
		border-radius: 8px;
		background: #fffdf8;
		color: #687163;
		padding: 1rem;
	}
	.state-card--error {
		color: #9f3b2f;
	}
	.state-card :global(.spin) {
		animation: spin 1s linear infinite;
	}
	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
	@media (max-width: 900px) {
		.hero,
		.product-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
