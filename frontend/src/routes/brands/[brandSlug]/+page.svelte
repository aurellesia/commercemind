<script lang="ts">
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { ArrowRight, Leaf, Loader2, PackageX } from 'lucide-svelte';
	import {
		getPublicStorefrontConfig,
		type PublicStorefrontConfig
	} from '$lib/api/storefront-config';
	import {
		isPubliclyVisibleProduct,
		productImageAlt,
		stockLabel,
		storefrontPrice,
		storefrontProductsApi,
		type StorefrontProduct
	} from '$lib/storefront';

	let config = $state<PublicStorefrontConfig | null>(null);
	let featuredProducts = $state<StorefrontProduct[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	const brandSlug = $derived(page.params.brandSlug ?? 'default');

	async function loadHome() {
		loading = true;
		error = null;
		try {
			config = await getPublicStorefrontConfig(brandSlug);
			if (!config.storefront_enabled || !config.public_catalog_enabled) {
				featuredProducts = [];
				return;
			}
			const products = await storefrontProductsApi.catalog(
				0,
				config.featured_product_limit || 3,
				false,
				config.brand_id
			);
			const visibleProducts = config.show_out_of_stock_products
				? products
				: products.filter((product) => product.is_purchasable);
			featuredProducts = visibleProducts
				.filter(isPubliclyVisibleProduct)
				.slice(0, config.featured_product_limit);
		} catch (e) {
			error = 'Storefront belum bisa dimuat. Coba lagi beberapa saat lagi.';
		} finally {
			loading = false;
		}
	}

	onMount(loadHome);
</script>

<svelte:head>
	<title>{config?.default_title ?? config?.brand_name ?? brandSlug}</title>
	<meta name="description" content={config?.default_description ?? config?.tagline ?? ''} />
	<meta property="og:title" content={config?.default_title ?? config?.brand_name ?? brandSlug} />
	<meta property="og:description" content={config?.default_description ?? config?.tagline ?? ''} />
	{#if config?.social_image_url}
		<meta property="og:image" content={config.social_image_url} />
	{/if}
</svelte:head>

<section class="hero">
	<div>
		<p class="eyebrow"><Leaf size={16} /> {config?.brand_name ?? brandSlug}</p>
		<h1>{config?.homepage_headline ?? 'Katalog produk dengan stok dan harga yang jelas.'}</h1>
		<p>{config?.homepage_description ?? config?.tagline ?? 'Lihat produk dan ketersediaan stok.'}</p>
		<a class="primary-link" href={`/brands/${brandSlug}/products`}>
			Lihat Produk
			<ArrowRight size={18} />
		</a>
	</div>
</section>

<section class="featured" aria-label="Produk pilihan">
	<div class="section-heading">
		<h2>Produk pilihan</h2>
		<a href={`/brands/${brandSlug}/products`}>Semua Produk</a>
	</div>

	{#if loading}
		<div class="state-row"><Loader2 size={21} class="spin" /> Memuat produk...</div>
	{:else if error}
		<div class="state-row state-row--error"><PackageX size={21} /> {error}</div>
	{:else if config && !config.public_catalog_enabled}
		<div class="state-row">Katalog produk brand ini sedang belum dibuka untuk publik.</div>
	{:else if featuredProducts.length === 0}
		<div class="state-row">Produk aktif belum tersedia.</div>
	{:else}
		<div class="featured-grid">
			{#each featuredProducts as product}
				<a class="product-tile" href={`/brands/${brandSlug}/products/${product.slug}`}>
					<div class="tile-image">
						{#if product.primary_image}
							<img src={product.primary_image.image_url} alt={productImageAlt(product.primary_image, product.name)} />
						{:else}
							<div class="image-placeholder"><Leaf size={30} /></div>
						{/if}
					</div>
					<div class="tile-copy">
						<span>{stockLabel(product)}</span>
						<h3>{product.name}</h3>
						<strong>{storefrontPrice(product)}</strong>
					</div>
				</a>
			{/each}
		</div>
	{/if}
</section>

<style>
	.hero {
		display: grid;
		align-items: center;
		min-height: 44vh;
	}
	.eyebrow {
		display: inline-flex;
		align-items: center;
		gap: 0.45rem;
		color: #557467;
		font-size: 0.8rem;
		font-weight: 800;
		text-transform: uppercase;
	}
	h1 {
		max-width: 760px;
		margin: 0.75rem 0;
		color: #17211e;
		font-size: clamp(2.35rem, 7vw, 4.8rem);
		line-height: 1;
	}
	.hero p {
		max-width: 42rem;
		color: #56645e;
		line-height: 1.7;
	}
	.primary-link {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		margin-top: 1rem;
		border-radius: 8px;
		background: #1f3c33;
		color: white;
		padding: 0.75rem 1rem;
		font-weight: 900;
		text-decoration: none;
	}
	.featured {
		border-top: 1px solid #e3dccd;
		padding-top: 2rem;
	}
	.section-heading {
		display: flex;
		align-items: end;
		justify-content: space-between;
		margin-bottom: 1rem;
	}
	.section-heading h2 {
		color: #17211e;
		font-size: 2rem;
		font-weight: 900;
	}
	.section-heading a {
		color: #1f3c33;
		font-weight: 900;
		text-decoration: none;
	}
	.featured-grid {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 1rem;
	}
	.product-tile {
		overflow: hidden;
		border: 1px solid #dfd7c8;
		border-radius: 8px;
		background: #fffdf8;
		color: inherit;
		text-decoration: none;
	}
	.tile-image {
		aspect-ratio: 4 / 3;
		background: #e8eddf;
	}
	.tile-image img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}
	.image-placeholder,
	.state-row {
		display: flex;
		align-items: center;
		justify-content: center;
	}
	.image-placeholder {
		height: 100%;
		color: #65735f;
	}
	.tile-copy {
		display: grid;
		gap: 0.45rem;
		padding: 1rem;
	}
	.tile-copy h3 {
		color: #17211e;
		font-weight: 900;
	}
	.state-row {
		min-height: 10rem;
		border: 1px dashed #d7cfbd;
		border-radius: 8px;
		color: #66746c;
		gap: 0.65rem;
	}
	.state-row--error {
		color: #9f3b2f;
	}
	.state-row :global(.spin) {
		animation: spin 1s linear infinite;
	}
	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
	@media (max-width: 820px) {
		.featured-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
