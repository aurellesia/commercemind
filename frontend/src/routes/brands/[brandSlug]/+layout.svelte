<script lang="ts">
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { ShoppingCart, UserRound } from 'lucide-svelte';
	import {
		getPublicStorefrontConfig,
		type PublicStorefrontConfig
	} from '$lib/api/storefront-config';

	let { children } = $props();
	let config = $state<PublicStorefrontConfig | null>(null);
	let error = $state<string | null>(null);
	const brandSlug = $derived(page.params.brandSlug ?? 'default');

	async function loadConfig() {
		error = null;
		try {
			config = await getPublicStorefrontConfig(brandSlug);
		} catch (e) {
			error = (e as Error).message;
		}
	}

	onMount(loadConfig);
</script>

<div class="storefront-shell">
	<header>
		<a class="brand" href={`/brands/${brandSlug}`}>{config?.brand_name ?? brandSlug}</a>
		<nav aria-label="Navigasi toko">
			<a href={`/brands/${brandSlug}`}>Home</a>
			{#if config?.modules.products_enabled ?? true}
				<a href={`/brands/${brandSlug}/products`}>Produk</a>
			{/if}
			{#if config?.modules.cart_enabled}
				<a class="icon-link" href={`/brands/${brandSlug}/cart`} aria-label="Keranjang">
					<ShoppingCart size={18} />
				</a>
			{/if}
			{#if config?.modules.customer_accounts_enabled}
				<a class="icon-link" href={`/brands/${brandSlug}/account`} aria-label="Akun customer">
					<UserRound size={18} />
				</a>
			{/if}
		</nav>
	</header>

	{#if error}
		<main>
			<div class="state-card">Brand tidak ditemukan atau belum aktif.</div>
		</main>
	{:else if config && !config.storefront_enabled}
		<main>
			<div class="state-card">Storefront brand ini sedang belum tersedia.</div>
		</main>
	{:else}
		<main>
			{@render children()}
		</main>
	{/if}
</div>

<style>
	.storefront-shell {
		min-height: 100vh;
		background: #fbfaf7;
	}
	header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		width: min(1120px, calc(100% - 32px));
		margin: 0 auto;
		padding: 20px 0;
	}
	.brand {
		color: #17211e;
		font-weight: 900;
		text-decoration: none;
	}
	nav {
		display: flex;
		flex-wrap: wrap;
		gap: 18px;
	}
	nav a {
		display: inline-flex;
		align-items: center;
		min-height: 2rem;
		color: #46534d;
		font-weight: 800;
		text-decoration: none;
	}
	.icon-link {
		justify-content: center;
		width: 2rem;
	}
	main {
		width: min(1120px, calc(100% - 32px));
		margin: 0 auto;
		padding: 48px 0;
	}
	.state-card {
		border: 1px dashed #cfc8b8;
		border-radius: 8px;
		background: #fffdf8;
		color: #687163;
		padding: 2rem;
		text-align: center;
	}
	@media (max-width: 560px) {
		header {
			align-items: flex-start;
			flex-direction: column;
			padding: 16px 0;
		}
		main {
			padding: 28px 0;
		}
	}
</style>
