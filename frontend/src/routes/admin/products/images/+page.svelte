<script lang="ts">
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import {
		CheckCircle2,
		ImagePlus,
		Images,
		Loader2,
		RefreshCw,
		Search,
		Star,
		Trash2,
		TriangleAlert
	} from 'lucide-svelte';
	import { Badge } from '$lib/components/ui/badge';
	import { Button } from '$lib/components/ui/button';
	import { Card } from '$lib/components/ui/card';
	import { Input } from '$lib/components/ui/input';
	import { productsApi, type Product, type ProductImage } from '$lib/api/products';

	let products = $state<Product[]>([]);
	let selectedProductId = $state<number | null>(null);
	let images = $state<ProductImage[]>([]);
	let loading = $state(true);
	let imagesLoading = $state(false);
	let submitting = $state(false);
	let error = $state<string | null>(null);
	let imageError = $state<string | null>(null);
	let searchQuery = $state('');
	let toast = $state<{ type: 'success' | 'error'; message: string } | null>(null);

	let imageUrl = $state('');
	let imageAltText = $state('');
	let imageSortOrder = $state('0');
	let imageIsPrimary = $state(false);

	const selectedProduct = $derived(
		products.find((product) => product.id === selectedProductId) ?? null
	);

	const filteredProducts = $derived(
		products.filter((product) => {
			const query = searchQuery.trim().toLowerCase();
			return (
				!query ||
				product.name.toLowerCase().includes(query) ||
				product.slug.toLowerCase().includes(query) ||
				(product.sku ?? '').toLowerCase().includes(query)
			);
		})
	);

	function showToast(type: 'success' | 'error', message: string) {
		toast = { type, message };
		setTimeout(() => (toast = null), 3500);
	}

	function emptyToNull(value: string): string | null {
		return value.trim() || null;
	}

	function productIdFromUrl(): number | null {
		const rawProductId = page.url.searchParams.get('product_id');
		if (!rawProductId) return null;
		const parsedProductId = Number(rawProductId);
		return Number.isInteger(parsedProductId) && parsedProductId > 0 ? parsedProductId : null;
	}

	async function loadProducts() {
		loading = true;
		error = null;
		try {
			products = await productsApi.list();
			const requestedProductId = productIdFromUrl();
			const requestedProductExists = products.some((product) => product.id === requestedProductId);
			if (requestedProductExists) {
				selectedProductId = requestedProductId;
			} else if (!selectedProductId && products.length > 0) {
				selectedProductId = products[0].id;
			}
			if (selectedProductId) await loadImages(selectedProductId);
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	async function loadImages(productId: number) {
		imagesLoading = true;
		imageError = null;
		try {
			images = await productsApi.listImages(productId);
		} catch (e) {
			images = [];
			imageError = (e as Error).message;
		} finally {
			imagesLoading = false;
		}
	}

	async function selectProduct(productId: number) {
		selectedProductId = productId;
		imageUrl = '';
		imageAltText = '';
		imageSortOrder = '0';
		imageIsPrimary = false;
		await loadImages(productId);
	}

	async function handleAddImage(e: SubmitEvent) {
		e.preventDefault();
		if (!selectedProduct || !imageUrl.trim()) return;
		submitting = true;
		try {
			await productsApi.addImage(selectedProduct.id, {
				product_id: selectedProduct.id,
				image_url: imageUrl.trim(),
				alt_text: emptyToNull(imageAltText),
				sort_order: imageSortOrder ? parseInt(imageSortOrder, 10) : 0,
				is_primary: imageIsPrimary
			});
			imageUrl = '';
			imageAltText = '';
			imageSortOrder = '0';
			imageIsPrimary = false;
			await loadImages(selectedProduct.id);
			showToast('success', 'Image produk berhasil ditambahkan.');
		} catch (e) {
			showToast('error', (e as Error).message);
		} finally {
			submitting = false;
		}
	}

	async function handleSetPrimaryImage(image: ProductImage) {
		if (!selectedProduct) return;
		submitting = true;
		try {
			await productsApi.setPrimaryImage(selectedProduct.id, image.id);
			await loadImages(selectedProduct.id);
			showToast('success', 'Primary image berhasil diperbarui.');
		} catch (e) {
			showToast('error', (e as Error).message);
		} finally {
			submitting = false;
		}
	}

	async function handleRemoveImage(image: ProductImage) {
		if (!selectedProduct) return;
		submitting = true;
		try {
			await productsApi.removeImage(selectedProduct.id, image.id);
			await loadImages(selectedProduct.id);
			showToast('success', 'Image produk berhasil dihapus.');
		} catch (e) {
			showToast('error', (e as Error).message);
		} finally {
			submitting = false;
		}
	}

	onMount(loadProducts);
</script>

{#if toast}
	<div class="toast toast--{toast.type}" role="alert" aria-live="polite">
		{#if toast.type === 'success'}
			<CheckCircle2 size={18} />
		{:else}
			<TriangleAlert size={18} />
		{/if}
		<span>{toast.message}</span>
	</div>
{/if}

<section class="mb-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
	<div>
		<p class="text-sm font-medium text-slate-500">Products</p>
		<h1 class="mt-1 text-3xl font-bold tracking-tight text-slate-950">Product images</h1>
		<p class="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
			Manage storefront gallery URLs separately from product catalog data, so product editing stays clean.
		</p>
	</div>

	<Button variant="outline" onclick={loadProducts} disabled={loading || imagesLoading}>
		{#if loading || imagesLoading}
			<Loader2 size={16} class="animate-spin" />
		{:else}
			<RefreshCw size={16} />
		{/if}
		Refresh
	</Button>
</section>

<div class="grid gap-6 xl:grid-cols-[22rem_minmax(0,1fr)]">
	<Card class="overflow-hidden">
		<div class="border-b border-slate-200 p-5">
			<h2 class="text-base font-semibold text-slate-950">Select product</h2>
			<p class="mt-1 text-sm text-slate-500">Pilih produk yang gallery-nya mau diedit.</p>
			<div class="relative mt-4">
				<Search class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
				<Input class="pl-9" placeholder="Search product, slug, SKU..." bind:value={searchQuery} />
			</div>
		</div>

		{#if loading}
			<div class="empty-state"><Loader2 size={18} class="animate-spin" /> Memuat products...</div>
		{:else if error}
			<div class="empty-state empty-state--error"><TriangleAlert size={18} /> {error}</div>
		{:else if filteredProducts.length === 0}
			<div class="empty-state">Tidak ada produk yang cocok.</div>
		{:else}
			<div class="product-list">
				{#each filteredProducts as product (product.id)}
					<button
						class:active={product.id === selectedProductId}
						class="product-row"
						type="button"
						onclick={() => selectProduct(product.id)}
					>
						<span>
							<strong>{product.name}</strong>
							<small>/{product.slug}</small>
						</span>
						<Badge variant={product.status === 'active' ? 'success' : 'outline'}>{product.status}</Badge>
					</button>
				{/each}
			</div>
		{/if}
	</Card>

	<Card class="overflow-hidden">
		<div class="border-b border-slate-200 p-5">
			<div class="flex flex-col justify-between gap-3 sm:flex-row sm:items-start">
				<div>
					<h2 class="text-base font-semibold text-slate-950">
						{selectedProduct ? selectedProduct.name : 'No product selected'}
					</h2>
					<p class="mt-1 text-sm text-slate-500">
						{selectedProduct ? `/${selectedProduct.slug}` : 'Select a product to manage images.'}
					</p>
				</div>
				<Badge variant="secondary">{images.length} images</Badge>
			</div>
		</div>

		{#if selectedProduct}
			<form class="image-form" onsubmit={handleAddImage}>
				<div class="field field--wide">
					<label for="image-url">Image URL <span class="required">*</span></label>
					<input id="image-url" type="url" bind:value={imageUrl} placeholder="https://example.com/product.jpg" required />
				</div>
				<div class="field">
					<label for="image-alt">Alt text</label>
					<input id="image-alt" type="text" bind:value={imageAltText} placeholder="Front bottle packshot" />
				</div>
				<div class="field field--small">
					<label for="image-order">Order</label>
					<input id="image-order" type="number" bind:value={imageSortOrder} min="0" step="1" />
				</div>
				<label class="checkbox-field"><input type="checkbox" bind:checked={imageIsPrimary} /> Primary</label>
				<Button type="submit" disabled={submitting || !imageUrl.trim()}>
					{#if submitting}<Loader2 size={16} class="animate-spin" />{:else}<ImagePlus size={16} />{/if}
					Add image
				</Button>
			</form>

			{#if imagesLoading}
				<div class="empty-state"><Loader2 size={18} class="animate-spin" /> Memuat images...</div>
			{:else if imageError}
				<div class="empty-state empty-state--error"><TriangleAlert size={18} /> {imageError}</div>
			{:else if images.length === 0}
				<div class="empty-state"><Images size={20} /> Belum ada image URL untuk produk ini.</div>
			{:else}
				<div class="image-grid">
					{#each images as image (image.id)}
						<article class="image-card">
							<div class="image-preview">
								<img src={image.image_url} alt={image.alt_text ?? selectedProduct.name} />
								{#if image.is_primary}<Badge variant="success">Primary</Badge>{/if}
							</div>
							<div class="image-card-body">
								<p class="font-medium text-slate-950">{image.alt_text ?? 'No alt text'}</p>
								<p class="image-url">{image.image_url}</p>
								<p class="text-xs text-slate-500">Sort order {image.sort_order}</p>
								<div class="flex flex-wrap gap-2 pt-1">
									<Button size="sm" variant={image.is_primary ? 'secondary' : 'outline'} onclick={() => handleSetPrimaryImage(image)} disabled={submitting || image.is_primary}>
										<Star size={14} /> {image.is_primary ? 'Primary' : 'Set primary'}
									</Button>
									<Button size="sm" variant="outline" class="text-red-600 hover:bg-red-50 hover:text-red-700" onclick={() => handleRemoveImage(image)} disabled={submitting}>
										<Trash2 size={14} /> Remove
									</Button>
								</div>
							</div>
						</article>
					{/each}
				</div>
			{/if}
		{:else}
			<div class="empty-state"><Images size={20} /> Pilih produk terlebih dahulu.</div>
		{/if}
	</Card>
</div>

<style>
	.toast {
		position: fixed;
		bottom: 1.5rem;
		right: 1.5rem;
		z-index: 9999;
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.75rem 1.25rem;
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 500;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
	}
	.toast--success { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
	.toast--error { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }

	.empty-state {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		padding: 3rem 1.5rem;
		font-size: 0.875rem;
		color: #64748b;
		text-align: center;
	}
	.empty-state--error { color: #991b1b; }

	.product-list { max-height: 38rem; overflow-y: auto; padding: 0.5rem; }
	.product-row {
		display: flex;
		width: 100%;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		border: 0;
		border-radius: 0.75rem;
		background: transparent;
		padding: 0.875rem;
		text-align: left;
		cursor: pointer;
	}
	.product-row:hover,
	.product-row.active { background: #f1f5f9; }
	.product-row strong { display: block; color: #0f172a; font-size: 0.875rem; }
	.product-row small { display: block; margin-top: 0.25rem; color: #64748b; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }

	.image-form {
		display: grid;
		grid-template-columns: minmax(0, 2fr) minmax(12rem, 1fr) 6rem auto auto;
		gap: 0.75rem;
		align-items: end;
		padding: 1.25rem;
		border-bottom: 1px solid #e2e8f0;
	}
	.field { display: flex; flex-direction: column; gap: 0.375rem; }
	.field label { font-size: 0.8125rem; font-weight: 600; color: #475569; }
	.required { color: #ef4444; }
	.field input {
		width: 100%;
		border: 1px solid #cbd5e1;
		border-radius: 0.5rem;
		padding: 0.55rem 0.75rem;
		font-size: 0.875rem;
		outline: none;
	}
	.checkbox-field { display: flex; align-items: center; gap: 0.375rem; min-height: 2.35rem; font-size: 0.875rem; color: #475569; }

	.image-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; padding: 1.25rem; }
	.image-card { overflow: hidden; border: 1px solid #e2e8f0; border-radius: 0.875rem; background: white; }
	.image-preview { position: relative; height: 14rem; background: #f1f5f9; }
	.image-preview img { width: 100%; height: 100%; object-fit: cover; }
	.image-preview :global(.inline-flex) { position: absolute; top: 0.75rem; left: 0.75rem; }
	.image-card-body { display: flex; flex-direction: column; gap: 0.375rem; padding: 1rem; }
	.image-url { overflow-wrap: anywhere; font-size: 0.75rem; color: #64748b; }

	@media (max-width: 900px) {
		.image-form,
		.image-grid { grid-template-columns: 1fr; }
	}
</style>
