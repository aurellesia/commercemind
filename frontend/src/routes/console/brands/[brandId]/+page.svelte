<script lang="ts">
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { Save } from 'lucide-svelte';
	import { platformSettingsApi, type Brand } from '$lib/api/platform-settings';

	let brand = $state<Brand | null>(null);
	let loading = $state(true);
	let saving = $state(false);
	let error = $state<string | null>(null);
	let success = $state<string | null>(null);

	let name = $state('');
	let slug = $state('');
	let status = $state<'draft' | 'active' | 'suspended' | 'archived'>('active');
	let plan = $state('');
	let primaryDomain = $state('');

	const brandId = $derived(Number(page.params.brandId));

	async function loadBrand() {
		loading = true;
		error = null;
		try {
			brand = await platformSettingsApi.getBrand(brandId);
			name = brand.name;
			slug = brand.slug;
			status = brand.status;
			plan = brand.plan;
			primaryDomain = brand.primary_domain ?? '';
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	async function saveBrand() {
		saving = true;
		error = null;
		success = null;
		try {
			brand = await platformSettingsApi.updateTenantBrand(brandId, {
				name,
				slug,
				status,
				plan,
				primary_domain: primaryDomain.trim() || null
			});
			success = 'Brand tersimpan.';
		} catch (e) {
			error = (e as Error).message;
		} finally {
			saving = false;
		}
	}

	onMount(loadBrand);
</script>

<section class="space-y-2">
	<p class="text-sm font-semibold uppercase text-emerald-300">Brand</p>
	<h1 class="text-3xl font-bold tracking-tight text-zinc-50">{brand?.name ?? 'Brand detail'}</h1>
	<p class="max-w-3xl text-zinc-400">
		Atur metadata tenant brand. Settings storefront per brand tersedia lewat endpoint `/platform/brands/{brandId}/settings`.
	</p>
</section>

{#if loading}
	<div class="mt-8 rounded-lg border border-zinc-800 bg-zinc-900 p-5 text-zinc-300">Memuat brand...</div>
{:else}
	<form class="mt-8 space-y-5" onsubmit={(event) => { event.preventDefault(); saveBrand(); }}>
		<section class="rounded-lg border border-zinc-800 bg-zinc-900 p-5">
			<div class="grid gap-4 md:grid-cols-2">
				<label class="field">Name <input bind:value={name} required /></label>
				<label class="field">Slug <input bind:value={slug} required /></label>
				<label class="field">
					Status
					<select bind:value={status}>
						<option value="draft">Draft</option>
						<option value="active">Active</option>
						<option value="suspended">Suspended</option>
						<option value="archived">Archived</option>
					</select>
				</label>
				<label class="field">Plan <input bind:value={plan} required /></label>
				<label class="field md:col-span-2">Primary domain <input bind:value={primaryDomain} /></label>
			</div>
		</section>

		<div class="flex flex-wrap gap-3">
			<button class="save-button" disabled={saving} type="submit">
				<Save size={16} />
				{saving ? 'Menyimpan...' : 'Simpan Brand'}
			</button>
			<a class="secondary-link" href={`/console/brands/${brandId}/settings`}>Brand Settings</a>
			<a class="secondary-link" href={`/storefront/${brand?.slug ?? 'default'}/config`}>Public Config JSON</a>
		</div>
	</form>
{/if}

{#if error}<p class="mt-4 rounded-lg border border-red-900 bg-red-950/40 p-3 text-sm text-red-200">{error}</p>{/if}
{#if success}<p class="mt-4 rounded-lg border border-emerald-900 bg-emerald-950/40 p-3 text-sm text-emerald-200">{success}</p>{/if}

<style>
	.field {
		display: grid;
		gap: 0.45rem;
		color: #d4d4d8;
		font-size: 0.875rem;
		font-weight: 700;
	}
	input,
	select {
		width: 100%;
		border: 1px solid #3f3f46;
		border-radius: 8px;
		background: #18181b;
		color: #fafafa;
		padding: 0.7rem 0.8rem;
		outline: none;
	}
	.save-button,
	.secondary-link {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		border-radius: 8px;
		padding: 0.7rem 1rem;
		font-weight: 900;
		text-decoration: none;
	}
	.save-button {
		background: #34d399;
		color: #052e1b;
	}
	.secondary-link {
		border: 1px solid #3f3f46;
		color: #e4e4e7;
	}
</style>
