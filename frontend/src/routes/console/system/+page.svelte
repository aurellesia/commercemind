<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { Save } from 'lucide-svelte';
	import {
		platformSettingsApi,
		type Brand,
		type PlatformSettings,
		type SystemSettingsUpdate
	} from '$lib/api/platform-settings';

	let brands = $state<Brand[]>([]);
	let selectedBrandId = $state<number | null>(null);
	let settings = $state<PlatformSettings | null>(null);
	let maintenanceMode = $state(false);
	let testMode = $state(true);
	let publicCatalogEnabled = $state(true);
	let allowCheckout = $state(false);
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
		maintenanceMode = settings.system.maintenance_mode;
		testMode = settings.system.test_mode;
		publicCatalogEnabled = settings.system.public_catalog_enabled;
		allowCheckout = settings.system.allow_checkout;
	}

	async function changeBrand(value: string) {
		const brandId = Number(value);
		if (!brandId) return;
		selectedBrandId = brandId;
		loading = true;
		try {
			await loadSettings(brandId);
			await goto(`/console/system?brandId=${brandId}`, { replaceState: true, noScroll: true });
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
			const payload: SystemSettingsUpdate = {
				maintenance_mode: maintenanceMode,
				test_mode: testMode,
				public_catalog_enabled: publicCatalogEnabled,
				allow_checkout: allowCheckout
			};
			await platformSettingsApi.updateBrandScopedSystem(selectedBrandId, payload);
			await loadSettings(selectedBrandId);
			success = 'System settings tersimpan untuk brand ini.';
		} catch (e) {
			error = (e as Error).message;
		} finally {
			saving = false;
		}
	}

	onMount(loadInitial);
</script>

<section class="space-y-2">
	<p class="text-sm font-semibold uppercase text-emerald-300">System</p>
	<h1 class="text-3xl font-bold tracking-tight text-zinc-50">System controls</h1>
	<p class="max-w-3xl text-zinc-400">
		Maintenance mode, test mode, public catalog, dan checkout availability adalah kontrol platform per brand.
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
		<p class="mt-3 text-sm text-zinc-400">Editing system controls for {settings.tenant_brand.name}.</p>
	{/if}
</section>

{#if loading}
	<div class="mt-8 rounded-lg border border-zinc-800 bg-zinc-900 p-5 text-zinc-300">Memuat system settings...</div>
{:else if !selectedBrandId}
	<div class="mt-8 rounded-lg border border-zinc-800 bg-zinc-900 p-5 text-zinc-300">Belum ada brand.</div>
{:else}
	<form class="mt-8 space-y-5" onsubmit={(event) => { event.preventDefault(); saveSettings(); }}>
		<div class="grid gap-4 md:grid-cols-2">
			<label class="setting-card">
				<input type="checkbox" bind:checked={maintenanceMode} />
				<span>
					<span>Maintenance mode</span>
					<small>Storefront brand ini akan menampilkan maintenance/coming soon.</small>
				</span>
			</label>
			<label class="setting-card">
				<input type="checkbox" bind:checked={testMode} />
				<span>
					<span>Test mode</span>
					<small>Menandai brand ini sebagai environment test/operator.</small>
				</span>
			</label>
			<label class="setting-card">
				<input type="checkbox" bind:checked={publicCatalogEnabled} />
				<span>
					<span>Public catalog enabled</span>
					<small>Mengizinkan storefront public brand ini menampilkan catalog produk.</small>
				</span>
			</label>
			<label class="setting-card">
				<input type="checkbox" bind:checked={allowCheckout} />
				<span>
					<span>Allow checkout</span>
					<small>Checkout tetap belum aktif penuh sampai cart/checkout module selesai.</small>
				</span>
			</label>
		</div>

		{#if error}<p class="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-200">{error}</p>{/if}
		{#if success}<p class="rounded-lg border border-emerald-900 bg-emerald-950/40 p-3 text-sm text-emerald-200">{success}</p>{/if}

		<button class="save-button" disabled={saving} type="submit">
			<Save size={16} />
			{saving ? 'Menyimpan...' : 'Simpan System Settings'}
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
	.setting-card {
		display: flex;
		gap: 0.9rem;
		border: 1px solid #27272a;
		border-radius: 8px;
		background: #18181b;
		padding: 1.25rem;
	}
	input {
		margin-top: 0.25rem;
		width: 1rem;
		height: 1rem;
	}
	.setting-card span span {
		display: block;
		color: #f4f4f5;
		font-weight: 800;
	}
	.setting-card small {
		display: block;
		margin-top: 0.35rem;
		color: #a1a1aa;
		line-height: 1.55;
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
