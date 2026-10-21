<script lang="ts">
	import { storefrontConfig } from '$lib/storefront';

	let { children } = $props();
</script>

<div class="storefront-shell">
	<header>
		<a class="brand" href="/storefront">{storefrontConfig.brandName}</a>
		<nav aria-label="Navigasi toko">
			<a href="/storefront">Home</a>
			<a href="/storefront/products">Produk</a>
		</nav>
	</header>

	<main>
		{@render children()}
	</main>
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
		color: #46534d;
		font-weight: 800;
		text-decoration: none;
	}

	main {
		width: min(1120px, calc(100% - 32px));
		margin: 0 auto;
		padding: 48px 0;
	}

	@media (max-width: 560px) {
		header {
			align-items: flex-start;
			flex-direction: column;
			padding: 16px 0;
		}

		nav a {
			min-height: 2.5rem;
			display: inline-flex;
			align-items: center;
		}

		main {
			padding: 28px 0;
		}
	}
</style>
