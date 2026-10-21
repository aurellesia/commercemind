<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { platformSettingsApi, type Brand, type PlatformSettings } from '$lib/api/platform-settings';

	let brands = $state<Brand[]>([]);
	let selectedBrandId = $state<number | null>(null);
	let settings = $state<PlatformSettings | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);

	async function loadInitial() {
		loading = true;
		error = null;
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
		settings = await platformSettingsApi.getBrandSettings(brandId);
	}

	async function changeBrand(value: string) {
		const brandId = Number(value);
		if (!brandId) return;
		selectedBrandId = brandId;
		loading = true;
		try {
			await loadSettings(brandId);
			await goto(`/console/settings?brandId=${brandId}`, { replaceState: true, noScroll: true });
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	onMount(loadInitial);
</script>

<section class="space-y-2">
	<p class="text-sm font-semibold uppercase text-emerald-300">Settings</p>
	<h1 class="text-3xl font-bold tracking-tight text-zinc-50">Brand settings overview</h1>
	<p class="max-w-3xl text-zinc-400">
		Settings foundation dipisah menjadi brand, storefront, SEO, module, dan system settings per brand.
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
</section>

{#if loading}
	<div class="mt-8 rounded-lg border border-zinc-800 bg-zinc-900 p-5 text-zinc-300">Memuat settings...</div>
{:else if error}
	<div class="mt-8 rounded-lg border border-red-900 bg-red-950/40 p-5 text-red-200">{error}</div>
{:else if !selectedBrandId}
	<div class="mt-8 rounded-lg border border-zinc-800 bg-zinc-900 p-5 text-zinc-300">Belum ada brand.</div>
{:else if settings}
	<div class="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
		<a class="rounded-lg border border-zinc-800 bg-zinc-900 p-5 hover:border-emerald-300" href={`/console/storefront?brandId=${selectedBrandId}`}>
			<h2 class="font-semibold text-zinc-100">Brand & Storefront</h2>
			<p class="mt-2 text-sm leading-6 text-zinc-400">{settings.brand.brand_name}</p>
			<p class="mt-1 text-sm leading-6 text-zinc-500">{settings.storefront.homepage_headline}</p>
		</a>
		<a class="rounded-lg border border-zinc-800 bg-zinc-900 p-5 hover:border-emerald-300" href={`/console/storefront?brandId=${selectedBrandId}`}>
			<h2 class="font-semibold text-zinc-100">SEO Settings</h2>
			<p class="mt-2 text-sm leading-6 text-zinc-400">{settings.seo.site_url}</p>
			<p class="mt-1 text-sm leading-6 text-zinc-500">{settings.seo.default_title}</p>
		</a>
		<a class="rounded-lg border border-zinc-800 bg-zinc-900 p-5 hover:border-emerald-300" href={`/console/modules?brandId=${selectedBrandId}`}>
			<h2 class="font-semibold text-zinc-100">Module Settings</h2>
			<p class="mt-2 text-sm leading-6 text-zinc-400">Cart: {settings.modules.cart_enabled ? 'enabled' : 'disabled'}</p>
			<p class="mt-1 text-sm leading-6 text-zinc-500">Checkout: {settings.modules.guest_checkout_enabled ? 'enabled' : 'disabled'}</p>
		</a>
		<a class="rounded-lg border border-zinc-800 bg-zinc-900 p-5 hover:border-emerald-300" href={`/console/system?brandId=${selectedBrandId}`}>
			<h2 class="font-semibold text-zinc-100">System Settings</h2>
			<p class="mt-2 text-sm leading-6 text-zinc-400">Public catalog: {settings.system.public_catalog_enabled ? 'enabled' : 'disabled'}</p>
			<p class="mt-1 text-sm leading-6 text-zinc-500">Maintenance: {settings.system.maintenance_mode ? 'enabled' : 'disabled'}</p>
		</a>
		<a class="rounded-lg border border-zinc-800 bg-zinc-900 p-5 hover:border-emerald-300" href={`/console/brands/${selectedBrandId}`}>
			<h2 class="font-semibold text-zinc-100">Tenant Brand</h2>
			<p class="mt-2 text-sm leading-6 text-zinc-400">{settings.tenant_brand.name}</p>
			<p class="mt-1 text-sm leading-6 text-zinc-500">/{settings.tenant_brand.slug}</p>
		</a>
	</div>
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
</style>
