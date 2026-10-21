<script lang="ts">
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { platformSettingsApi, type PlatformSettings } from '$lib/api/platform-settings';

	let settings = $state<PlatformSettings | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const brandId = $derived(Number(page.params.brandId));

	async function loadSettings() {
		loading = true;
		error = null;
		try {
			settings = await platformSettingsApi.getBrandSettings(brandId);
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	onMount(loadSettings);
</script>

<section class="space-y-2">
	<p class="text-sm font-semibold uppercase text-emerald-300">Brand Settings</p>
	<h1 class="text-3xl font-bold tracking-tight text-zinc-50">{settings?.tenant_brand.name ?? 'Brand settings'}</h1>
	<p class="max-w-3xl text-zinc-400">
		Brand-scoped settings endpoint sudah tersedia. Form edit penuh akan digabung setelah UI global lama dipindah ke konteks brand.
	</p>
</section>

{#if loading}
	<div class="mt-8 rounded-lg border border-zinc-800 bg-zinc-900 p-5 text-zinc-300">Memuat settings...</div>
{:else if error}
	<div class="mt-8 rounded-lg border border-red-900 bg-red-950/40 p-5 text-red-200">{error}</div>
{:else if settings}
	<div class="mt-8 grid gap-4 md:grid-cols-2">
		<div class="rounded-lg border border-zinc-800 bg-zinc-900 p-5">
			<h2 class="font-semibold text-zinc-100">Storefront</h2>
			<p class="mt-2 text-sm text-zinc-400">{settings.storefront.homepage_headline}</p>
		</div>
		<div class="rounded-lg border border-zinc-800 bg-zinc-900 p-5">
			<h2 class="font-semibold text-zinc-100">Modules</h2>
			<p class="mt-2 text-sm text-zinc-400">Cart: {settings.modules.cart_enabled ? 'enabled' : 'disabled'}</p>
		</div>
	</div>
{/if}
