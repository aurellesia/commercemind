<script lang="ts">
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import {
		Eye,
		Loader2,
		MapPin,
		Plus,
		RefreshCw,
		Save,
		Search,
		ShoppingBag,
		TriangleAlert,
		UserRound,
		UsersRound,
		X
	} from 'lucide-svelte';
	import { Badge } from '$lib/components/ui/badge';
	import { Button } from '$lib/components/ui/button';
	import { Card } from '$lib/components/ui/card';
	import { Input } from '$lib/components/ui/input';
	import {
		customersApi,
		type CustomerAddress,
		type CustomerAddressCreate,
		type CustomerDetail,
		type CustomerFilterType,
		type CustomerSummary
	} from '$lib/api/customers';
	import {
		getPublicStorefrontConfig,
		type PublicStorefrontConfig
	} from '$lib/api/storefront-config';

	let config = $state<PublicStorefrontConfig | null>(null);
	let customers = $state<CustomerSummary[]>([]);
	let selectedCustomer = $state<CustomerDetail | null>(null);
	let loading = $state(true);
	let detailLoading = $state(false);
	let savingProfile = $state(false);
	let savingAddress = $state(false);
	let error = $state<string | null>(null);
	let detailError = $state<string | null>(null);
	let success = $state<string | null>(null);
	let search = $state('');
	let customerType = $state<CustomerFilterType>('all');

	let profileName = $state('');
	let profilePhone = $state('');
	let profileEmail = $state('');

	let editingAddressId = $state<number | null>(null);
	let addressRecipientName = $state('');
	let addressPhone = $state('');
	let addressLine = $state('');
	let addressDistrict = $state('');
	let addressCity = $state('');
	let addressProvince = $state('');
	let addressPostalCode = $state('');
	let addressNotes = $state('');
	let addressIsDefault = $state(false);

	const brandSlug = $derived(page.params.brandSlug ?? 'default');
	const totalCustomers = $derived(customers.length);
	const guestCustomers = $derived(
		customers.filter((customer) => customer.customer_type === 'guest').length
	);
	const registeredCustomers = $derived(
		customers.filter((customer) => customer.customer_type === 'registered').length
	);
	const totalOrders = $derived(
		customers.reduce((sum, customer) => sum + customer.total_orders, 0)
	);
	const stats = $derived([
		{ label: 'Total customers', value: totalCustomers, icon: UsersRound },
		{ label: 'Guest customers', value: guestCustomers, icon: UserRound },
		{ label: 'Registered customers', value: registeredCustomers, icon: UserRound },
		{ label: 'Customer orders', value: totalOrders, icon: ShoppingBag }
	]);
	const typeFilters: { label: string; value: CustomerFilterType }[] = [
		{ label: 'All', value: 'all' },
		{ label: 'Guest', value: 'guest' },
		{ label: 'Registered', value: 'registered' }
	];
	const filteredCustomers = $derived(
		customers.filter((customer) => {
			const normalizedSearch = search.trim().toLowerCase();
			const matchesSearch =
				!normalizedSearch ||
				customer.name.toLowerCase().includes(normalizedSearch) ||
				(customer.email ?? '').toLowerCase().includes(normalizedSearch) ||
				(customer.phone ?? '').toLowerCase().includes(normalizedSearch);
			const matchesType = customerType === 'all' || customer.customer_type === customerType;
			return matchesSearch && matchesType;
		})
	);

	async function loadCustomers() {
		loading = true;
		error = null;
		try {
			config = await getPublicStorefrontConfig(brandSlug);
			customers = await customersApi.summary(config.brand_id);
		} catch (e) {
			error = (e as Error).message;
			customers = [];
		} finally {
			loading = false;
		}
	}

	async function openCustomer(customerId: number) {
		if (!config) return;
		detailLoading = true;
		detailError = null;
		success = null;
		selectedCustomer = null;
		try {
			selectedCustomer = await customersApi.detail(customerId, config.brand_id);
			profileName = selectedCustomer.name;
			profilePhone = selectedCustomer.phone ?? '';
			profileEmail = selectedCustomer.email ?? '';
			resetAddressForm();
		} catch (e) {
			detailError = (e as Error).message;
		} finally {
			detailLoading = false;
		}
	}

	function closeCustomerDrawer() {
		selectedCustomer = null;
		detailLoading = false;
		detailError = null;
		success = null;
		resetAddressForm();
	}

	async function saveProfile() {
		if (!config || !selectedCustomer) return;
		savingProfile = true;
		detailError = null;
		success = null;
		try {
			await customersApi.update(selectedCustomer.id, config.brand_id, {
				name: profileName,
				phone: emptyToNull(profilePhone),
				email: emptyToNull(profileEmail)
			});
			await openCustomer(selectedCustomer.id);
			await loadCustomers();
			success = 'Customer profile tersimpan.';
		} catch (e) {
			detailError = (e as Error).message;
		} finally {
			savingProfile = false;
		}
	}

	async function saveAddress() {
		if (!config || !selectedCustomer) return;
		savingAddress = true;
		detailError = null;
		success = null;
		try {
			const payload: CustomerAddressCreate = {
				recipient_name: addressRecipientName,
				phone: addressPhone,
				address_line: addressLine,
				district: addressDistrict,
				city: addressCity,
				province: addressProvince,
				postal_code: addressPostalCode,
				notes: emptyToNull(addressNotes),
				is_default: addressIsDefault
			};
			if (editingAddressId) {
				await customersApi.updateAddress(editingAddressId, config.brand_id, payload);
			} else {
				await customersApi.createAddress(selectedCustomer.id, config.brand_id, payload);
			}
			await openCustomer(selectedCustomer.id);
			success = editingAddressId ? 'Alamat customer diperbarui.' : 'Alamat customer ditambahkan.';
		} catch (e) {
			detailError = (e as Error).message;
		} finally {
			savingAddress = false;
		}
	}

	function editAddress(address: CustomerAddress) {
		editingAddressId = address.id;
		addressRecipientName = address.recipient_name;
		addressPhone = address.phone;
		addressLine = address.address_line;
		addressDistrict = address.district;
		addressCity = address.city;
		addressProvince = address.province;
		addressPostalCode = address.postal_code;
		addressNotes = address.notes ?? '';
		addressIsDefault = address.is_default;
	}

	function resetAddressForm() {
		editingAddressId = null;
		addressRecipientName = selectedCustomer?.name ?? '';
		addressPhone = selectedCustomer?.phone ?? '';
		addressLine = '';
		addressDistrict = '';
		addressCity = '';
		addressProvince = '';
		addressPostalCode = '';
		addressNotes = '';
		addressIsDefault = selectedCustomer?.addresses.length === 0;
	}

	function emptyToNull(value: string): string | null {
		const trimmed = value.trim();
		return trimmed ? trimmed : null;
	}

	function formatDate(value: string | null): string {
		if (!value) return '-';
		return new Intl.DateTimeFormat('id-ID', { dateStyle: 'medium' }).format(new Date(value));
	}

	function formatMoney(value: string): string {
		return new Intl.NumberFormat('id-ID', {
			style: 'currency',
			currency: 'IDR',
			minimumFractionDigits: 0
		}).format(Number(value));
	}

	function initials(name: string): string {
		return name
			.split(' ')
			.filter(Boolean)
			.slice(0, 2)
			.map((part) => part[0]?.toUpperCase())
			.join('');
	}

	onMount(loadCustomers);
</script>

<section class="mb-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
	<div>
		<p class="text-sm font-medium text-slate-500">Customers</p>
		<h1 class="mt-1 text-3xl font-bold tracking-tight text-slate-950">
			Customer directory
		</h1>
		<p class="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
			Manage guest and registered customers for {config?.brand_name ?? brandSlug}.
		</p>
	</div>

	<div class="flex flex-wrap gap-2">
		<Button variant="outline" onclick={loadCustomers} disabled={loading}>
			{#if loading}
				<Loader2 size={16} class="animate-spin" />
			{:else}
				<RefreshCw size={16} />
			{/if}
			Refresh
		</Button>
	</div>
</section>

<section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4" aria-label="Customer summary">
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
	<div
		class="flex flex-col gap-4 border-b border-slate-200 p-5 xl:flex-row xl:items-center xl:justify-between"
	>
		<div>
			<h2 class="text-base font-semibold">Customer list</h2>
			<p class="text-sm text-slate-500">Data is scoped to the active brand: {brandSlug}.</p>
		</div>

		<div class="flex w-full flex-col gap-2 lg:flex-row xl:w-auto">
			<div class="relative min-w-0 flex-1 xl:w-80">
				<Search class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
				<Input class="pl-9" placeholder="Search name, phone, or email" bind:value={search} aria-label="Search customers" />
			</div>

			<div class="inline-flex rounded-md border border-slate-200 bg-white p-1">
				{#each typeFilters as filter}
					<button
						type="button"
						class="rounded px-3 py-1.5 text-sm font-medium transition-colors {customerType ===
						filter.value
							? 'bg-slate-950 text-white'
							: 'text-slate-600 hover:bg-slate-100 hover:text-slate-950'}"
						onclick={() => (customerType = filter.value)}
					>
						{filter.label}
					</button>
				{/each}
			</div>
			{#if search}
				<Button
					type="button"
					variant="ghost"
					onclick={() => {
						search = '';
					}}>Reset</Button
				>
			{/if}
		</div>
	</div>

	<div class="overflow-x-auto">
		{#if loading}
			<div class="flex items-center justify-center gap-3 py-16 text-slate-500">
				<Loader2 size={20} class="animate-spin" />
				<span>Loading customers...</span>
			</div>
		{:else if error}
			<div class="flex flex-col items-center justify-center gap-3 py-16 text-red-600">
				<TriangleAlert size={32} />
				<p class="font-medium">Could not load customers</p>
				<p class="max-w-sm text-center text-sm text-slate-500">{error}</p>
				<Button variant="outline" onclick={loadCustomers}>Try again</Button>
			</div>
		{:else if filteredCustomers.length === 0}
			<div class="flex flex-col items-center justify-center gap-2 py-16 text-slate-500">
				<UsersRound size={28} />
				<p class="font-medium">
					{search || customerType !== 'all' ? 'No customers match this filter.' : 'No customers yet.'}
				</p>
			</div>
		{:else}
			<table class="w-full text-left text-sm">
				<thead class="bg-slate-50 text-xs uppercase text-slate-500">
					<tr>
						<th class="px-5 py-3 font-semibold">Customer</th>
						<th class="px-5 py-3 font-semibold">Type</th>
						<th class="px-5 py-3 font-semibold">Phone</th>
						<th class="px-5 py-3 font-semibold">Orders</th>
						<th class="px-5 py-3 font-semibold">Total spent</th>
						<th class="px-5 py-3 font-semibold">Last order</th>
						<th class="px-5 py-3 font-semibold">Created</th>
						<th class="px-5 py-3 text-right font-semibold">Actions</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-slate-100">
					{#each filteredCustomers as customer (customer.id)}
						<tr class="hover:bg-slate-50">
							<td class="px-5 py-4">
								<div class="flex items-center gap-3">
									<div class="customer-thumb">
										{initials(customer.name) || 'C'}
									</div>
									<div>
										<p class="font-medium text-slate-950">{customer.name}</p>
										<p class="text-xs text-slate-500">{customer.email ?? 'Email not set'}</p>
									</div>
								</div>
							</td>
							<td class="px-5 py-4">
								<Badge variant={customer.customer_type === 'registered' ? 'success' : 'secondary'}>
									{customer.customer_type}
								</Badge>
							</td>
							<td class="px-5 py-4 text-slate-600">{customer.phone ?? 'Not set'}</td>
							<td class="px-5 py-4 tabular-nums text-slate-600">{customer.total_orders}</td>
							<td class="px-5 py-4 font-medium tabular-nums text-slate-950">{formatMoney(customer.total_spent)}</td>
							<td class="px-5 py-4 text-xs text-slate-600">{formatDate(customer.last_order_date)}</td>
							<td class="px-5 py-4 text-xs text-slate-600">{formatDate(customer.created_at)}</td>
							<td class="px-5 py-4">
								<div class="flex justify-end">
									<Button variant="ghost" size="icon" aria-label="View {customer.name}" onclick={() => openCustomer(customer.id)}>
										<Eye size={16} />
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

{#if detailLoading || selectedCustomer}
	<div
		class="drawer-backdrop"
		role="presentation"
		onclick={(event) => {
			if (event.target === event.currentTarget) closeCustomerDrawer();
		}}
	>
		<aside class="detail-drawer" aria-label="Customer detail drawer">
			<div class="drawer-header">
				<div>
					<p class="text-xs font-bold uppercase text-slate-500">Customer</p>
					<h2 class="mt-1 text-lg font-bold text-slate-950">
						{selectedCustomer?.name ?? 'Loading detail...'}
					</h2>
				</div>
				<button class="drawer-close" type="button" aria-label="Close customer detail" onclick={closeCustomerDrawer}>
					<X size={18} />
				</button>
			</div>

		{#if detailLoading}
			<div class="state-row"><Loader2 size={18} class="spin" /> Loading detail...</div>
		{:else if !selectedCustomer}
			<div class="state-row"><UserRound size={18} /> Select a customer to view details.</div>
		{:else}
			<section class="detail-section">
				<div class="flex items-start justify-between gap-3">
					<div>
						<p class="text-xs font-bold uppercase text-slate-500">Customer Detail</p>
						<h2 class="mt-1 text-xl font-bold text-slate-950">{selectedCustomer.name}</h2>
						<p class="mt-1 text-sm text-slate-500">{selectedCustomer.customer_type}</p>
					</div>
					<Badge variant={selectedCustomer.customer_type === 'registered' ? 'success' : 'secondary'}>
						{selectedCustomer.customer_type}
					</Badge>
				</div>

				<form
					class="mt-5 grid gap-3"
					onsubmit={(event) => {
						event.preventDefault();
						saveProfile();
					}}
				>
					<label class="field">Name <input bind:value={profileName} required /></label>
					<label class="field">Phone <input bind:value={profilePhone} /></label>
					<label class="field">Email <input bind:value={profileEmail} type="email" /></label>
					<Button class="w-full" disabled={savingProfile} type="submit">
						<Save size={15} />
						{savingProfile ? 'Saving...' : 'Save profile'}
					</Button>
				</form>
			</section>

			<section class="detail-section">
				<div class="flex items-center justify-between gap-3">
					<h3 class="font-bold text-slate-950">Addresses</h3>
					<Button variant="outline" size="sm" type="button" onclick={resetAddressForm}>
						<Plus size={15} />
						New
					</Button>
				</div>

				<div class="mt-3 grid gap-3">
					{#if selectedCustomer.addresses.length === 0}
						<p class="rounded-md border border-dashed border-slate-300 p-3 text-sm text-slate-500">
							No addresses yet.
						</p>
					{:else}
						{#each selectedCustomer.addresses as address}
							<button class="address-row" type="button" onclick={() => editAddress(address)}>
								<MapPin size={16} />
								<span>
									<strong>{address.recipient_name}</strong>
									<small>{address.address_line}, {address.city}</small>
									{#if address.is_default}<em>Default</em>{/if}
								</span>
							</button>
						{/each}
					{/if}
				</div>

				<form
					class="mt-4 grid gap-3"
					onsubmit={(event) => {
						event.preventDefault();
						saveAddress();
					}}
				>
					<p class="text-sm font-semibold text-slate-700">
						{editingAddressId ? 'Edit address' : 'Add address'}
					</p>
					<label class="field">Recipient <input bind:value={addressRecipientName} required /></label>
					<label class="field">Phone <input bind:value={addressPhone} required /></label>
					<label class="field">Address <textarea bind:value={addressLine} required></textarea></label>
					<div class="grid gap-3 sm:grid-cols-2">
						<label class="field">District <input bind:value={addressDistrict} required /></label>
						<label class="field">City <input bind:value={addressCity} required /></label>
						<label class="field">Province <input bind:value={addressProvince} required /></label>
						<label class="field">Postal code <input bind:value={addressPostalCode} required /></label>
					</div>
					<label class="field">Notes <textarea bind:value={addressNotes}></textarea></label>
					<label class="checkbox-row">
						<input type="checkbox" bind:checked={addressIsDefault} />
						Default address
					</label>
					<Button class="w-full" disabled={savingAddress} type="submit">
						<Save size={15} />
						{savingAddress ? 'Saving...' : editingAddressId ? 'Update address' : 'Add address'}
					</Button>
				</form>
			</section>

			<section class="detail-section">
				<h3 class="font-bold text-slate-950">Order History</h3>
				<div class="mt-3 grid gap-2">
					{#if selectedCustomer.recent_orders.length === 0}
						<p class="rounded-md border border-dashed border-slate-300 p-3 text-sm text-slate-500">
							No orders yet.
						</p>
					{:else}
						{#each selectedCustomer.recent_orders as order}
							<div class="order-row">
								<div>
									<strong>Order #{order.id}</strong>
									<small>{formatDate(order.created_at)} · {order.status}</small>
								</div>
								<span>{formatMoney(order.total_amount)}</span>
							</div>
						{/each}
					{/if}
				</div>
			</section>

			{#if detailError}
				<p class="message message--error">{detailError}</p>
			{/if}
			{#if success}
				<p class="message message--success">{success}</p>
			{/if}
		{/if}
	</aside>
	</div>
{/if}

<style>
	.field {
		display: grid;
		gap: 0.4rem;
		color: #475569;
		font-size: 0.78rem;
		font-weight: 800;
		text-transform: uppercase;
	}
	input,
	textarea {
		width: 100%;
		border: 1px solid #cbd5e1;
		border-radius: 8px;
		background: white;
		color: #0f172a;
		padding: 0.65rem 0.75rem;
		font-size: 0.9rem;
		font-weight: 600;
		outline: none;
		text-transform: none;
	}
	textarea {
		min-height: 5rem;
		resize: vertical;
	}
	input:focus,
	textarea:focus {
		border-color: #0f172a;
	}
	.customer-thumb {
		display: flex;
		width: 3rem;
		height: 3rem;
		flex-shrink: 0;
		align-items: center;
		justify-content: center;
		border-radius: 0.625rem;
		background: #f1f5f9;
		color: #334155;
		font-size: 0.875rem;
		font-weight: 900;
	}
	.state-row {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.6rem;
		min-height: 12rem;
		color: #64748b;
	}
	.state-row :global(.spin) {
		animation: spin 1s linear infinite;
	}
	.drawer-backdrop {
		position: fixed;
		inset: 0;
		z-index: 60;
		display: flex;
		justify-content: flex-end;
		background: rgb(15 23 42 / 0.34);
	}
	.detail-drawer {
		display: grid;
		width: min(100vw, 520px);
		max-width: 100%;
		height: 100vh;
		align-content: start;
		gap: 1rem;
		overflow-y: auto;
		border-left: 1px solid #e2e8f0;
		background: #f8fafc;
		padding: 1rem;
		box-shadow: -18px 0 45px rgb(15 23 42 / 0.16);
	}
	.drawer-header {
		position: sticky;
		top: -1rem;
		z-index: 1;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		border-bottom: 1px solid #e2e8f0;
		background: #f8fafc;
		padding: 1rem 0;
	}
	.drawer-close {
		display: inline-flex;
		width: 2.25rem;
		height: 2.25rem;
		align-items: center;
		justify-content: center;
		border: 1px solid #cbd5e1;
		border-radius: 8px;
		background: white;
		color: #334155;
	}
	.detail-section {
		border: 1px solid #e2e8f0;
		border-radius: 8px;
		background: white;
		padding: 1rem;
	}
	.address-row {
		display: flex;
		align-items: flex-start;
		gap: 0.65rem;
		border: 1px solid #e2e8f0;
		border-radius: 8px;
		background: #f8fafc;
		padding: 0.8rem;
		text-align: left;
	}
	.address-row strong,
	.address-row small,
	.address-row em {
		display: block;
	}
	.address-row small {
		margin-top: 0.2rem;
		color: #64748b;
	}
	.address-row em {
		margin-top: 0.35rem;
		color: #047857;
		font-size: 0.75rem;
		font-style: normal;
		font-weight: 900;
	}
	.checkbox-row {
		display: flex;
		align-items: center;
		gap: 0.55rem;
		color: #475569;
		font-size: 0.9rem;
		font-weight: 800;
	}
	.checkbox-row input {
		width: 1rem;
	}
	.order-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		border: 1px solid #e2e8f0;
		border-radius: 8px;
		padding: 0.75rem;
	}
	.order-row strong,
	.order-row small {
		display: block;
	}
	.order-row small {
		margin-top: 0.15rem;
		color: #64748b;
	}
	.order-row span {
		font-weight: 900;
	}
	.message {
		border-radius: 8px;
		padding: 0.8rem;
		font-size: 0.9rem;
		font-weight: 800;
	}
	.message--error {
		border: 1px solid #fecaca;
		background: #fef2f2;
		color: #b91c1c;
	}
	.message--success {
		border: 1px solid #bbf7d0;
		background: #f0fdf4;
		color: #047857;
	}
	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>
