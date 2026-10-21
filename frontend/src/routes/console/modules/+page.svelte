<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { Save } from 'lucide-svelte';
	import {
		platformSettingsApi,
		type Brand,
		type ModuleSettingsUpdate,
		type PlatformSettings
	} from '$lib/api/platform-settings';

	type ModuleFlagKey =
		| 'products_enabled'
		| 'inventory_enabled'
		| 'cart_enabled'
		| 'guest_checkout_enabled'
		| 'customer_accounts_enabled'
		| 'payments_enabled'
		| 'shipping_enabled'
		| 'reports_enabled';

	const moduleItems: readonly [ModuleFlagKey, string, string][] = [
		['products_enabled', 'Products', 'Public and admin product catalog'],
		['inventory_enabled', 'Inventory', 'Stock, reservations, and availability'],
		['cart_enabled', 'Cart', 'Customer cart module'],
		['guest_checkout_enabled', 'Guest Checkout', 'Checkout without customer account'],
		['customer_accounts_enabled', 'Customer Accounts', 'Registered customer account area'],
		['payments_enabled', 'Payments', 'Payment records and future gateway hooks'],
		['shipping_enabled', 'Shipping', 'Shipping method and fulfillment options'],
		['reports_enabled', 'Reports', 'Merchant reporting screens']
	];

	let brands = $state<Brand[]>([]);
	let selectedBrandId = $state<number | null>(null);
	let settings = $state<PlatformSettings | null>(null);
	let values = $state<Record<ModuleFlagKey, boolean>>({
		products_enabled: true,
		inventory_enabled: true,
		cart_enabled: false,
		guest_checkout_enabled: false,
		customer_accounts_enabled: false,
		payments_enabled: true,
		shipping_enabled: false,
		reports_enabled: true
	});
	let loading = $state(true);
	let saving = $state(false);
	let error = $state<string | null>(null);
	let success = $state<string | null>(null);

	async function loadInitial() {
		loading = true;
		error = null;
		success = null;
		try {
			brands = await platformSettingsApi.listBrands();
			const queryBrandId = Number(page.url.searchParams.get('brandId'));
			selectedBrandId = brands.some((brand) => brand.id === queryBrandId)
				? queryBrandId
				: brands[0]?.id ?? null;
			if (selectedBrandId) await loadSettings(selectedBrandId);
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	async function loadSettings(brandId: number) {
		error = null;
		success = null;
		settings = await platformSettingsApi.getBrandSettings(brandId);
		values = {
			products_enabled: settings.modules.products_enabled,
			inventory_enabled: settings.modules.inventory_enabled,
			cart_enabled: settings.modules.cart_enabled,
			guest_checkout_enabled: settings.modules.guest_checkout_enabled,
			customer_accounts_enabled: settings.modules.customer_accounts_enabled,
			payments_enabled: settings.modules.payments_enabled,
			shipping_enabled: settings.modules.shipping_enabled,
			reports_enabled: settings.modules.reports_enabled
		};
	}

	async function changeBrand(value: string) {
		const brandId = Number(value);
		if (!brandId) return;
		selectedBrandId = brandId;
		loading = true;
		try {
			await loadSettings(brandId);
			await goto(`/console/modules?brandId=${brandId}`, { replaceState: true, noScroll: true });
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	async function saveSettings() {
		if (!selectedBrandId) return;
		saving = true;
		error = null;
		success = null;
		try {
			await platformSettingsApi.updateBrandScopedModules(
				selectedBrandId,
				values as ModuleSettingsUpdate
			);
			await loadSettings(selectedBrandId);
			success = 'Module settings tersimpan untuk brand ini.';
		} catch (e) {
			error = (e as Error).message;
		} finally {
			saving = false;
		}
	}

	onMount(loadInitial);
</script>

<section class="space-y-2">
	<p class="text-sm font-semibold uppercase text-emerald-300">Modules</p>
	<h1 class="text-3xl font-bold tracking-tight text-zinc-50">Module flags</h1>
	<p class="max-w-3xl text-zinc-400">
		Kontrol ketersediaan products, inventory, cart, guest checkout, customer accounts, payments, shipping, dan reports per brand.
	</p>
</section>

<section class="mt-6 rounded-lg border border-zinc-800 bg-zinc-900 p-5">
	<label class="field max-w-xl">
		Brand scope
		<select value={selectedBrandId ?? ''} onchange={(event) => changeBrand(event.currentTarget.value)}>
			{#each brands as brand}
				<option value={brand.id}>{brand.name} /{brand.slug}</option>
			{/each}
		</select>
	</label>
	{#if settings}
		<p class="mt-3 text-sm text-zinc-400">Editing module flags for {settings.tenant_brand.name}.</p>
	{/if}
</section>

{#if loading}
	<div class="mt-8 rounded-lg border border-zinc-800 bg-zinc-900 p-5 text-zinc-300">Memuat module flags...</div>
{:else if !selectedBrandId}
	<div class="mt-8 rounded-lg border border-zinc-800 bg-zinc-900 p-5 text-zinc-300">Belum ada brand.</div>
{:else}
	<form class="mt-8 space-y-5" onsubmit={(event) => { event.preventDefault(); saveSettings(); }}>
		<div class="grid gap-4 md:grid-cols-2">
			{#each moduleItems as [key, label, description]}
				<label class="rounded-lg border border-zinc-800 bg-zinc-900 p-5">
					<span class="flex items-start gap-3">
						<input type="checkbox" bind:checked={values[key]} />
						<span>
							<span class="block font-semibold text-zinc-100">{label}</span>
							<span class="mt-1 block text-sm leading-6 text-zinc-400">{description}</span>
						</span>
					</span>
				</label>
			{/each}
		</div>

		{#if error}<p class="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-200">{error}</p>{/if}
		{#if success}<p class="rounded-lg border border-emerald-900 bg-emerald-950/40 p-3 text-sm text-emerald-200">{success}</p>{/if}

		<button class="save-button" disabled={saving} type="submit">
			<Save size={16} />
			{saving ? 'Menyimpan...' : 'Simpan Module Flags'}
		</button>
	</form>
{/if}

<style>
	.field {
		display: grid;
		gap: 0.45rem;
		color: #d4d4d8;
		font-size: 0.875rem;
		font-weight: 700;
	}
	select {
		width: 100%;
		border: 1px solid #3f3f46;
		border-radius: 8px;
		background: #18181b;
		color: #fafafa;
		padding: 0.7rem 0.8rem;
		font-weight: 500;
		outline: none;
	}
	input {
		margin-top: 0.25rem;
		width: 1rem;
		height: 1rem;
	}
	.save-button {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		border-radius: 8px;
		background: #34d399;
		color: #052e1b;
		padding: 0.7rem 1rem;
		font-weight: 900;
	}
	.save-button:disabled {
		opacity: 0.65;
	}
</style>
