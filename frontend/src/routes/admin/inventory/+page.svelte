<script lang="ts">
	import { onMount } from 'svelte';
	import {
		AlertTriangle,
		Archive,
		Boxes,
		CheckCheck,
		CheckCircle2,
		CircleGauge,
		Clock3,
		Eye,
		History,
		ListChecks,
		Loader2,
		MinusCircle,
		PackageCheck,
		PlusCircle,
		RefreshCw,
		Search,
		ShieldCheck,
		Undo2,
		X
	} from 'lucide-svelte';
	import { Badge } from '$lib/components/ui/badge';
	import { Button } from '$lib/components/ui/button';
	import { Card } from '$lib/components/ui/card';
	import { Input } from '$lib/components/ui/input';
	import {
		inventoryApi,
		type InventoryItem,
		type InventoryMovement,
		type InventoryReservation
	} from '$lib/api/inventory';
	import { productsApi, type Product } from '$lib/api/products';

	type StockFilter = 'all' | 'low' | 'reserved' | 'available';
	type ActionMode = 'receive' | 'adjust';
	type ReservationActionMode = 'release' | 'commit';

	let inventoryItems = $state<InventoryItem[]>([]);
	let products = $state<Product[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let productLoadError = $state<string | null>(null);
	let searchQuery = $state('');
	let stockFilter = $state<StockFilter>('all');
	let toast = $state<{ type: 'success' | 'error'; message: string } | null>(null);
	let showActionModal = $state(false);
	let actionMode = $state<ActionMode>('receive');
	let actionSubmitting = $state(false);
	let selectedProductId = $state('');
	let actionQuantity = $state('');
	let actionNotes = $state('');
	let actionReferenceType = $state('');
	let actionReferenceId = $state('');
	let detailItem = $state<InventoryItem | null>(null);
	let detailMovements = $state<InventoryMovement[]>([]);
	let detailReservations = $state<InventoryReservation[]>([]);
	let detailLoading = $state(false);
	let detailError = $state<string | null>(null);
	let showReservationConfirm = $state(false);
	let reservationActionMode = $state<ReservationActionMode>('release');
	let selectedReservation = $state<InventoryReservation | null>(null);
	let reservationActionNotes = $state('');
	let reservationSubmitting = $state(false);

	const productById = $derived(new Map(products.map((product) => [product.id, product])));

	const filteredItems = $derived(
		inventoryItems.filter((item) => {
			const product = productById.get(item.product_id);
			const query = searchQuery.trim().toLowerCase();
			const matchesSearch =
				!query ||
				String(item.product_id).includes(query) ||
				product?.name.toLowerCase().includes(query);

			const matchesFilter =
				stockFilter === 'all' ||
				(stockFilter === 'low' && item.is_low_stock) ||
				(stockFilter === 'reserved' && item.reserved_quantity > 0) ||
				(stockFilter === 'available' && item.available_quantity > 0);

			return matchesSearch && matchesFilter;
		})
	);

	const summary = $derived({
		totalSku: inventoryItems.length,
		totalOnHand: inventoryItems.reduce((sum, item) => sum + item.on_hand_quantity, 0),
		totalReserved: inventoryItems.reduce((sum, item) => sum + item.reserved_quantity, 0),
		totalAvailable: inventoryItems.reduce((sum, item) => sum + item.available_quantity, 0),
		lowStockCount: inventoryItems.filter((item) => item.is_low_stock).length
	});

	const summaryCards = $derived([
		{
			label: 'SKU tracked',
			value: summary.totalSku,
			icon: Boxes,
			tone: 'text-slate-700',
			bg: 'bg-slate-100'
		},
		{
			label: 'On hand',
			value: summary.totalOnHand,
			icon: Archive,
			tone: 'text-cyan-700',
			bg: 'bg-cyan-50'
		},
		{
			label: 'Reserved',
			value: summary.totalReserved,
			icon: ShieldCheck,
			tone: 'text-amber-700',
			bg: 'bg-amber-50'
		},
		{
			label: 'Available',
			value: summary.totalAvailable,
			icon: PackageCheck,
			tone: 'text-emerald-700',
			bg: 'bg-emerald-50'
		},
		{
			label: 'Low stock',
			value: summary.lowStockCount,
			icon: AlertTriangle,
			tone: 'text-red-700',
			bg: 'bg-red-50'
		}
	]);

	const filters: { label: string; value: StockFilter }[] = [
		{ label: 'All', value: 'all' },
		{ label: 'Low stock', value: 'low' },
		{ label: 'Reserved', value: 'reserved' },
		{ label: 'Available', value: 'available' }
	];

	const trackedProductIds = $derived(new Set(inventoryItems.map((item) => item.product_id)));
	const actionProductOptions = $derived(
		actionMode === 'receive'
			? products
			: products.filter((product) => trackedProductIds.has(product.id))
	);
	const selectedInventoryItem = $derived(
		inventoryItems.find((item) => item.product_id === Number(selectedProductId)) ?? null
	);
	const canSubmitAction = $derived(
		Boolean(selectedProductId) &&
			(actionMode === 'receive' ? Number(actionQuantity) > 0 : Number(actionQuantity) !== 0) &&
			(actionMode === 'receive' || actionNotes.trim().length > 0)
	);

	function showToast(type: 'success' | 'error', message: string) {
		toast = { type, message };
		setTimeout(() => (toast = null), 3500);
	}

	function formatNumber(value: number): string {
		return new Intl.NumberFormat('id-ID').format(value);
	}

	function formatDate(iso: string): string {
		return new Intl.DateTimeFormat('id-ID', { dateStyle: 'medium', timeStyle: 'short' }).format(
			new Date(iso)
		);
	}

	function formatOptionalDate(iso: string | null): string {
		return iso ? formatDate(iso) : 'No expiry';
	}

	function productName(item: InventoryItem): string {
		return productById.get(item.product_id)?.name ?? `Product #${item.product_id}`;
	}

	function productLabel(product: Product): string {
		return `${product.name} (#${product.id})`;
	}

	function movementLabel(type: InventoryMovement['movement_type']): string {
		return type
			.split('_')
			.map((part) => part.charAt(0).toUpperCase() + part.slice(1))
			.join(' ');
	}

	function referenceLabel(referenceType: string | null, referenceId: number | null): string {
		if (!referenceType && !referenceId) return 'No reference';
		if (!referenceId) return referenceType ?? 'No reference';
		if (!referenceType) return `#${referenceId}`;
		return `${referenceType} #${referenceId}`;
	}

	function movementVariant(type: InventoryMovement['movement_type']) {
		if (type === 'inbound' || type === 'return') return 'success' as const;
		if (type === 'reservation') return 'warning' as const;
		if (type === 'deduction') return 'secondary' as const;
		return 'outline' as const;
	}

	function reservationActionLabel(mode: ReservationActionMode): string {
		return mode === 'release' ? 'Release reservation' : 'Commit reservation';
	}

	async function loadInventory() {
		loading = true;
		error = null;
		productLoadError = null;

		const [inventoryResult, productsResult] = await Promise.allSettled([
			inventoryApi.list(),
			productsApi.list()
		]);

		if (inventoryResult.status === 'fulfilled') {
			inventoryItems = inventoryResult.value;
		} else {
			error = inventoryResult.reason instanceof Error ? inventoryResult.reason.message : 'Unknown error';
		}

		if (productsResult.status === 'fulfilled') {
			products = productsResult.value;
		} else {
			productLoadError =
				productsResult.reason instanceof Error ? productsResult.reason.message : 'Unknown error';
		}

		loading = false;
	}

	function openActionModal(mode: ActionMode, item?: InventoryItem) {
		actionMode = mode;
		selectedProductId = item ? String(item.product_id) : '';
		actionQuantity = '';
		actionNotes = '';
		actionReferenceType = mode === 'receive' ? 'manual_receive' : 'manual_adjustment';
		actionReferenceId = '';
		showActionModal = true;
	}

	function closeActionModal() {
		if (actionSubmitting) return;
		showActionModal = false;
	}

	async function handleActionSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (!canSubmitAction) return;

		const productId = Number(selectedProductId);
		const quantity = Number(actionQuantity);
		const referenceType = actionReferenceType.trim() || null;
		const referenceId = actionReferenceId ? Number(actionReferenceId) : null;
		const notes = actionNotes.trim() || null;

		actionSubmitting = true;
		try {
			const updated =
				actionMode === 'receive'
					? await inventoryApi.receiveStock({
							product_id: productId,
							quantity,
							reference_type: referenceType,
							reference_id: referenceId,
							notes
						})
					: await inventoryApi.adjustStock({
							product_id: productId,
							delta: quantity,
							reference_type: referenceType,
							reference_id: referenceId,
							notes
						});

			inventoryItems = [
				updated,
				...inventoryItems.filter((item) => item.id !== updated.id)
			].sort((a, b) => a.product_id - b.product_id);
			showToast(
				'success',
				actionMode === 'receive'
					? `Stock ${productName(updated)} bertambah ${formatNumber(quantity)}.`
					: `Stock ${productName(updated)} disesuaikan ${quantity > 0 ? '+' : ''}${formatNumber(quantity)}.`
			);
			showActionModal = false;
			await loadInventory();
			if (detailItem?.product_id === updated.product_id) {
				detailItem = updated;
				await loadDetail(updated);
			}
		} catch (e) {
			showToast('error', (e as Error).message);
		} finally {
			actionSubmitting = false;
		}
	}

	function handleBackdropClick(e: MouseEvent) {
		if (e.target === e.currentTarget) closeActionModal();
	}

	function handleBackdropKeydown(e: KeyboardEvent) {
		if (e.target !== e.currentTarget) return;
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			closeActionModal();
		}
	}

	async function loadDetail(item: InventoryItem) {
		detailLoading = true;
		detailError = null;
		const [movementsResult, reservationsResult] = await Promise.allSettled([
			inventoryApi.movementsByProduct(item.product_id),
			inventoryApi.activeReservationsByProduct(item.product_id)
		]);

		if (movementsResult.status === 'fulfilled') {
			detailMovements = movementsResult.value;
		} else {
			detailMovements = [];
			detailError =
				movementsResult.reason instanceof Error ? movementsResult.reason.message : 'Unknown error';
		}

		if (reservationsResult.status === 'fulfilled') {
			detailReservations = reservationsResult.value;
		} else {
			detailReservations = [];
			detailError =
				reservationsResult.reason instanceof Error
					? reservationsResult.reason.message
					: 'Unknown error';
		}

		detailLoading = false;
	}

	async function refreshInventoryItem(productId: number) {
		const updatedItem = await inventoryApi.getByProduct(productId);
		inventoryItems = [
			updatedItem,
			...inventoryItems.filter((item) => item.id !== updatedItem.id)
		].sort((a, b) => a.product_id - b.product_id);

		if (detailItem?.product_id === productId) {
			detailItem = updatedItem;
			await loadDetail(updatedItem);
		}
	}

	async function openDetailPanel(item: InventoryItem) {
		detailItem = item;
		detailMovements = [];
		detailReservations = [];
		await loadDetail(item);
	}

	function closeDetailPanel() {
		detailItem = null;
		detailMovements = [];
		detailReservations = [];
		detailError = null;
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

	function openReservationConfirm(mode: ReservationActionMode, reservation: InventoryReservation) {
		reservationActionMode = mode;
		selectedReservation = reservation;
		reservationActionNotes = mode === 'release' ? 'Released by admin' : 'Committed by admin';
		showReservationConfirm = true;
	}

	function closeReservationConfirm() {
		if (reservationSubmitting) return;
		showReservationConfirm = false;
		selectedReservation = null;
		reservationActionNotes = '';
	}

	async function handleReservationActionSubmit(e: SubmitEvent) {
		e.preventDefault();
		if (!selectedReservation) return;

		const reservation = selectedReservation;
		reservationSubmitting = true;
		try {
			if (reservationActionMode === 'release') {
				await inventoryApi.releaseReservation({
					reservation_id: reservation.id,
					notes: reservationActionNotes.trim() || null
				});
			} else {
				await inventoryApi.commitReservation({
					reservation_id: reservation.id,
					notes: reservationActionNotes.trim() || null
				});
			}

			await refreshInventoryItem(reservation.product_id);
			showToast(
				'success',
				reservationActionMode === 'release'
					? `Reservation #${reservation.id} released.`
					: `Reservation #${reservation.id} committed.`
			);
			showReservationConfirm = false;
			selectedReservation = null;
			reservationActionNotes = '';
		} catch (err) {
			showToast('error', (err as Error).message);
		} finally {
			reservationSubmitting = false;
		}
	}

	function handleReservationBackdropClick(e: MouseEvent) {
		if (e.target === e.currentTarget) closeReservationConfirm();
	}

	function handleReservationBackdropKeydown(e: KeyboardEvent) {
		if (e.target !== e.currentTarget) return;
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			closeReservationConfirm();
		}
	}

	onMount(loadInventory);
</script>

{#if toast}
	<div class="toast toast--{toast.type}" role="alert" aria-live="polite">
		{#if toast.type === 'success'}
			<CheckCircle2 size={18} />
		{:else}
			<AlertTriangle size={18} />
		{/if}
		<span>{toast.message}</span>
	</div>
{/if}

<section class="mb-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
	<div>
		<p class="text-sm font-medium text-slate-500">Inventory</p>
		<h1 class="mt-1 text-3xl font-bold tracking-tight text-slate-950">Stock overview</h1>
		<p class="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
			Monitor aggregate stock, reservations, availability, and low-stock risk across products.
		</p>
	</div>

	<div class="flex flex-wrap gap-2">
		<Button variant="outline" onclick={loadInventory} disabled={loading}>
			{#if loading}
				<Loader2 size={16} class="animate-spin" />
			{:else}
				<RefreshCw size={16} />
			{/if}
			Refresh
		</Button>
		<Button onclick={() => openActionModal('receive')}>
			<PlusCircle size={16} />
			Receive stock
		</Button>
		<Button variant="outline" onclick={() => openActionModal('adjust')}>
			<MinusCircle size={16} />
			Adjust stock
		</Button>
	</div>
</section>

<section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-5" aria-label="Inventory summary">
	{#each summaryCards as stat}
		{@const Icon = stat.icon}
		<Card class="p-5">
			<div class="flex items-center justify-between gap-3">
				<div>
					<p class="text-sm font-medium text-slate-500">{stat.label}</p>
					<p class="mt-2 text-2xl font-bold tabular-nums text-slate-950">
						{formatNumber(stat.value)}
					</p>
				</div>
				<div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-md {stat.bg}">
					<Icon size={18} class={stat.tone} />
				</div>
			</div>
		</Card>
	{/each}
</section>

<Card class="mt-6 overflow-hidden">
	<div
		class="flex flex-col gap-4 border-b border-slate-200 p-5 xl:flex-row xl:items-center xl:justify-between"
	>
		<div>
			<h2 class="text-base font-semibold text-slate-950">Inventory table</h2>
			<p class="text-sm text-slate-500">Availability is derived from on-hand minus reserved stock.</p>
		</div>

		<div class="flex w-full flex-col gap-2 lg:flex-row xl:w-auto">
			<div class="relative min-w-0 flex-1 xl:w-80">
				<Search class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
				<Input
					class="pl-9"
					placeholder="Search product name or ID..."
					aria-label="Search inventory"
					bind:value={searchQuery}
				/>
			</div>

			<div class="inline-flex rounded-md border border-slate-200 bg-white p-1">
				{#each filters as filter}
					<button
						type="button"
						class="rounded px-3 py-1.5 text-sm font-medium transition-colors {stockFilter ===
						filter.value
							? 'bg-slate-950 text-white'
							: 'text-slate-600 hover:bg-slate-100 hover:text-slate-950'}"
						onclick={() => (stockFilter = filter.value)}
					>
						{filter.label}
					</button>
				{/each}
			</div>
		</div>
	</div>

	{#if productLoadError && !error}
		<div class="flex items-start gap-2 border-b border-amber-200 bg-amber-50 px-5 py-3 text-sm text-amber-800">
			<AlertTriangle size={16} class="mt-0.5 shrink-0" />
			<p>Product names could not be loaded. Inventory rows are shown by product ID.</p>
		</div>
	{/if}

	<div class="overflow-x-auto">
		{#if loading}
			<div class="flex items-center justify-center gap-3 py-16 text-slate-500">
				<Loader2 size={20} class="animate-spin" />
				<span>Memuat inventory...</span>
			</div>
		{:else if error}
			<div class="flex flex-col items-center justify-center gap-3 px-5 py-16 text-red-600">
				<AlertTriangle size={32} />
				<p class="font-medium">Gagal memuat inventory</p>
				<p class="max-w-md text-center text-sm text-slate-500">{error}</p>
				<Button variant="outline" onclick={loadInventory}>Coba lagi</Button>
			</div>
		{:else if filteredItems.length === 0}
			<div class="flex flex-col items-center justify-center gap-2 px-5 py-16 text-slate-500">
				<CircleGauge size={32} class="text-slate-400" />
				<p class="font-medium">
					{inventoryItems.length === 0
						? 'Belum ada inventory yang dilacak.'
						: 'Tidak ada inventory yang cocok.'}
				</p>
				{#if searchQuery || stockFilter !== 'all'}
					<p class="text-sm">Coba ubah pencarian atau filter stok.</p>
				{/if}
			</div>
		{:else}
			<table class="w-full text-left text-sm">
				<thead class="bg-slate-50 text-xs uppercase text-slate-500">
					<tr>
						<th class="px-5 py-3 font-semibold">Product</th>
						<th class="px-5 py-3 text-right font-semibold">On hand</th>
						<th class="px-5 py-3 text-right font-semibold">Reserved</th>
						<th class="px-5 py-3 text-right font-semibold">Available</th>
						<th class="px-5 py-3 text-right font-semibold">Threshold</th>
						<th class="px-5 py-3 font-semibold">Status</th>
						<th class="px-5 py-3 font-semibold">Updated</th>
						<th class="px-5 py-3 text-right font-semibold">Actions</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-slate-100">
					{#each filteredItems as item (item.id)}
						<tr class="hover:bg-slate-50">
							<td class="px-5 py-4">
								<div class="flex items-center gap-3">
									<div
										class="flex h-11 w-11 shrink-0 items-center justify-center rounded-md bg-slate-100 text-sm font-semibold text-slate-700"
									>
										{productName(item).slice(0, 2).toUpperCase()}
									</div>
									<div>
										<p class="font-medium text-slate-950">{productName(item)}</p>
										<p class="font-mono text-xs text-slate-500">Product #{item.product_id}</p>
									</div>
								</div>
							</td>
							<td class="px-5 py-4 text-right font-medium tabular-nums text-slate-950">
								{formatNumber(item.on_hand_quantity)}
							</td>
							<td class="px-5 py-4 text-right tabular-nums text-slate-700">
								{formatNumber(item.reserved_quantity)}
							</td>
							<td class="px-5 py-4 text-right font-semibold tabular-nums text-slate-950">
								{formatNumber(item.available_quantity)}
							</td>
							<td class="px-5 py-4 text-right tabular-nums text-slate-700">
								{formatNumber(item.low_stock_threshold)}
							</td>
							<td class="px-5 py-4">
								{#if item.is_low_stock}
									<Badge variant="warning">Low stock</Badge>
								{:else}
									<Badge variant="success">Healthy</Badge>
								{/if}
							</td>
							<td class="px-5 py-4 text-xs text-slate-600">{formatDate(item.updated_at)}</td>
							<td class="px-5 py-4">
								<div class="flex flex-wrap justify-end gap-2">
									<Button
										variant="outline"
										size="sm"
										onclick={() => openActionModal('receive', item)}
									>
										<PlusCircle size={14} />
										Receive
									</Button>
									<Button
										variant="outline"
										size="sm"
										onclick={() => openActionModal('adjust', item)}
									>
										<MinusCircle size={14} />
										Adjust
									</Button>
									<Button variant="outline" size="sm" onclick={() => openDetailPanel(item)}>
										<Eye size={14} />
										Details
									</Button>
								</div>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		{/if}
	</div>
</Card>

{#if showActionModal}
	<div
		class="modal-backdrop"
		role="button"
		tabindex="0"
		aria-label="Close inventory action modal"
		onclick={handleBackdropClick}
		onkeydown={handleBackdropKeydown}
	>
		<div class="modal" role="dialog" aria-modal="true" aria-labelledby="inventory-action-title">
			<div class="modal-header">
				<div>
					<h2 id="inventory-action-title" class="text-lg font-semibold text-slate-950">
						{actionMode === 'receive' ? 'Receive stock' : 'Adjust stock'}
					</h2>
					<p class="mt-1 text-sm text-slate-500">
						{actionMode === 'receive'
							? 'Tambah stok masuk lewat workflow domain inventory.'
							: 'Gunakan adjustment untuk koreksi stok admin yang punya alasan jelas.'}
					</p>
				</div>
				<button class="modal-close" onclick={closeActionModal} aria-label="Close">
					<X size={18} />
				</button>
			</div>

			<form class="modal-body" onsubmit={handleActionSubmit}>
				<div class="field">
					<label for="action-product">Product <span class="required">*</span></label>
					<select id="action-product" bind:value={selectedProductId} required>
						<option value="" disabled>
							{actionMode === 'receive' ? 'Pilih product...' : 'Pilih tracked inventory...'}
						</option>
						{#each actionProductOptions as product (product.id)}
							<option value={String(product.id)}>{productLabel(product)}</option>
						{/each}
					</select>
					{#if actionMode === 'adjust' && actionProductOptions.length === 0}
						<p class="field-hint text-amber-700">
							Belum ada inventory yang bisa di-adjust. Receive stock dulu untuk membuat aggregate.
						</p>
					{/if}
				</div>

				{#if selectedInventoryItem}
					<div class="stock-snapshot">
						<div>
							<span>On hand</span>
							<strong>{formatNumber(selectedInventoryItem.on_hand_quantity)}</strong>
						</div>
						<div>
							<span>Reserved</span>
							<strong>{formatNumber(selectedInventoryItem.reserved_quantity)}</strong>
						</div>
						<div>
							<span>Available</span>
							<strong>{formatNumber(selectedInventoryItem.available_quantity)}</strong>
						</div>
					</div>
				{/if}

				<div class="field">
					<label for="action-quantity">
						{actionMode === 'receive' ? 'Quantity received' : 'Adjustment delta'}
						<span class="required">*</span>
					</label>
					<input
						id="action-quantity"
						type="number"
						bind:value={actionQuantity}
						step="1"
						min={actionMode === 'receive' ? '1' : undefined}
						placeholder={actionMode === 'receive' ? 'e.g. 12' : 'e.g. 5 or -2'}
						required
					/>
					{#if actionMode === 'adjust'}
						<p class="field-hint">
							Gunakan angka positif untuk menambah stok atau negatif untuk mengurangi stok. Backend
							akan menolak adjustment yang membuat stok negatif atau lebih kecil dari reserved stock.
						</p>
					{/if}
				</div>

				<div class="grid gap-3 sm:grid-cols-2">
					<div class="field">
						<label for="action-reference-type">Reference type</label>
						<input
							id="action-reference-type"
							type="text"
							bind:value={actionReferenceType}
							placeholder="manual_receive"
						/>
					</div>

					<div class="field">
						<label for="action-reference-id">Reference ID</label>
						<input
							id="action-reference-id"
							type="number"
							bind:value={actionReferenceId}
							min="1"
							step="1"
							placeholder="Optional"
						/>
					</div>
				</div>

				<div class="field">
					<label for="action-notes">
						Notes / reason
						{#if actionMode === 'adjust'}
							<span class="required">*</span>
						{/if}
					</label>
					<textarea
						id="action-notes"
						bind:value={actionNotes}
						rows={3}
						placeholder={actionMode === 'receive'
							? 'Optional receiving notes...'
							: 'Wajib isi alasan adjustment...'}
						required={actionMode === 'adjust'}
					></textarea>
				</div>

				<div class="modal-footer">
					<Button type="button" variant="outline" onclick={closeActionModal} disabled={actionSubmitting}>
						Batal
					</Button>
					<Button type="submit" disabled={actionSubmitting || !canSubmitAction}>
						{#if actionSubmitting}
							<Loader2 size={16} class="animate-spin" />
						{/if}
						{actionMode === 'receive' ? 'Receive stock' : 'Apply adjustment'}
					</Button>
				</div>
			</form>
		</div>
	</div>
{/if}

{#if detailItem}
	<div
		class="detail-backdrop"
		role="button"
		tabindex="0"
		aria-label="Close inventory detail panel"
		onclick={handleDetailBackdropClick}
		onkeydown={handleDetailBackdropKeydown}
	>
		<div class="detail-panel" role="dialog" aria-modal="true" aria-labelledby="detail-title">
			<div class="detail-header">
				<div>
					<p class="text-sm font-medium text-slate-500">Inventory detail</p>
					<h2 id="detail-title" class="mt-1 text-xl font-bold text-slate-950">
						{productName(detailItem)}
					</h2>
					<p class="mt-1 font-mono text-xs text-slate-500">Product #{detailItem.product_id}</p>
				</div>
				<button class="modal-close" onclick={closeDetailPanel} aria-label="Close">
					<X size={18} />
				</button>
			</div>

			<div class="detail-body">
				<div class="stock-snapshot">
					<div>
						<span>On hand</span>
						<strong>{formatNumber(detailItem.on_hand_quantity)}</strong>
					</div>
					<div>
						<span>Reserved</span>
						<strong>{formatNumber(detailItem.reserved_quantity)}</strong>
					</div>
					<div>
						<span>Available</span>
						<strong>{formatNumber(detailItem.available_quantity)}</strong>
					</div>
				</div>

				{#if detailError}
					<div class="detail-alert">
						<AlertTriangle size={16} />
						<p>{detailError}</p>
					</div>
				{/if}

				<section class="detail-section">
					<div class="detail-section-header">
						<div>
							<h3><History size={16} /> Movement history</h3>
							<p>Audit trail for inbound, adjustment, reservation, and deduction events.</p>
						</div>
						<Button
							variant="outline"
							size="sm"
							onclick={() => detailItem && loadDetail(detailItem)}
							disabled={detailLoading}
						>
							{#if detailLoading}
								<Loader2 size={14} class="animate-spin" />
							{:else}
								<RefreshCw size={14} />
							{/if}
							Refresh
						</Button>
					</div>

					{#if detailLoading}
						<div class="detail-empty">
							<Loader2 size={18} class="animate-spin" />
							<span>Memuat movement history...</span>
						</div>
					{:else if detailMovements.length === 0}
						<div class="detail-empty">
							<Clock3 size={18} />
							<span>Belum ada movement untuk produk ini.</span>
						</div>
					{:else}
						<div class="movement-list">
							{#each detailMovements as movement (movement.id)}
								<article class="movement-card">
									<div class="flex items-start justify-between gap-3">
										<div>
											<Badge variant={movementVariant(movement.movement_type)}>
												{movementLabel(movement.movement_type)}
											</Badge>
											<p class="mt-2 text-sm font-semibold text-slate-950">
												Quantity {formatNumber(movement.quantity)}
											</p>
										</div>
										<p class="text-right text-xs text-slate-500">{formatDate(movement.created_at)}</p>
									</div>
									<div class="mt-3 grid gap-2 text-sm text-slate-600">
										<p>
											<span class="font-medium text-slate-700">Reference:</span>
											{referenceLabel(movement.reference_type, movement.reference_id)}
										</p>
										<p>
											<span class="font-medium text-slate-700">Notes:</span>
											{movement.notes ?? 'No notes'}
										</p>
									</div>
								</article>
							{/each}
						</div>
					{/if}
				</section>

				<section class="detail-section">
					<div class="detail-section-header">
						<div>
							<h3><ListChecks size={16} /> Active reservations</h3>
							<p>Open reservations currently holding available stock for orders.</p>
						</div>
					</div>

					{#if detailLoading}
						<div class="detail-empty">
							<Loader2 size={18} class="animate-spin" />
							<span>Memuat active reservations...</span>
						</div>
					{:else if detailReservations.length === 0}
						<div class="detail-empty">
							<ListChecks size={18} />
							<span>Tidak ada active reservation untuk produk ini.</span>
						</div>
					{:else}
						<div class="reservation-list">
							{#each detailReservations as reservation (reservation.id)}
								<article class="reservation-card">
									<div class="flex items-start justify-between gap-3">
										<div>
											<p class="font-semibold text-slate-950">Reservation #{reservation.id}</p>
											<p class="mt-1 text-sm text-slate-600">
												Order #{reservation.order_id}
												{#if reservation.order_item_id}
													/ Item #{reservation.order_item_id}
												{/if}
											</p>
										</div>
										<Badge variant="warning">{reservation.status}</Badge>
									</div>
									<div class="mt-3 grid grid-cols-2 gap-3 text-sm">
										<div>
											<p class="text-xs text-slate-500">Quantity</p>
											<p class="font-semibold text-slate-950">
												{formatNumber(reservation.quantity)}
											</p>
										</div>
										<div>
											<p class="text-xs text-slate-500">Expires</p>
											<p class="font-semibold text-slate-950">
												{formatOptionalDate(reservation.expires_at)}
											</p>
										</div>
									</div>
									<div class="mt-4 flex flex-wrap justify-end gap-2">
										<Button
											variant="outline"
											size="sm"
											onclick={() => openReservationConfirm('release', reservation)}
										>
											<Undo2 size={14} />
											Release
										</Button>
										<Button
											size="sm"
											onclick={() => openReservationConfirm('commit', reservation)}
										>
											<CheckCheck size={14} />
											Commit
										</Button>
									</div>
								</article>
							{/each}
						</div>
					{/if}
				</section>
			</div>
		</div>
	</div>
{/if}

{#if showReservationConfirm && selectedReservation}
	<div
		class="modal-backdrop"
		role="button"
		tabindex="0"
		aria-label="Close reservation confirmation modal"
		onclick={handleReservationBackdropClick}
		onkeydown={handleReservationBackdropKeydown}
	>
		<div
			class="modal {reservationActionMode === 'commit' ? 'modal--commit' : ''}"
			role="dialog"
			aria-modal="true"
			aria-labelledby="reservation-action-title"
		>
			<div class="modal-header">
				<div>
					<h2 id="reservation-action-title" class="text-lg font-semibold text-slate-950">
						{reservationActionLabel(reservationActionMode)}
					</h2>
					<p class="mt-1 text-sm text-slate-500">
						{reservationActionMode === 'release'
							? 'Release akan mengembalikan reserved stock menjadi available stock.'
							: 'Commit akan mengurangi reserved stock dan on-hand stock untuk fulfillment.'}
					</p>
				</div>
				<button class="modal-close" onclick={closeReservationConfirm} aria-label="Close">
					<X size={18} />
				</button>
			</div>

			<form class="modal-body" onsubmit={handleReservationActionSubmit}>
				<div class="reservation-confirm-card">
					<div>
						<p class="text-xs text-slate-500">Reservation</p>
						<p class="font-semibold text-slate-950">#{selectedReservation.id}</p>
					</div>
					<div>
						<p class="text-xs text-slate-500">Order</p>
						<p class="font-semibold text-slate-950">#{selectedReservation.order_id}</p>
					</div>
					<div>
						<p class="text-xs text-slate-500">Quantity</p>
						<p class="font-semibold text-slate-950">
							{formatNumber(selectedReservation.quantity)}
						</p>
					</div>
				</div>

				<div class="field">
					<label for="reservation-action-notes">Notes</label>
					<textarea
						id="reservation-action-notes"
						bind:value={reservationActionNotes}
						rows={3}
						placeholder="Catatan untuk audit trail..."
					></textarea>
				</div>

				<div class="detail-alert {reservationActionMode === 'commit' ? 'detail-alert--commit' : ''}">
					{#if reservationActionMode === 'release'}
						<Undo2 size={16} />
						<p>
							Konfirmasi release hanya jika order dibatalkan, payment gagal, atau stok tidak perlu
							ditahan lagi.
						</p>
					{:else}
						<CheckCheck size={16} />
						<p>
							Konfirmasi commit hanya jika barang benar-benar siap dipenuhi atau dikirim. Backend akan
							menolak jika reservation tidak aktif atau stok tidak cukup.
						</p>
					{/if}
				</div>

				<div class="modal-footer">
					<Button
						type="button"
						variant="outline"
						onclick={closeReservationConfirm}
						disabled={reservationSubmitting}
					>
						Batal
					</Button>
					<Button type="submit" disabled={reservationSubmitting}>
						{#if reservationSubmitting}
							<Loader2 size={16} class="animate-spin" />
						{/if}
						{reservationActionLabel(reservationActionMode)}
					</Button>
				</div>
			</form>
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
	.toast--success {
		background: #ecfdf5;
		color: #065f46;
		border: 1px solid #a7f3d0;
	}
	.toast--error {
		background: #fef2f2;
		color: #991b1b;
		border: 1px solid #fecaca;
	}
	@keyframes slide-in {
		from {
			transform: translateY(1rem);
			opacity: 0;
		}
		to {
			transform: translateY(0);
			opacity: 1;
		}
	}

	.modal-backdrop {
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
	@keyframes fade-in {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}

	.modal {
		background: white;
		border-radius: 0.75rem;
		box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
		width: 100%;
		max-width: 36rem;
		animation: scale-in 0.2s ease;
		overflow: hidden;
	}
	.modal--commit .modal-header {
		background: #f8fafc;
	}
	@keyframes scale-in {
		from {
			transform: scale(0.96);
			opacity: 0;
		}
		to {
			transform: scale(1);
			opacity: 1;
		}
	}

	.modal-header {
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
		transition: background 0.15s;
	}
	.modal-close:hover {
		background: #f1f5f9;
		color: #0f172a;
	}
	.modal-body {
		padding: 1.5rem;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}
	.modal-footer {
		display: flex;
		justify-content: flex-end;
		gap: 0.5rem;
		padding-top: 0.5rem;
	}

	.field {
		display: flex;
		flex-direction: column;
		gap: 0.375rem;
	}
	.field label {
		font-size: 0.875rem;
		font-weight: 500;
		color: #374151;
	}
	.required {
		color: #ef4444;
	}
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
		transition:
			border-color 0.15s,
			box-shadow 0.15s;
	}
	.field input:focus,
	.field textarea:focus,
	.field select:focus {
		border-color: #0f172a;
		box-shadow: 0 0 0 3px rgba(15, 23, 42, 0.12);
	}
	.field textarea {
		resize: vertical;
	}
	.field-hint {
		font-size: 0.75rem;
		line-height: 1.25rem;
		color: #64748b;
	}
	.stock-snapshot {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 0.75rem;
		border-radius: 0.75rem;
		border: 1px solid #e2e8f0;
		background: #f8fafc;
		padding: 0.75rem;
	}
	.stock-snapshot div {
		display: flex;
		flex-direction: column;
		gap: 0.125rem;
	}
	.stock-snapshot span {
		font-size: 0.75rem;
		color: #64748b;
	}
	.stock-snapshot strong {
		font-size: 1rem;
		color: #0f172a;
		font-variant-numeric: tabular-nums;
	}
	.detail-backdrop {
		position: fixed;
		inset: 0;
		z-index: 8500;
		display: flex;
		justify-content: flex-end;
		background: rgba(15, 23, 42, 0.32);
		backdrop-filter: blur(2px);
		animation: fade-in 0.15s ease;
	}
	.detail-panel {
		height: 100%;
		width: min(100%, 42rem);
		overflow: hidden;
		background: #ffffff;
		box-shadow: -24px 0 60px rgba(15, 23, 42, 0.22);
		animation: slide-panel 0.22s ease;
	}
	@keyframes slide-panel {
		from {
			transform: translateX(2rem);
			opacity: 0;
		}
		to {
			transform: translateX(0);
			opacity: 1;
		}
	}
	.detail-header {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 1rem;
		border-bottom: 1px solid #e2e8f0;
		padding: 1.25rem 1.5rem;
	}
	.detail-body {
		display: flex;
		height: calc(100% - 6rem);
		flex-direction: column;
		gap: 1.25rem;
		overflow-y: auto;
		padding: 1.5rem;
	}
	.detail-alert {
		display: flex;
		align-items: flex-start;
		gap: 0.5rem;
		border-radius: 0.75rem;
		border: 1px solid #fecaca;
		background: #fef2f2;
		padding: 0.75rem;
		font-size: 0.875rem;
		color: #991b1b;
	}
	.detail-alert--commit {
		border-color: #bbf7d0;
		background: #f0fdf4;
		color: #166534;
	}
	.detail-section {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}
	.detail-section-header {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 1rem;
	}
	.detail-section-header h3 {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 1rem;
		font-weight: 700;
		color: #0f172a;
	}
	.detail-section-header p {
		margin-top: 0.25rem;
		font-size: 0.875rem;
		color: #64748b;
	}
	.detail-empty {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		min-height: 5.5rem;
		border-radius: 0.75rem;
		border: 1px dashed #cbd5e1;
		background: #f8fafc;
		padding: 1rem;
		text-align: center;
		font-size: 0.875rem;
		color: #64748b;
	}
	.movement-list,
	.reservation-list {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}
	.movement-card,
	.reservation-card {
		border-radius: 0.75rem;
		border: 1px solid #e2e8f0;
		background: #ffffff;
		padding: 1rem;
	}
	.reservation-confirm-card {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 0.75rem;
		border-radius: 0.75rem;
		border: 1px solid #e2e8f0;
		background: #f8fafc;
		padding: 1rem;
	}
	@media (max-width: 640px) {
		.modal {
			max-height: calc(100vh - 2rem);
			overflow-y: auto;
		}
		.modal-footer {
			flex-direction: column-reverse;
		}
		.modal-footer :global(button) {
			width: 100%;
		}
		.stock-snapshot,
		.reservation-confirm-card {
			grid-template-columns: 1fr;
		}
		.detail-panel {
			width: 100%;
		}
		.detail-section-header {
			flex-direction: column;
		}
	}
</style>
