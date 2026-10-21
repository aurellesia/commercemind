<script lang="ts">
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { ArrowLeft, CreditCard, Leaf, Loader2, PackageX, ShoppingCart, Truck } from 'lucide-svelte';
	import {
		friendlyStorefrontError,
		productImageAlt,
		stockLabel,
		storefrontPrice,
		storefrontProductsApi,
		type StorefrontProductDetail,
		type StorefrontProductImage
	} from '$lib/storefront';
	import {
		getPublicStorefrontConfig,
		type PublicStorefrontConfig
	} from '$lib/api/storefront-config';

	let product = $state<StorefrontProductDetail | null>(null);
	let selectedImage = $state<StorefrontProductImage | null>(null);
	let config = $state<PublicStorefrontConfig | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	const brandSlug = $derived(page.params.brandSlug ?? 'default');

	async function loadProduct() {
		loading = true;
		error = null;
		try {
			config = await getPublicStorefrontConfig(brandSlug);
			if (!config.storefront_enabled || !config.public_catalog_enabled) {
				product = null;
				error = 'Katalog produk brand ini sedang tidak tersedia untuk publik.';
				return;
			}
			product = await storefrontProductsApi.detailBySlug(page.params.slug ?? '', config.brand_id);
			selectedImage = product.primary_image ?? product.images[0] ?? null;
		} catch (e) {
			error = friendlyStorefrontError(e, 'Produk belum bisa dimuat.');
		} finally {
			loading = false;
		}
	}

	onMount(loadProduct);
</script>

<svelte:head>
	<title>{product?.name ? `${product.name} | ${config?.brand_name ?? brandSlug}` : config?.default_title ?? brandSlug}</title>
	<meta name="description" content={product?.description ?? config?.default_description ?? ''} />
	{#if product?.primary_image}
		<meta property="og:image" content={product.primary_image.image_url} />
	{:else if config?.social_image_url}
		<meta property="og:image" content={config.social_image_url} />
	{/if}
</svelte:head>

<a class="back-link" href={`/brands/${brandSlug}/products`}><ArrowLeft size={16} /> Kembali ke produk</a>

{#if loading}
	<div class="state-card"><Loader2 size={22} class="spin" /> Memuat produk...</div>
{:else if error}
	<div class="state-card state-card--error"><PackageX size={22} /> {error}</div>
{:else if product}
	<article class="detail-shell">
		<section class="gallery" aria-label="Galeri produk">
			<div class="hero-image">
				{#if selectedImage}
					<img src={selectedImage.image_url} alt={productImageAlt(selectedImage, product.name)} />
				{:else}
					<div class="image-placeholder"><Leaf size={42} /></div>
				{/if}
			</div>
		</section>

		<section class="product-copy">
			<p class="eyebrow">{config?.show_sku ? product.sku ?? product.slug : config?.brand_name ?? brandSlug}</p>
			<h1>{product.name}</h1>
			<p class="description">{product.description ?? 'Detail produk sedang dilengkapi.'}</p>
			<div class="purchase-card">
				<div>
					<span>Harga</span>
					<strong>{storefrontPrice(product)}</strong>
				</div>
				<div>
					<span>Ketersediaan</span>
					<strong>{stockLabel(product)}</strong>
				</div>
			</div>
			{#if config?.allow_checkout && config.modules.cart_enabled}
				<div class="purchase-actions">
					<a class="checkout-button" href={`/brands/${brandSlug}/cart`}>
						<ShoppingCart size={18} />
						Tambah ke Keranjang
					</a>
					{#if config.modules.payments_enabled}
						<span><CreditCard size={16} /> Pembayaran tersedia</span>
					{/if}
					{#if config.modules.shipping_enabled}
						<span><Truck size={16} /> Pengiriman tersedia</span>
					{/if}
				</div>
			{/if}
		</section>
	</article>
{/if}

<style>
	.back-link {
		display: inline-flex;
		align-items: center;
		gap: 0.45rem;
		margin-bottom: 1.5rem;
		color: #59665e;
		font-weight: 900;
		text-decoration: none;
	}
	.detail-shell {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(20rem, 0.85fr);
		gap: 2rem;
	}
	.hero-image {
		overflow: hidden;
		aspect-ratio: 4 / 5;
		border: 1px solid #e0d8c7;
		border-radius: 8px;
		background: #e6ecdf;
	}
	.hero-image img {
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
		color: #687763;
	}
	.eyebrow {
		color: #65735f;
		font-size: 0.78rem;
		font-weight: 900;
		text-transform: uppercase;
	}
	h1 {
		margin: 0.75rem 0;
		color: #17211e;
		font-size: clamp(2.35rem, 6vw, 4.9rem);
		line-height: 1;
	}
	.description {
		color: #5d665f;
		line-height: 1.75;
	}
	.purchase-card {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.75rem;
		margin: 1.5rem 0;
	}
	.purchase-card div {
		border: 1px solid #dfd7c5;
		border-radius: 8px;
		background: #fffdf8;
		padding: 1rem;
	}
	.purchase-card span {
		display: block;
		color: #7b806f;
		font-size: 0.78rem;
		font-weight: 900;
		text-transform: uppercase;
	}
	.purchase-card strong {
		display: block;
		margin-top: 0.45rem;
		color: #17211e;
	}
	.purchase-actions {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 0.75rem;
	}
	.checkout-button,
	.purchase-actions span {
		display: inline-flex;
		align-items: center;
		gap: 0.45rem;
		border-radius: 8px;
		font-weight: 900;
	}
	.checkout-button {
		background: #1f3c33;
		color: white;
		padding: 0.8rem 1rem;
		text-decoration: none;
	}
	.purchase-actions span {
		border: 1px solid #dfd7c5;
		color: #46534d;
		padding: 0.65rem 0.8rem;
	}
	.state-card {
		min-height: 16rem;
		gap: 0.75rem;
		border: 1px dashed #cfc8b8;
		border-radius: 8px;
		background: #fffdf8;
		color: #687163;
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
		.detail-shell,
		.purchase-card {
			grid-template-columns: 1fr;
		}
	}
</style>
