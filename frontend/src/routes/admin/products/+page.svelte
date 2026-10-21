<script lang="ts">
	import { onMount } from 'svelte';
	import {
		Archive,
		Ban,
		Boxes,
		CheckCircle2,
		CircleDollarSign,
		Edit,
		Eye,
		Images,
		Loader2,
		PackageCheck,
		PackagePlus,
		RefreshCw,
		RotateCcw,
		Search,
		Trash2,
		TriangleAlert,
		X
	} from 'lucide-svelte';
	import { Badge } from '$lib/components/ui/badge';
	import { Button } from '$lib/components/ui/button';
	import { Card } from '$lib/components/ui/card';
	import { Input } from '$lib/components/ui/input';
	import { inventoryApi, type InventoryMovement, type InventoryReservation } from '$lib/api/inventory';
	import {
		productsApi,
		type Product,
		type ProductAvailability,
		type ProductCreate,
		type ProductUpdate
	} from '$lib/api/products';

	type ProductFormMode = 'add' | 'edit';
	type LifecycleAction = 'archive' | 'discontinue' | 'reactivate';

	let products = $state<Product[]>([]);
	let availability = $state<ProductAvailability[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let searchQuery = $state('');
	let toast = $state<{ type: 'success' | 'error'; message: string } | null>(null);

	let showFormModal = $state(false);
	let showDeleteModal = $state(false);
	let formMode = $state<ProductFormMode>('add');
	let submitting = $state(false);
	let selectedProduct = $state<Product | null>(null);

	let formName = $state('');
	let formSlug = $state('');
	let formSku = $state('');
	let formDescription = $state('');
	let formBpomNumber = $state('');
	let formUsageInstructions = $state('');
	let formIngredients = $state('');
	let formStorageInstructions = $state('');
	let formWarnings = $state('');
	let formNetWeight = $state('');
	let formCostPrice = $state('');
	let formPrice = $state('');
	let formStatus = $state<Product['status']>('draft');
	let slugManuallyEdited = $state(false);

	let detailProduct = $state<Product | null>(null);
	let detailAvailability = $state<ProductAvailability | null>(null);
	let detailMovements = $state<InventoryMovement[]>([]);
	let detailReservations = $state<InventoryReservation[]>([]);
	let detailLoading = $state(false);
	let detailError = $state<string | null>(null);

	const availabilityById = $derived(new Map(availability.map((item) => [item.id, item])));

	const filtered = $derived(
		products.filter((product) => {
			const query = searchQuery.trim().toLowerCase();
			const productAvailability = availabilityById.get(product.id);
			return (
				!query ||
				product.name.toLowerCase().includes(query) ||
				product.slug.toLowerCase().includes(query) ||
				(product.sku ?? '').toLowerCase().includes(query) ||
				String(product.id).includes(query) ||
				(productAvailability?.not_purchasable_reason ?? '').toLowerCase().includes(query)
			);
		})
	);

	const stats = $derived([
		{ label: 'Total products', value: products.length, icon: Boxes },
		{ label: 'Active listings', value: products.filter((p) => p.status === 'active').length, icon: PackageCheck },
		{ label: 'Purchasable', value: availability.filter((item) => item.is_purchasable).length, icon: CheckCircle2 },
		{ label: 'Low stock', value: availability.filter((item) => item.is_low_stock).length, icon: TriangleAlert }
	]);

	function showToast(type: 'success' | 'error', message: string) {
		toast = { type, message };
		setTimeout(() => (toast = null), 3500);
	}

	function formatNumber(value: number): string {
		return new Intl.NumberFormat('id-ID').format(value);
	}

	function formatPrice(raw: string | number | null): string {
		if (raw === null) return 'No price';
		const num = typeof raw === 'string' ? parseFloat(raw) : raw;
		return new Intl.NumberFormat('id-ID', {
			style: 'currency',
			currency: 'IDR',
			minimumFractionDigits: 0
		}).format(num);
	}

	function formatDate(iso: string): string {
		return new Intl.DateTimeFormat('id-ID', { dateStyle: 'medium', timeStyle: 'short' }).format(
			new Date(iso)
		);
	}

	function slugify(value: string): string {
		return value
			.toLowerCase()
			.replace(/[^a-z0-9]+/g, '-')
			.replace(/^-+|-+$/g, '') || 'product';
	}

	function statusVariant(status: Product['status']) {
		if (status === 'active') return 'success' as const;
		if (status === 'draft') return 'secondary' as const;
		if (status === 'discontinued') return 'warning' as const;
		return 'outline' as const;
	}

	function replaceProduct(updated: Product) {
		products = products.map((product) => (product.id === updated.id ? updated : product));
	}

	function emptyToNull(value: string): string | null {
		return value.trim() || null;
	}

	function primaryImage(product: Product) {
		return availabilityById.get(product.id)?.primary_image ?? null;
	}

	function availabilityFor(product: Product): ProductAvailability | null {
		return availabilityById.get(product.id) ?? null;
	}

	async function loadProducts() {
		loading = true;
		error = null;
		try {
			const [productsResult, catalogResult] = await Promise.allSettled([
				productsApi.list(),
				productsApi.catalog(0, 100, true)
			]);

			if (productsResult.status === 'fulfilled') products = productsResult.value;
			else throw productsResult.reason;

			availability = catalogResult.status === 'fulfilled' ? catalogResult.value : [];
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	onMount(loadProducts);

	function resetForm() {
		formName = '';
		formSlug = '';
		formSku = '';
		formDescription = '';
		formBpomNumber = '';
		formUsageInstructions = '';
		formIngredients = '';
		formStorageInstructions = '';
		formWarnings = '';
		formNetWeight = '';
		formCostPrice = '';
		formPrice = '';
		formStatus = 'draft';
		slugManuallyEdited = false;
	}

	function openAddModal() {
		formMode = 'add';
		selectedProduct = null;
		resetForm();
		showFormModal = true;
	}

	function openEditModal(product: Product) {
		formMode = 'edit';
		selectedProduct = product;
		formName = product.name;
		formSlug = product.slug;
		formSku = product.sku ?? '';
		formDescription = product.description ?? '';
		formBpomNumber = product.bpom_number ?? '';
		formUsageInstructions = product.usage_instructions ?? '';
		formIngredients = product.ingredients ?? '';
		formStorageInstructions = product.storage_instructions ?? '';
		formWarnings = product.warnings ?? '';
		formNetWeight = product.net_weight ?? '';
		formCostPrice = String(parseFloat(product.cost_price));
		formPrice = String(parseFloat(product.base_price));
		formStatus = product.status;
		slugManuallyEdited = true;
		showFormModal = true;
	}

	function openDeleteModal(product: Product) {
		selectedProduct = product;
		showDeleteModal = true;
	}

	function closeModals() {
		showFormModal = false;
		showDeleteModal = false;
		selectedProduct = null;
	}

	function handleNameInput() {
		if (!slugManuallyEdited) formSlug = slugify(formName);
	}

	function handleSlugInput() {
		slugManuallyEdited = true;
		formSlug = slugify(formSlug);
	}

	function productPayload(): ProductCreate | ProductUpdate {
		return {
			name: formName.trim(),
			slug: emptyToNull(formSlug),
			sku: emptyToNull(formSku),
			description: emptyToNull(formDescription),
			bpom_number: emptyToNull(formBpomNumber),
			usage_instructions: emptyToNull(formUsageInstructions),
			ingredients: emptyToNull(formIngredients),
			storage_instructions: emptyToNull(formStorageInstructions),
			warnings: emptyToNull(formWarnings),
			net_weight: emptyToNull(formNetWeight),
			cost_price: formCostPrice ? parseFloat(formCostPrice) : 0,
			base_price: parseFloat(formPrice),
			status: formStatus
		};
	}

	async function refreshAvailability(productId?: number) {
		try {
			if (productId) {
				const updated = await productsApi.getAvailability(productId);
				availability = [updated, ...availability.filter((item) => item.id !== updated.id)];
				if (detailProduct?.id === productId) detailAvailability = updated;
			} else {
				availability = await productsApi.catalog(0, 100, true);
			}
		} catch (e) {
			showToast('error', (e as Error).message);
		}
	}

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (!formName.trim() || !formPrice) return;
		submitting = true;
		try {
			if (formMode === 'add') {
				const created = await productsApi.create(productPayload() as ProductCreate);
				products = [created, ...products];
				await refreshAvailability(created.id);
				showToast('success', `Produk "${created.name}" berhasil ditambahkan.`);
			} else if (selectedProduct) {
				const updated = await productsApi.update(selectedProduct.id, productPayload() as ProductUpdate);
				replaceProduct(updated);
				await refreshAvailability(updated.id);
				showToast('success', `Produk "${updated.name}" berhasil diperbarui.`);
			}
			closeModals();
		} catch (e) {
			showToast('error', (e as Error).message);
		} finally {
			submitting = false;
		}
	}

	async function handleDelete() {
		if (!selectedProduct) return;
		submitting = true;
		try {
			await productsApi.remove(selectedProduct.id);
			const name = selectedProduct.name;
			const deletedId = selectedProduct.id;
			products = products.filter((product) => product.id !== deletedId);
			availability = availability.filter((item) => item.id !== deletedId);
			showToast('success', `Produk "${name}" berhasil dihapus.`);
			closeModals();
		} catch (e) {
			showToast('error', (e as Error).message);
		} finally {
			submitting = false;
		}
	}

	async function handleLifecycleAction(product: Product, action: LifecycleAction) {
		submitting = true;
		try {
			const updated =
				action === 'archive'
					? await productsApi.archive(product.id)
					: action === 'discontinue'
						? await productsApi.discontinue(product.id)
						: await productsApi.reactivate(product.id);

			replaceProduct(updated);
			await refreshAvailability(updated.id);
			const actionLabel =
				action === 'archive'
					? 'diarsipkan'
					: action === 'discontinue'
						? 'dihentikan'
						: 'diaktifkan kembali';
			showToast('success', `Produk "${updated.name}" berhasil ${actionLabel}.`);
		} catch (e) {
			showToast('error', (e as Error).message);
		} finally {
			submitting = false;
		}
	}

	async function openDetailPanel(product: Product) {
		detailProduct = product;
		detailAvailability = availabilityFor(product);
		detailMovements = [];
		detailReservations = [];
		detailError = null;
		await loadProductDetail(product);
	}

	async function loadProductDetail(product: Product) {
		detailLoading = true;
		detailError = null;
		const [availabilityResult, movementsResult, reservationsResult] = await Promise.allSettled([
			productsApi.getAvailability(product.id),
			inventoryApi.movementsByProduct(product.id),
			inventoryApi.activeReservationsByProduct(product.id)
		]);

		if (availabilityResult.status === 'fulfilled') detailAvailability = availabilityResult.value;
		else detailError = (availabilityResult.reason as Error).message;

		if (movementsResult.status === 'fulfilled') detailMovements = movementsResult.value;
		else detailMovements = [];

		if (reservationsResult.status === 'fulfilled') detailReservations = reservationsResult.value;
		else detailReservations = [];

		detailLoading = false;
	}

	function closeDetailPanel() {
		detailProduct = null;
		detailAvailability = null;
		detailMovements = [];
		detailReservations = [];
		detailError = null;
	}

	function handleBackdropClick(e: MouseEvent) {
		if (e.target === e.currentTarget) closeModals();
	}

	function handleBackdropKeydown(e: KeyboardEvent) {
		if (e.target !== e.currentTarget) return;
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			closeModals();
		}
	}

	function handleDetailBackdropClick(e: MouseEvent) {
		if (e.target === e.currentTarget) closeDetailPanel();
	}

	function handleDetailBackdropKeydown(e: KeyboardEvent) {
		if (e.target !== e.currentTarget) return;
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			closeDetailPanel();
		}
	}
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
		<h1 class="mt-1 text-3xl font-bold tracking-tight text-slate-950">Product catalog</h1>
		<p class="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
			Manage catalog identity, pricing, skincare details, images, and stock readiness from one place.
		</p>
	</div>

	<div class="flex flex-wrap gap-2">
		<Button variant="outline" onclick={loadProducts} disabled={loading}>
			{#if loading}
				<Loader2 size={16} class="animate-spin" />
			{:else}
				<RefreshCw size={16} />
			{/if}
			Refresh
		</Button>
		<Button id="btn-add-product" onclick={openAddModal}>
			<PackagePlus size={16} />
			Add Product
		</Button>
	</div>
</section>

<section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4" aria-label="Product summary">
	{#each stats as stat}
		{@const Icon = stat.icon}
		<Card class="p-5">
			<div class="flex items-center justify-between gap-3">
				<div>
					<p class="text-sm font-medium text-slate-500">{stat.label}</p>
					<p class="mt-2 text-2xl font-bold tabular-nums text-slate-950">{stat.value}</p>
				</div>
				<div class="flex h-10 w-10 items-center justify-center rounded-md bg-slate-100 text-slate-700">
					<Icon size={18} />
				</div>
			</div>
		</Card>
	{/each}
</section>

<Card class="mt-6 overflow-hidden">
	<div class="flex flex-col gap-3 border-b border-slate-200 p-5 xl:flex-row xl:items-center xl:justify-between">
		<div>
			<h2 class="text-base font-semibold">Products table</h2>
			<p class="text-sm text-slate-500">Inventory and purchasability are read from the product availability model.</p>
		</div>

		<div class="relative min-w-0 flex-1 xl:max-w-sm">
			<Search class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
			<Input class="pl-9" placeholder="Search name, slug, SKU, status reason..." bind:value={searchQuery} />
		</div>
	</div>

	<div class="overflow-x-auto">
		{#if loading}
			<div class="flex items-center justify-center gap-3 py-16 text-slate-500">
				<Loader2 size={20} class="animate-spin" />
				<span>Memuat produk...</span>
			</div>
		{:else if error}
			<div class="flex flex-col items-center justify-center gap-3 py-16 text-red-600">
				<TriangleAlert size={32} />
				<p class="font-medium">Gagal memuat produk</p>
				<p class="max-w-sm text-center text-sm text-slate-500">{error}</p>
				<Button variant="outline" onclick={loadProducts}>Coba lagi</Button>
			</div>
		{:else if filtered.length === 0}
			<div class="flex flex-col items-center justify-center gap-2 py-16 text-slate-500">
				<p class="font-medium">{searchQuery ? 'Tidak ada produk yang cocok.' : 'Belum ada produk.'}</p>
				{#if !searchQuery}
					<Button onclick={openAddModal}><PackagePlus size={16} /> Tambah Produk</Button>
				{/if}
			</div>
		{:else}
			<table class="w-full text-left text-sm">
				<thead class="bg-slate-50 text-xs uppercase text-slate-500">
					<tr>
						<th class="px-5 py-3 font-semibold">Product</th>
						<th class="px-5 py-3 font-semibold">Price</th>
						<th class="px-5 py-3 font-semibold">Inventory</th>
						<th class="px-5 py-3 font-semibold">Status</th>
						<th class="px-5 py-3 font-semibold">Updated</th>
						<th class="px-5 py-3 text-right font-semibold">Actions</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-slate-100">
					{#each filtered as product (product.id)}
						{@const itemAvailability = availabilityFor(product)}
						{@const image = primaryImage(product)}
						<tr class="hover:bg-slate-50">
							<td class="px-5 py-4">
								<div class="flex items-center gap-3">
									<div class="product-thumb">
										{#if image}
											<img src={image.image_url} alt={image.alt_text ?? product.name} />
										{:else}
											<Images size={18} />
										{/if}
									</div>
									<div>
										<p class="font-medium text-slate-950">{product.name}</p>
										<p class="font-mono text-xs text-slate-500">/{product.slug}</p>
										<p class="text-xs text-slate-500">SKU: {product.sku ?? 'Not set'}</p>
									</div>
								</div>
							</td>
							<td class="px-5 py-4">
								<p class="font-medium tabular-nums text-slate-950">{formatPrice(product.base_price)}</p>
								<p class="text-xs tabular-nums text-slate-500">Cost {formatPrice(product.cost_price)}</p>
								<p class="text-xs tabular-nums text-slate-500">Effective {formatPrice(itemAvailability?.effective_price ?? null)}</p>
							</td>
							<td class="px-5 py-4">
								{#if itemAvailability}
									<p class="font-medium tabular-nums text-slate-950">Available {formatNumber(itemAvailability.available_quantity)}</p>
									<p class="text-xs tabular-nums text-slate-500">On hand {formatNumber(itemAvailability.on_hand_quantity)} / Reserved {formatNumber(itemAvailability.reserved_quantity)}</p>
									{#if itemAvailability.is_low_stock}
										<Badge variant="warning">Low stock</Badge>
									{/if}
								{:else}
									<Badge variant="outline">Not tracked</Badge>
								{/if}
							</td>
							<td class="px-5 py-4">
								<div class="flex flex-col gap-1">
									<Badge variant={statusVariant(product.status)}>{product.status}</Badge>
									{#if itemAvailability?.is_purchasable}
										<Badge variant="success">Purchasable</Badge>
									{:else}
										<Badge variant="outline">{itemAvailability?.not_purchasable_reason ?? 'Not ready'}</Badge>
									{/if}
								</div>
							</td>
							<td class="px-5 py-4 text-xs text-slate-600">{formatDate(product.updated_at)}</td>
							<td class="px-5 py-4">
								<div class="flex flex-wrap justify-end gap-1">
									<Button variant="ghost" size="icon" aria-label="View {product.name}" onclick={() => openDetailPanel(product)}><Eye size={16} /></Button>
									<Button variant="ghost" size="icon" aria-label="Edit {product.name}" onclick={() => openEditModal(product)}><Edit size={16} /></Button>
									{#if product.status !== 'archived'}
										<Button variant="ghost" size="icon" aria-label="Archive {product.name}" disabled={submitting} onclick={() => handleLifecycleAction(product, 'archive')}><Archive size={16} /></Button>
									{/if}
									{#if product.status !== 'discontinued'}
										<Button variant="ghost" size="icon" class="text-amber-700 hover:bg-amber-50 hover:text-amber-800" aria-label="Discontinue {product.name}" disabled={submitting} onclick={() => handleLifecycleAction(product, 'discontinue')}><Ban size={16} /></Button>
									{/if}
									{#if product.status === 'archived' || product.status === 'discontinued'}
										<Button variant="ghost" size="icon" class="text-emerald-700 hover:bg-emerald-50 hover:text-emerald-800" aria-label="Reactivate {product.name}" disabled={submitting} onclick={() => handleLifecycleAction(product, 'reactivate')}><RotateCcw size={16} /></Button>
									{/if}
									{#if product.status === 'draft'}
										<Button variant="ghost" size="icon" class="text-red-600 hover:bg-red-50 hover:text-red-700" aria-label="Delete draft product {product.name}" onclick={() => openDeleteModal(product)}><Trash2 size={16} /></Button>
									{/if}
								</div>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		{/if}
	</div>
</Card>

{#if showFormModal}
	<div class="modal-backdrop" role="button" tabindex="0" aria-label="Close product form modal" onclick={handleBackdropClick} onkeydown={handleBackdropKeydown}>
		<div class="modal modal--wide" role="dialog" aria-modal="true" aria-labelledby="modal-title">
			<div class="modal-header">
				<div>
					<h2 id="modal-title" class="text-lg font-semibold">{formMode === 'add' ? 'Tambah Produk Baru' : 'Edit Produk'}</h2>
					<p class="mt-1 text-sm text-slate-500">Cost price hanya internal. Base sell price adalah harga jual fallback.</p>
				</div>
				<button class="modal-close" onclick={closeModals} aria-label="Close"><X size={18} /></button>
			</div>

			<form class="modal-body" onsubmit={handleSubmit}>
				<div class="form-grid">
					<div class="field">
						<label for="form-name">Nama Produk <span class="required">*</span></label>
						<input id="form-name" type="text" bind:value={formName} oninput={handleNameInput} required maxlength={255} />
					</div>
					<div class="field">
						<label for="form-slug">Slug</label>
						<input id="form-slug" type="text" bind:value={formSlug} oninput={handleSlugInput} maxlength={255} />
						<p class="field-hint">Dipakai untuk URL storefront.</p>
					</div>
					<div class="field">
						<label for="form-sku">SKU</label>
						<input id="form-sku" type="text" bind:value={formSku} maxlength={100} />
					</div>
					<div class="field">
						<label for="form-bpom">BPOM</label>
						<input id="form-bpom" type="text" bind:value={formBpomNumber} maxlength={100} />
					</div>
					<div class="field">
						<label for="form-cost-price">Cost price internal</label>
						<input id="form-cost-price" type="number" bind:value={formCostPrice} min="0" step="1000" placeholder="Harga modal" />
					</div>
					<div class="field">
						<label for="form-price">Base sell price <span class="required">*</span></label>
						<input id="form-price" type="number" bind:value={formPrice} min="0" step="1000" required placeholder="Harga jual fallback" />
					</div>
					<div class="field">
						<label for="form-net-weight">Net weight</label>
						<input id="form-net-weight" type="text" bind:value={formNetWeight} maxlength={100} placeholder="100 ml" />
					</div>
					<div class="field">
						<label for="form-status">Status</label>
						<select id="form-status" bind:value={formStatus}>
							<option value="draft">Draft</option>
							<option value="active">Active</option>
							<option value="archived">Archived</option>
							<option value="discontinued">Discontinued</option>
						</select>
					</div>
				</div>

				<div class="field"><label for="form-description">Deskripsi</label><textarea id="form-description" bind:value={formDescription} rows={3}></textarea></div>
				<div class="field"><label for="form-usage">Cara pakai</label><textarea id="form-usage" bind:value={formUsageInstructions} rows={3}></textarea></div>
				<div class="field"><label for="form-ingredients">Komposisi</label><textarea id="form-ingredients" bind:value={formIngredients} rows={3}></textarea></div>
				<div class="field"><label for="form-storage">Storage instructions</label><textarea id="form-storage" bind:value={formStorageInstructions} rows={2}></textarea></div>
				<div class="field"><label for="form-warnings">Warnings</label><textarea id="form-warnings" bind:value={formWarnings} rows={2}></textarea></div>

				<div class="modal-footer">
					<Button type="button" variant="outline" onclick={closeModals} disabled={submitting}>Batal</Button>
					<Button type="submit" disabled={submitting || !formName.trim() || !formPrice}>{#if submitting}<Loader2 size={16} class="animate-spin" />{/if}{formMode === 'add' ? 'Simpan Produk' : 'Perbarui Produk'}</Button>
				</div>
			</form>
		</div>
	</div>
{/if}

{#if showDeleteModal && selectedProduct}
	<div class="modal-backdrop" role="button" tabindex="0" aria-label="Close delete product modal" onclick={handleBackdropClick} onkeydown={handleBackdropKeydown}>
		<div class="modal modal--danger" role="dialog" aria-modal="true" aria-labelledby="delete-title">
			<div class="modal-header">
				<h2 id="delete-title" class="text-lg font-semibold text-red-700">Hapus Produk</h2>
				<button class="modal-close" onclick={closeModals} aria-label="Close"><X size={18} /></button>
			</div>
			<div class="modal-body">
				<div class="delete-warning">
					<TriangleAlert size={40} class="text-red-500" />
					<p>Apakah kamu yakin ingin menghapus produk <strong>"{selectedProduct.name}"</strong>? Hard delete hanya untuk draft tanpa histori. Untuk produk yang sudah berjalan, gunakan Archive atau Discontinue.</p>
				</div>
				<div class="modal-footer">
					<Button variant="outline" onclick={closeModals} disabled={submitting}>Batal</Button>
					<Button class="bg-red-600 text-white hover:bg-red-700" onclick={handleDelete} disabled={submitting}>{#if submitting}<Loader2 size={16} class="animate-spin" />{/if}Ya, Hapus</Button>
				</div>
			</div>
		</div>
	</div>
{/if}

{#if detailProduct}
	<div class="detail-backdrop" role="button" tabindex="0" aria-label="Close product detail panel" onclick={handleDetailBackdropClick} onkeydown={handleDetailBackdropKeydown}>
		<div class="detail-panel" role="dialog" aria-modal="true" aria-labelledby="detail-title">
			<div class="detail-header">
				<div>
					<p class="text-sm font-medium text-slate-500">Product detail</p>
					<h2 id="detail-title" class="mt-1 text-xl font-bold text-slate-950">{detailProduct.name}</h2>
					<p class="mt-1 font-mono text-xs text-slate-500">/{detailProduct.slug}</p>
				</div>
				<button class="modal-close" onclick={closeDetailPanel} aria-label="Close"><X size={18} /></button>
			</div>

			<div class="detail-body">
				{#if detailLoading}
					<div class="detail-empty"><Loader2 size={18} class="animate-spin" /> Memuat detail product...</div>
				{/if}
				{#if detailError}
					<div class="detail-alert"><TriangleAlert size={16} /> <p>{detailError}</p></div>
				{/if}

				<section class="detail-section">
					<h3><CircleDollarSign size={16} /> Catalog and price</h3>
					<div class="info-grid">
						<div><span>Status</span><strong>{detailProduct.status}</strong></div>
						<div><span>SKU</span><strong>{detailProduct.sku ?? 'Not set'}</strong></div>
						<div><span>BPOM</span><strong>{detailProduct.bpom_number ?? 'Not set'}</strong></div>
						<div><span>Net weight</span><strong>{detailProduct.net_weight ?? 'Not set'}</strong></div>
						<div><span>Cost price</span><strong>{formatPrice(detailProduct.cost_price)}</strong></div>
						<div><span>Base sell price</span><strong>{formatPrice(detailProduct.base_price)}</strong></div>
						<div><span>Effective price</span><strong>{formatPrice(detailAvailability?.effective_price ?? null)}</strong></div>
						<div><span>Purchasable</span><strong>{detailAvailability?.is_purchasable ? 'Yes' : (detailAvailability?.not_purchasable_reason ?? 'No')}</strong></div>
					</div>
				</section>

				<section class="detail-section">
					<h3><Images size={16} /> Primary image</h3>
					{#if detailAvailability?.primary_image}
						<div class="primary-image-summary">
							<img
								src={detailAvailability.primary_image.image_url}
								alt={detailAvailability.primary_image.alt_text ?? detailProduct.name}
							/>
							<div>
								<p class="font-medium text-slate-950">
									{detailAvailability.primary_image.alt_text ?? 'Primary storefront image'}
								</p>
								<p class="image-url">{detailAvailability.primary_image.image_url}</p>
								<Button size="sm" variant="outline" href={`/admin/products/images?product_id=${detailProduct.id}`}>Manage images</Button>
							</div>
						</div>
					{:else}
						<div class="detail-empty">
							<Images size={18} />
							No primary image yet.
							<Button size="sm" variant="outline" href={`/admin/products/images?product_id=${detailProduct.id}`}>Manage images</Button>
						</div>
					{/if}
				</section>

				<section class="detail-section">
					<h3><PackageCheck size={16} /> Inventory summary</h3>
					<div class="info-grid">
						<div><span>On hand</span><strong>{formatNumber(detailAvailability?.on_hand_quantity ?? 0)}</strong></div>
						<div><span>Reserved</span><strong>{formatNumber(detailAvailability?.reserved_quantity ?? 0)}</strong></div>
						<div><span>Available</span><strong>{formatNumber(detailAvailability?.available_quantity ?? 0)}</strong></div>
						<div><span>Stock flag</span><strong>{detailAvailability?.is_low_stock ? 'Low stock' : 'Healthy / not tracked'}</strong></div>
					</div>
				</section>

				<section class="detail-section">
					<h3><RefreshCw size={16} /> Recent movements</h3>
					{#if detailMovements.length === 0}
						<div class="detail-empty">Belum ada movement.</div>
					{:else}
						<div class="mini-list">
							{#each detailMovements.slice(0, 5) as movement (movement.id)}
								<div><strong>{movement.movement_type}</strong><span>{formatNumber(movement.quantity)} pcs · {formatDate(movement.created_at)}</span></div>
							{/each}
						</div>
					{/if}
				</section>

				<section class="detail-section">
					<h3><Archive size={16} /> Active reservations</h3>
					{#if detailReservations.length === 0}
						<div class="detail-empty">Tidak ada active reservation.</div>
					{:else}
						<div class="mini-list">
							{#each detailReservations as reservation (reservation.id)}
								<div><strong>Reservation #{reservation.id}</strong><span>Order #{reservation.order_id} · {formatNumber(reservation.quantity)} pcs</span></div>
							{/each}
						</div>
					{/if}
				</section>
			</div>
		</div>
	</div>
{/if}

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
		animation: slide-in 0.25s ease;
	}
	.toast--success { background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }
	.toast--error { background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
	@keyframes slide-in { from { transform: translateY(1rem); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

	.product-thumb {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 3rem;
		height: 3rem;
		flex-shrink: 0;
		overflow: hidden;
		border-radius: 0.625rem;
		background: #f1f5f9;
		color: #64748b;
	}
	.product-thumb img { width: 100%; height: 100%; object-fit: cover; }

	.modal-backdrop,
	.detail-backdrop {
		position: fixed;
		inset: 0;
		z-index: 9000;
		background: rgba(15, 23, 42, 0.45);
		backdrop-filter: blur(3px);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 1rem;
		animation: fade-in 0.15s ease;
	}
	.detail-backdrop { justify-content: flex-end; z-index: 8500; }
	@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }

	.modal {
		background: white;
		border-radius: 0.75rem;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
		width: 100%;
		max-width: 32rem;
		max-height: calc(100vh - 2rem);
		overflow: hidden;
		animation: scale-in 0.2s ease;
	}
	.modal--wide { max-width: 54rem; overflow-y: auto; }
	.modal--danger .modal-header { border-bottom-color: #fecaca; background: #fff5f5; }
	@keyframes scale-in { from { transform: scale(0.96); opacity: 0; } to { transform: scale(1); opacity: 1; } }

	.modal-header,
	.detail-header {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 1rem;
		padding: 1.25rem 1.5rem;
		border-bottom: 1px solid #e2e8f0;
	}
	.modal-close {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 2rem;
		height: 2rem;
		border-radius: 0.375rem;
		color: #64748b;
		background: transparent;
		border: none;
		cursor: pointer;
	}
	.modal-close:hover { background: #f1f5f9; color: #0f172a; }
	.modal-body { padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem; }
	.modal-footer { display: flex; justify-content: flex-end; gap: 0.5rem; padding-top: 0.5rem; }

	.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; }
	.field { display: flex; flex-direction: column; gap: 0.375rem; }
	.field label { font-size: 0.875rem; font-weight: 500; color: #374151; }
	.required { color: #ef4444; }
	.field input,
	.field textarea,
	.field select {
		width: 100%;
		padding: 0.5rem 0.75rem;
		border: 1px solid #d1d5db;
		border-radius: 0.5rem;
		font-size: 0.875rem;
		color: #111827;
		background: white;
		outline: none;
	}
	.field textarea { resize: vertical; }
	.field-hint { font-size: 0.75rem; color: #64748b; }
	.delete-warning { display: flex; flex-direction: column; align-items: center; text-align: center; gap: 0.75rem; padding: 0.5rem 0; color: #374151; }

	.detail-panel {
		height: 100%;
		width: min(100%, 46rem);
		overflow: hidden;
		background: white;
		box-shadow: -24px 0 60px rgba(15, 23, 42, 0.22);
		animation: slide-panel 0.22s ease;
	}
	@keyframes slide-panel { from { transform: translateX(2rem); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
	.detail-body { height: calc(100% - 6rem); overflow-y: auto; padding: 1.5rem; display: flex; flex-direction: column; gap: 1.25rem; }
	.detail-section { display: flex; flex-direction: column; gap: 0.75rem; }
	.detail-section h3 { display: flex; align-items: center; gap: 0.5rem; font-size: 1rem; font-weight: 700; color: #0f172a; }
	.info-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.75rem; }
	.info-grid div { border: 1px solid #e2e8f0; border-radius: 0.75rem; padding: 0.75rem; background: #f8fafc; }
	.info-grid span { display: block; font-size: 0.75rem; color: #64748b; }
	.info-grid strong { display: block; margin-top: 0.25rem; color: #0f172a; overflow-wrap: anywhere; }
	.detail-alert,
	.detail-empty { display: flex; align-items: center; justify-content: center; gap: 0.5rem; border-radius: 0.75rem; padding: 1rem; font-size: 0.875rem; color: #64748b; background: #f8fafc; border: 1px dashed #cbd5e1; }
	.detail-alert { justify-content: flex-start; color: #991b1b; background: #fef2f2; border: 1px solid #fecaca; }

	.primary-image-summary { display: grid; grid-template-columns: 9rem minmax(0, 1fr); gap: 1rem; align-items: center; border: 1px solid #e2e8f0; border-radius: 0.75rem; padding: 0.75rem; background: #f8fafc; }
	.primary-image-summary img { width: 9rem; height: 9rem; object-fit: cover; border-radius: 0.625rem; background: #f1f5f9; }
	.primary-image-summary div { display: flex; flex-direction: column; gap: 0.5rem; min-width: 0; }
	.image-url { overflow-wrap: anywhere; font-size: 0.75rem; color: #64748b; }
	.mini-list { display: flex; flex-direction: column; gap: 0.5rem; }
	.mini-list div { display: flex; justify-content: space-between; gap: 1rem; border: 1px solid #e2e8f0; border-radius: 0.625rem; padding: 0.75rem; }
	.mini-list span { font-size: 0.8125rem; color: #64748b; }

	@media (max-width: 760px) {
		.form-grid,
		.info-grid,
		.primary-image-summary { grid-template-columns: 1fr; }
		.modal-footer { flex-direction: column-reverse; }
		.modal-footer :global(button) { width: 100%; }
	}
</style>
