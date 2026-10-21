<script lang="ts">
	import { onMount } from 'svelte';
	import { ArrowRight, Flag, Globe2, Network, Settings, ShieldCheck } from 'lucide-svelte';
	import { platformSettingsApi, type Brand } from '$lib/api/platform-settings';

	const cards = [
		{
			href: '/console/storefront',
			title: 'Storefront Settings',
			description: 'Brand copy, public storefront behavior, and catalog display defaults.',
			icon: Globe2
		},
		{
			href: '/console/modules',
			title: 'Module Flags',
			description: 'Control which CommerceMind modules are available for each brand.',
			icon: Flag
		},
		{
			href: '/console/system',
			title: 'System Controls',
			description: 'Maintenance mode, test mode, public catalog, and checkout availability.',
			icon: ShieldCheck
		},
		{
			href: '/console/settings',
			title: 'Settings Overview',
			description: 'Review brand-scoped settings groups before editing detailed configuration.',
			icon: Settings
		}
	];

	let brands = $state<Brand[]>([]);
	let selectedBrandId = $state<number | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);

	async function loadBrands() {
		loading = true;
		error = null;
		try {
			brands = await platformSettingsApi.listBrands();
			selectedBrandId = brands[0]?.id ?? null;
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	function scopedHref(href: string) {
		return selectedBrandId ? `${href}?brandId=${selectedBrandId}` : href;
	}

	onMount(loadBrands);
</script>

<section class="space-y-2">
	<p class="text-sm font-semibold uppercase text-emerald-300">Platform Console</p>
	<h1 class="text-3xl font-bold tracking-tight text-zinc-50 sm:text-4xl">CommerceMind control surface</h1>
	<p class="max-w-3xl text-zinc-400">
		Area ini untuk platform operator. Merchant admin tetap memakai <a class="text-emerald-200 underline" href="/admin">/admin</a>
		untuk operasi toko harian.
	</p>
</section>

<section class="mt-6 rounded-lg border border-zinc-800 bg-zinc-900 p-5">
	<div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
		<label class="field w-full max-w-xl">
			Brand scope
			<select bind:value={selectedBrandId}>
				{#each brands as brand}
					<option value={brand.id}>{brand.name} /{brand.slug}</option>
				{/each}
			</select>
		</label>
		<a class="brand-link" href="/console/brands">
			<Network size={16} />
			Manage Brands
		</a>
	</div>
	{#if loading}
		<p class="mt-3 text-sm text-zinc-400">Memuat brand...</p>
	{:else if error}
		<p class="mt-3 text-sm text-red-200">{error}</p>
	{:else if !selectedBrandId}
		<p class="mt-3 text-sm text-zinc-400">Belum ada brand. Buat brand dari halaman Brands.</p>
	{/if}
</section>

<section class="mt-8 grid gap-4 md:grid-cols-2">
	{#each cards as card}
		{@const Icon = card.icon}
		<a
			href={scopedHref(card.href)}
			class="rounded-lg border border-zinc-800 bg-zinc-900 p-5 text-zinc-100 transition-colors hover:border-emerald-300"
		>
			<Icon class="text-emerald-300" size={24} />
			<h2 class="mt-4 text-lg font-semibold">{card.title}</h2>
			<p class="mt-2 text-sm leading-6 text-zinc-400">{card.description}</p>
			<span class="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-emerald-200">
				Open scoped panel
				<ArrowRight size={16} />
			</span>
		</a>
	{/each}
</section>

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
	.brand-link {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		border: 1px solid #3f3f46;
		border-radius: 8px;
		color: #e4e4e7;
		padding: 0.7rem 1rem;
		font-weight: 900;
		text-decoration: none;
	}
</style>
