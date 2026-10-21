<script lang="ts">
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import {
		AlertCircle,
		ArrowLeft,
		ArrowRight,
		BadgeCheck,
		Leaf,
		Loader2,
		PackageX,
		ShieldCheck
	} from 'lucide-svelte';
	import {
		friendlyStorefrontError,
		productImageAlt,
		stockLabel,
		storefrontConfig,
		storefrontPrice,
		storefrontProductsApi,
		type StorefrontProductDetail,
		type StorefrontProductImage
	} from '$lib/storefront';

	let product = $state<StorefrontProductDetail | null>(null);
	let selectedImage = $state<StorefrontProductImage | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let failedImageIds = $state<Set<number>>(new Set());

	const pageTitle = $derived(
		product ? `${product.name} | ${storefrontConfig.brandName}` : `Produk | ${storefrontConfig.brandName}`
	);
	const pageDescription = $derived(
		product?.description ??
			`Lihat detail produk, harga, stok, dan informasi katalog di ${storefrontConfig.brandName}.`
	);
	const pageImage = $derived(product?.primary_image?.image_url ?? selectedImage?.image_url ?? null);
	const pageUrl = $derived(
		product
			? `${storefrontConfig.siteUrl}/storefront/products/${product.slug}`
			: `${storefrontConfig.siteUrl}/storefront/products/${page.params.slug ?? ''}`
	);

	async function loadProduct() {
		loading = true;
		error = null;
		try {
			if (!page.params.slug) throw new Error('Product slug is missing.');
			product = await storefrontProductsApi.detailBySlug(page.params.slug);
			selectedImage = product.primary_image ?? product.images[0] ?? null;
		} catch (e) {
			error = friendlyStorefrontError(e, 'Produk belum bisa dimuat. Coba lagi beberapa saat lagi.');
		} finally {
			loading = false;
		}
	}

	function unavailableMessage(item: StorefrontProductDetail): string {
		if (item.is_purchasable) return 'Produk tersedia.';
		return item.not_purchasable_reason ?? 'Produk ini belum tersedia untuk dibeli.';
	}

	function markImageFailed(imageId: number) {
		failedImageIds = new Set([...failedImageIds, imageId]);
	}

	onMount(loadProduct);
</script>

<svelte:head>
	<title>{pageTitle}</title>
	<meta name="description" content={pageDescription} />
	<meta property="og:title" content={pageTitle} />
	<meta property="og:description" content={pageDescription} />
	<meta property="og:type" content="product" />
	<meta property="og:url" content={pageUrl} />
	{#if pageImage}
		<meta property="og:image" content={pageImage} />
	{/if}
	<meta name="twitter:card" content={pageImage ? 'summary_large_image' : 'summary'} />
</svelte:head>

<a class="back-link" href="/storefront/products"><ArrowLeft size={16} /> Kembali ke produk</a>

{#if loading}
	<div class="state-card"><Loader2 size={22} class="spin" /> Memuat produk...</div>
{:else if error}
	<div class="state-card state-card--error">
		<PackageX size={22} />
		<p>{error}</p>
		<div class="state-actions">
			<button type="button" onclick={loadProduct}>Coba Lagi</button>
			<a href="/storefront/products">Kembali ke Produk</a>
		</div>
	</div>
{:else if product}
	<article class="detail-shell">
		<section class="gallery" aria-label="Galeri produk">
			<div class="hero-image">
				{#if selectedImage && !failedImageIds.has(selectedImage.id)}
					<img
						src={selectedImage.image_url}
						alt={productImageAlt(selectedImage, product.name)}
						onerror={() => selectedImage && markImageFailed(selectedImage.id)}
					/>
				{:else}
					<div class="image-placeholder"><Leaf size={42} /></div>
				{/if}
			</div>
			{#if product.images.length > 1}
				<div class="thumbs">
					{#each product.images as image (image.id)}
						<button class:active={selectedImage?.id === image.id} type="button" onclick={() => (selectedImage = image)}>
							{#if failedImageIds.has(image.id)}
								<div class="thumb-placeholder"><Leaf size={18} /></div>
							{:else}
								<img
									src={image.image_url}
									alt={productImageAlt(image, product.name)}
									onerror={() => markImageFailed(image.id)}
								/>
							{/if}
						</button>
					{/each}
				</div>
			{/if}
		</section>

		<section class="product-copy">
			<p class="eyebrow"><BadgeCheck size={16} /> {product.sku ?? product.slug}</p>
			<h1>{product.name}</h1>
			{#if product.net_weight}<p class="net-weight">{product.net_weight}</p>{/if}
			<p class="description">{product.description ?? 'Detail produk sedang dilengkapi.'}</p>

			<div class="purchase-card">
				<div>
					<span>Harga</span>
					<strong>{storefrontPrice(product)}</strong>
				</div>
				<div>
					<span>Ketersediaan</span>
					<strong class:muted={!product.is_purchasable}>{stockLabel(product)}</strong>
				</div>
			</div>

			{#if !product.is_purchasable}
				<div class="availability-note">
					<AlertCircle size={18} />
					<p>{unavailableMessage(product)}</p>
				</div>
			{/if}

			<div class="trust-strip">
				{#if product.bpom_number}
					<div><ShieldCheck size={17} /> Sertifikasi/BPOM {product.bpom_number}</div>
				{/if}
				<div><Leaf size={17} /> Stok terhubung inventory</div>
			</div>

			<a class="secondary-link" href="/storefront/products">
				Lihat Produk Lainnya
				<ArrowRight size={16} />
			</a>
		</section>
	</article>

	<section class="detail-grid" aria-label="Informasi produk">
		<div class="info-card">
			<h2>Panduan produk</h2>
			<p>{product.usage_instructions ?? 'Panduan penggunaan atau perawatan produk akan segera dilengkapi.'}</p>
		</div>
		<div class="info-card">
			<h2>Material / komposisi</h2>
			<p>{product.ingredients ?? 'Informasi material, komposisi, atau bahan produk akan segera dilengkapi.'}</p>
		</div>
		<div class="info-card">
			<h2>Catatan penting</h2>
			<p>{product.warnings ?? 'Tidak ada catatan khusus yang tercatat.'}</p>
		</div>
		<div class="info-card">
			<h2>Penyimpanan / perawatan</h2>
			<p>{product.storage_instructions ?? 'Informasi penyimpanan atau perawatan produk akan segera dilengkapi.'}</p>
		</div>
	</section>
{/if}

<style>
	.back-link { display: inline-flex; align-items: center; gap: 0.45rem; margin-bottom: 1.5rem; color: #59665e; font-weight: 800; text-decoration: none; }
	.detail-shell { display: grid; grid-template-columns: minmax(0, 1fr) minmax(20rem, 0.85fr); gap: 2rem; align-items: start; }
	.gallery { display: flex; flex-direction: column; gap: 1rem; }
	.hero-image { overflow: hidden; aspect-ratio: 4 / 5; border: 1px solid #e0d8c7; border-radius: 8px; background: #e6ecdf; box-shadow: 0 24px 80px rgba(37, 45, 38, 0.12); }
	.hero-image img { width: 100%; height: 100%; object-fit: cover; }
	.image-placeholder { display: flex; height: 100%; min-height: 24rem; align-items: center; justify-content: center; color: #687763; }
	.thumbs { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 0.75rem; }
	.thumbs button { overflow: hidden; height: 5.5rem; border: 2px solid transparent; border-radius: 8px; background: #eee8d8; padding: 0; cursor: pointer; }
	.thumbs button.active { border-color: #173f2f; }
	.thumbs img { width: 100%; height: 100%; object-fit: cover; }
	.thumb-placeholder { display: flex; height: 100%; align-items: center; justify-content: center; color: #687763; }
	.product-copy { position: sticky; top: 6rem; }
	.eyebrow { display: inline-flex; align-items: center; gap: 0.45rem; color: #65735f; font-weight: 900; letter-spacing: 0; text-transform: uppercase; font-size: 0.78rem; }
	h1 { margin: 0.75rem 0; color: #17211e; font-size: clamp(2.35rem, 6vw, 4.9rem); line-height: 1; letter-spacing: 0; overflow-wrap: anywhere; }
	.net-weight { color: #7c6a36; font-weight: 900; }
	.description { margin-top: 1rem; color: #5d665f; font-size: 1.05rem; line-height: 1.75; }
	.purchase-card { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin: 1.5rem 0; }
	.purchase-card div { border: 1px solid #dfd7c5; border-radius: 8px; background: #fffdf8; padding: 1rem; }
	.purchase-card span { display: block; color: #7b806f; font-size: 0.78rem; font-weight: 900; text-transform: uppercase; letter-spacing: 0; }
	.purchase-card strong { display: block; margin-top: 0.45rem; color: #17211e; font-size: 1.15rem; }
	.purchase-card strong.muted { color: #9a5a31; }
	.availability-note { display: flex; align-items: flex-start; gap: 0.65rem; margin: -0.5rem 0 1rem; border: 1px solid #efd8b7; border-radius: 8px; background: #fff8ec; color: #865b22; padding: 0.85rem; }
	.availability-note p { margin: 0; line-height: 1.5; }
	.trust-strip { display: flex; flex-wrap: wrap; gap: 0.75rem; }
	.trust-strip div { display: inline-flex; align-items: center; gap: 0.45rem; border-radius: 999px; background: #e7efdf; color: #2f4f37; padding: 0.55rem 0.8rem; font-size: 0.85rem; font-weight: 800; }
	.secondary-link { display: inline-flex; align-items: center; gap: 0.45rem; margin-top: 1.15rem; border: 1px solid #cbd7c3; border-radius: 8px; color: #1f3c33; padding: 0.75rem 0.9rem; font-weight: 900; text-decoration: none; }
	.detail-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; margin-top: 2rem; }
	.info-card { border: 1px solid #e0d8c7; border-radius: 8px; background: #fffdf8; padding: 1.25rem; }
	.info-card h2 { margin-bottom: 0.6rem; color: #17211e; font-size: 1.1rem; }
	.info-card p { white-space: pre-wrap; color: #5d665f; line-height: 1.7; }
	.state-card { display: flex; min-height: 16rem; align-items: center; justify-content: center; gap: 0.75rem; border: 1px dashed #cfc8b8; border-radius: 8px; background: #fffdf8; color: #687163; padding: 1rem; text-align: center; }
	.state-card p { margin: 0; }
	.state-actions { display: flex; flex-wrap: wrap; justify-content: center; gap: 0.65rem; }
	.state-actions button,
	.state-actions a { border: 1px solid #cbd7c3; border-radius: 8px; background: #fffdf8; color: #1f3c33; padding: 0.65rem 0.85rem; font-weight: 900; text-decoration: none; cursor: pointer; }
	.state-card--error { color: #9f3b2f; }
	.state-card :global(.spin) { animation: spin 1s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }
	@media (max-width: 1100px) {
		.detail-shell { grid-template-columns: minmax(0, 0.95fr) minmax(18rem, 1fr); }
	}

	@media (max-width: 900px) {
		.detail-shell,
		.detail-grid,
		.purchase-card { grid-template-columns: 1fr; }
		.product-copy { position: static; }
		.hero-image { aspect-ratio: 4 / 3; }
		.image-placeholder { min-height: 18rem; }
	}

	@media (max-width: 560px) {
		.thumbs { grid-template-columns: repeat(4, minmax(0, 1fr)); }
		.thumbs button { height: 4.5rem; }
		.secondary-link { justify-content: center; width: 100%; }
	}
</style>
