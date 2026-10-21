<script lang="ts">
	import { onMount } from 'svelte';
	import { ArrowRight, Plus } from 'lucide-svelte';
	import { platformSettingsApi, type Brand } from '$lib/api/platform-settings';

	let brands = $state<Brand[]>([]);
	let loading = $state(true);
	let saving = $state(false);
	let error = $state<string | null>(null);
	let success = $state<string | null>(null);
	let name = $state('');
	let slug = $state('');
	let plan = $state('starter');

	async function loadBrands() {
		loading = true;
		error = null;
		try {
			brands = await platformSettingsApi.listBrands();
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	async function createBrand() {
		saving = true;
		error = null;
		success = null;
		try {
			await platformSettingsApi.createBrand({
				name,
				slug: slug || name,
				status: 'active',
				plan
			});
			name = '';
			slug = '';
			plan = 'starter';
			success = 'Brand dibuat.';
			await loadBrands();
		} catch (e) {
			error = (e as Error).message;
		} finally {
			saving = false;
		}
	}

	onMount(loadBrands);
</script>

<section class="space-y-2">
	<p class="text-sm font-semibold uppercase text-emerald-300">Brands</p>
	<h1 class="text-3xl font-bold tracking-tight text-zinc-50">Brand control plane</h1>
	<p class="max-w-3xl text-zinc-400">
		Kelola brand/client CommerceMind. Setiap brand akan punya settings, storefront, dan merchant admin sendiri.
	</p>
</section>

<form class="mt-8 rounded-lg border border-zinc-800 bg-zinc-900 p-5" onsubmit={(event) => { event.preventDefault(); createBrand(); }}>
	<h2 class="font-semibold text-zinc-100">Create brand</h2>
	<div class="mt-4 grid gap-3 md:grid-cols-3">
		<label class="field">Name <input bind:value={name} required /></label>
		<label class="field">Slug <input bind:value={slug} placeholder="auto from name" /></label>
		<label class="field">Plan <input bind:value={plan} required /></label>
	</div>
	<button class="save-button mt-4" disabled={saving} type="submit">
		<Plus size={16} />
		{saving ? 'Membuat...' : 'Create Brand'}
	</button>
</form>

{#if error}<p class="mt-4 rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-200">{error}</p>{/if}
{#if success}<p class="mt-4 rounded-lg border border-emerald-900 bg-emerald-950/40 p-3 text-sm text-emerald-200">{success}</p>{/if}

{#if loading}
	<div class="mt-8 rounded-lg border border-zinc-800 bg-zinc-900 p-5 text-zinc-300">Memuat brands...</div>
{:else}
	<section class="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-3" aria-label="Brands">
		{#each brands as brand}
			<a class="brand-card" href={`/console/brands/${brand.id}`}>
				<div>
					<p class="status">{brand.status}</p>
					<h2>{brand.name}</h2>
					<p>/{brand.slug}</p>
					<p>{brand.plan}</p>
				</div>
				<ArrowRight size={18} />
			</a>
		{/each}
	</section>
{/if}

<style>
	.field {
		display: grid;
		gap: 0.45rem;
		color: #d4d4d8;
		font-size: 0.875rem;
		font-weight: 700;
	}
	input {
		width: 100%;
		border: 1px solid #3f3f46;
		border-radius: 8px;
		background: #18181b;
		color: #fafafa;
		padding: 0.7rem 0.8rem;
		outline: none;
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
	.brand-card {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 1rem;
		border: 1px solid #27272a;
		border-radius: 8px;
		background: #18181b;
		color: #f4f4f5;
		padding: 1.25rem;
		text-decoration: none;
	}
	.brand-card:hover {
		border-color: #6ee7b7;
	}
	.status {
		color: #6ee7b7;
		font-size: 0.75rem;
		font-weight: 900;
		text-transform: uppercase;
	}
	.brand-card h2 {
		margin-top: 0.35rem;
		font-size: 1.2rem;
		font-weight: 900;
	}
	.brand-card p {
		margin: 0.2rem 0;
		color: #a1a1aa;
	}
</style>
