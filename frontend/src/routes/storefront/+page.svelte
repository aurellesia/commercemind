<script lang="ts">
	import { onMount } from 'svelte';
	import { ArrowRight, BadgeCheck, Leaf, Loader2, PackageCheck, ShieldCheck } from 'lucide-svelte';
	import {
		isPubliclyVisibleProduct,
		productImageAlt,
		stockLabel,
		storefrontConfig,
		storefrontPrice,
		storefrontProductsApi,
		type StorefrontProduct
	} from '$lib/storefront';

	let featuredProducts = $state<StorefrontProduct[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	async function loadFeaturedProducts() {
		loading = true;
		error = null;

		try {
			const products = await storefrontProductsApi.catalog(0, 12);
			featuredProducts = products.filter(isPubliclyVisibleProduct).slice(0, 3);
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	onMount(loadFeaturedProducts);
</script>

<svelte:head>
	<title>{storefrontConfig.brandName} | Storefront</title>
	<meta name="description" content={storefrontConfig.defaultDescription} />
	<meta property="og:title" content={`${storefrontConfig.brandName} | Storefront`} />
	<meta property="og:description" content={storefrontConfig.defaultDescription} />
	<meta property="og:type" content="website" />
	<meta property="og:url" content={`${storefrontConfig.siteUrl}/storefront`} />
	<meta name="twitter:card" content="summary" />
</svelte:head>

<section class="hero">
	<div class="hero-copy">
		<p class="eyebrow"><Leaf size={16} /> {storefrontConfig.brandName}</p>
		<h1>Katalog produk dengan stok dan harga yang jelas.</h1>
		<p>
			Gunakan storefront ini sebagai template toko untuk skincare, fashion, aksesoris, atau brand lain. Customer bisa melihat produk, detail penting, harga, dan ketersediaan stok sebelum lanjut ke pembelian.
		</p>
		<a class="primary-link" href="/storefront/products">
			{storefrontConfig.primaryCatalogCta}
			<ArrowRight size={18} />
		</a>
	</div>

	<div class="trust-panel" aria-label="Keunggulan toko">
		<div>
			<PackageCheck size={19} />
			<span>Stok terbaca dari inventory</span>
		</div>
		<div>
			<BadgeCheck size={19} />
			<span>Detail produk siap disesuaikan per brand</span>
		</div>
		<div>
			<ShieldCheck size={19} />
			<span>Harga publik dari server</span>
		</div>
	</div>
</section>

<section class="featured" aria-label="Produk pilihan">
	<div class="section-heading">
		<div>
			<p class="eyebrow">{storefrontConfig.categoryLabel}</p>
			<h2>Mulai dari katalog toko</h2>
		</div>
		<a href="/storefront/products">Semua Produk</a>
	</div>

	{#if loading}
		<div class="state-row"><Loader2 size={21} class="spin" /> Memuat produk...</div>
	{:else if error}
		<div class="state-row state-row--error">Produk belum bisa dimuat. Coba buka katalog beberapa saat lagi.</div>
	{:else if featuredProducts.length === 0}
		<div class="state-row">Produk aktif belum tersedia.</div>
	{:else}
		<div class="featured-grid">
			{#each featuredProducts as product (product.id)}
				<a class="product-tile" href={`/storefront/products/${product.slug}`}>
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
		grid-template-columns: minmax(0, 1.1fr) minmax(18rem, 0.9fr);
		gap: 2rem;
		align-items: center;
		min-height: 58vh;
	}

	.hero-copy {
		display: grid;
		justify-items: start;
		gap: 1rem;
	}

	.eyebrow {
		display: inline-flex;
		align-items: center;
		gap: 0.45rem;
		margin: 0;
		color: #557467;
		font-size: 0.8rem;
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0;
	}

	.hero h1 {
		max-width: 720px;
		margin: 0;
		color: #17211e;
		font-size: clamp(2.35rem, 7vw, 4.8rem);
		line-height: 1;
		letter-spacing: 0;
		overflow-wrap: anywhere;
	}

	.hero-copy > p {
		max-width: 40rem;
		margin: 0;
		color: #56645e;
		font-size: 1.06rem;
		line-height: 1.7;
	}

	.primary-link {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		width: fit-content;
		padding: 12px 18px;
		color: #ffffff;
		font-weight: 800;
		text-decoration: none;
		background: #1f3c33;
		border-radius: 8px;
	}

	.trust-panel {
		display: grid;
		gap: 0.85rem;
		border: 1px solid #ded7c9;
		border-radius: 8px;
		background: #fffdf8;
		padding: 1rem;
		box-shadow: 0 18px 48px rgba(34, 42, 36, 0.08);
	}

	.trust-panel div {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		min-height: 3.4rem;
		border-bottom: 1px solid #eee7d8;
		color: #2f493f;
		font-weight: 800;
	}

	.trust-panel div:last-child {
		border-bottom: 0;
	}

	.featured {
		margin-top: 1.5rem;
		padding-top: 2rem;
		border-top: 1px solid #e3dccd;
	}

	.section-heading {
		display: flex;
		align-items: end;
		justify-content: space-between;
		gap: 1rem;
		margin-bottom: 1rem;
	}

	.section-heading h2 {
		margin: 0.35rem 0 0;
		color: #17211e;
		font-size: clamp(1.7rem, 4vw, 2.6rem);
		line-height: 1.05;
		letter-spacing: 0;
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

	.image-placeholder {
		display: flex;
		height: 100%;
		align-items: center;
		justify-content: center;
		color: #65735f;
	}

	.tile-copy {
		display: grid;
		gap: 0.45rem;
		padding: 1rem;
	}

	.tile-copy span {
		color: #65735f;
		font-size: 0.82rem;
		font-weight: 800;
	}

	.tile-copy h3 {
		margin: 0;
		color: #17211e;
		font-size: 1.05rem;
		line-height: 1.25;
		overflow-wrap: anywhere;
	}

	.tile-copy strong {
		color: #1f3c33;
	}

	.state-row {
		display: flex;
		min-height: 10rem;
		align-items: center;
		justify-content: center;
		gap: 0.65rem;
		border: 1px dashed #d7cfbd;
		border-radius: 8px;
		background: #fffdf8;
		color: #66746c;
		font-weight: 700;
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

	@media (max-width: 960px) {
		.hero {
			grid-template-columns: 1fr;
		}
	}

	@media (max-width: 820px) {
		.featured-grid {
			grid-template-columns: 1fr;
		}

		.section-heading {
			align-items: start;
			flex-direction: column;
		}
	}

	@media (max-width: 560px) {
		.hero {
			min-height: auto;
		}

		.primary-link {
			width: 100%;
			justify-content: center;
		}
	}
</style>
