<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { Save } from 'lucide-svelte';
	import {
		platformSettingsApi,
		type Brand,
		type BrandSettingsUpdate,
		type PlatformSettings,
		type SeoSettingsUpdate,
		type StorefrontSettingsUpdate
	} from '$lib/api/platform-settings';

	let brands = $state<Brand[]>([]);
	let selectedBrandId = $state<number | null>(null);
	let settings = $state<PlatformSettings | null>(null);
	let loading = $state(true);
	let saving = $state(false);
	let error = $state<string | null>(null);
	let success = $state<string | null>(null);

	let brandName = $state('');
	let tagline = $state('');
	let logoUrl = $state('');
	let contactWhatsapp = $state('');
	let supportEmail = $state('');
	let businessAddress = $state('');
	let storefrontEnabled = $state(true);
	let homepageHeadline = $state('');
	let homepageDescription = $state('');
	let featuredProductLimit = $state(3);
	let showOutOfStockProducts = $state(true);
	let showSku = $state(true);
	let siteUrl = $state('');
	let defaultTitle = $state('');
	let defaultDescription = $state('');
	let socialImageUrl = $state('');

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
		brandName = settings.brand.brand_name;
		tagline = settings.brand.tagline ?? '';
		logoUrl = settings.brand.logo_url ?? '';
		contactWhatsapp = settings.brand.contact_whatsapp ?? '';
		supportEmail = settings.brand.support_email ?? '';
		businessAddress = settings.brand.business_address ?? '';
		storefrontEnabled = settings.storefront.storefront_enabled;
		homepageHeadline = settings.storefront.homepage_headline;
		homepageDescription = settings.storefront.homepage_description ?? '';
		featuredProductLimit = settings.storefront.featured_product_limit;
		showOutOfStockProducts = settings.storefront.show_out_of_stock_products;
		showSku = settings.storefront.show_sku;
		siteUrl = settings.seo.site_url;
		defaultTitle = settings.seo.default_title;
		defaultDescription = settings.seo.default_description ?? '';
		socialImageUrl = settings.seo.social_image_url ?? '';
	}

	async function changeBrand(value: string) {
		const brandId = Number(value);
		if (!brandId) return;
		selectedBrandId = brandId;
		loading = true;
		try {
			await loadSettings(brandId);
			await goto(`/console/storefront?brandId=${brandId}`, { replaceState: true, noScroll: true });
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
			const brand: BrandSettingsUpdate = {
				brand_name: brandName,
				tagline: nullable(tagline),
				logo_url: nullable(logoUrl),
				contact_whatsapp: nullable(contactWhatsapp),
				support_email: nullable(supportEmail),
				business_address: nullable(businessAddress)
			};
			const storefront: StorefrontSettingsUpdate = {
				storefront_enabled: storefrontEnabled,
				homepage_headline: homepageHeadline,
				homepage_description: nullable(homepageDescription),
				featured_product_limit: Number(featuredProductLimit),
				show_out_of_stock_products: showOutOfStockProducts,
				show_sku: showSku
			};
			const seo: SeoSettingsUpdate = {
				site_url: siteUrl,
				default_title: defaultTitle,
				default_description: nullable(defaultDescription),
				social_image_url: nullable(socialImageUrl)
			};
			await Promise.all([
				platformSettingsApi.updateBrandScopedBrand(selectedBrandId, brand),
				platformSettingsApi.updateBrandScopedStorefront(selectedBrandId, storefront),
				platformSettingsApi.updateBrandScopedSeo(selectedBrandId, seo)
			]);
			await loadSettings(selectedBrandId);
			success = 'Storefront settings tersimpan untuk brand ini.';
		} catch (e) {
			error = (e as Error).message;
		} finally {
			saving = false;
		}
	}

	function nullable(value: string): string | null {
		const trimmed = value.trim();
		return trimmed ? trimmed : null;
	}

	onMount(loadInitial);
</script>

<section class="space-y-2">
	<p class="text-sm font-semibold uppercase text-emerald-300">Storefront</p>
	<h1 class="text-3xl font-bold tracking-tight text-zinc-50">Storefront template controls</h1>
	<p class="max-w-3xl text-zinc-400">
		Konfigurasi brand, homepage copy, SEO default, SKU visibility, dan out-of-stock display per brand.
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
		<p class="mt-3 text-sm text-zinc-400">
			Public config: <a class="text-emerald-200 underline" href={`/storefront/${settings.tenant_brand.slug}/config`}>/{settings.tenant_brand.slug}/config</a>
		</p>
	{/if}
</section>

{#if loading}
	<div class="mt-8 rounded-lg border border-zinc-800 bg-zinc-900 p-5 text-zinc-300">Memuat settings...</div>
{:else if !selectedBrandId}
	<div class="mt-8 rounded-lg border border-zinc-800 bg-zinc-900 p-5 text-zinc-300">Belum ada brand.</div>
{:else}
	<form class="mt-8 space-y-5" onsubmit={(event) => { event.preventDefault(); saveSettings(); }}>
		<div class="grid gap-5 xl:grid-cols-2">
			<section class="rounded-lg border border-zinc-800 bg-zinc-900 p-5">
				<h2 class="text-lg font-semibold text-zinc-100">Brand</h2>
				<div class="mt-4 grid gap-4">
					<label class="field">Brand name <input bind:value={brandName} required /></label>
					<label class="field">Tagline <input bind:value={tagline} /></label>
					<label class="field">Logo URL <input bind:value={logoUrl} /></label>
					<label class="field">WhatsApp <input bind:value={contactWhatsapp} /></label>
					<label class="field">Support email <input bind:value={supportEmail} type="email" /></label>
					<label class="field">Business address <textarea bind:value={businessAddress}></textarea></label>
				</div>
			</section>

			<section class="rounded-lg border border-zinc-800 bg-zinc-900 p-5">
				<h2 class="text-lg font-semibold text-zinc-100">Homepage</h2>
				<div class="mt-4 grid gap-4">
					<label class="toggle"><input type="checkbox" bind:checked={storefrontEnabled} /> Storefront enabled</label>
					<label class="field">Headline <input bind:value={homepageHeadline} required /></label>
					<label class="field">Description <textarea bind:value={homepageDescription}></textarea></label>
					<label class="field">Featured product limit <input bind:value={featuredProductLimit} min="0" type="number" /></label>
					<label class="toggle"><input type="checkbox" bind:checked={showOutOfStockProducts} /> Show out-of-stock products</label>
					<label class="toggle"><input type="checkbox" bind:checked={showSku} /> Show SKU on storefront</label>
				</div>
			</section>
		</div>

		<section class="rounded-lg border border-zinc-800 bg-zinc-900 p-5">
			<h2 class="text-lg font-semibold text-zinc-100">SEO</h2>
			<div class="mt-4 grid gap-4 md:grid-cols-2">
				<label class="field">Site URL <input bind:value={siteUrl} required /></label>
				<label class="field">Default title <input bind:value={defaultTitle} required /></label>
				<label class="field md:col-span-2">Default description <textarea bind:value={defaultDescription}></textarea></label>
				<label class="field md:col-span-2">Social image URL <input bind:value={socialImageUrl} /></label>
			</div>
		</section>

		{#if error}<p class="rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-200">{error}</p>{/if}
		{#if success}<p class="rounded-lg border border-emerald-900 bg-emerald-950/40 p-3 text-sm text-emerald-200">{success}</p>{/if}

		<button class="save-button" disabled={saving} type="submit">
			<Save size={16} />
			{saving ? 'Menyimpan...' : 'Simpan Storefront Settings'}
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
	input,
	select,
	textarea {
		width: 100%;
		border: 1px solid #3f3f46;
		border-radius: 8px;
		background: #18181b;
		color: #fafafa;
		padding: 0.7rem 0.8rem;
		font-weight: 500;
		outline: none;
	}
	textarea {
		min-height: 6rem;
		resize: vertical;
	}
	.toggle {
		display: flex;
		align-items: center;
		gap: 0.7rem;
		color: #d4d4d8;
		font-size: 0.9rem;
		font-weight: 700;
	}
	.toggle input {
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
