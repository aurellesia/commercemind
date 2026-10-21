<script lang="ts">
	const areas = [
		{
			href: '/admin',
			title: 'Admin Dashboard',
			description: 'Manage catalog, inventory, customers, orders, and payments.'
		},
		{
			href: '/storefront',
			title: 'Customer Storefront',
			description: 'Browse products and start the customer shopping experience.'
		},
		{
			href: '/console',
			title: 'Platform Console',
			description: 'Configure platform-level settings, modules, and storefront templates.'
		}
	];
</script>

<main class="home">
	<section class="intro">
		<p class="eyebrow">CommerceMind</p>
		<h1>Choose an application area</h1>
	</section>

	<section class="area-grid" aria-label="Application areas">
		{#each areas as area}
			<a class="area-card" href={area.href}>
				<span>{area.title}</span>
				<p>{area.description}</p>
			</a>
		{/each}
	</section>
</main>

<style>
	:global(body) {
		margin: 0;
		font-family:
			Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
		color: #182026;
		background: #f6f7f4;
	}

	.home {
		width: min(1040px, calc(100% - 32px));
		margin: 0 auto;
		padding: 72px 0;
	}

	.intro {
		margin-bottom: 32px;
	}

	.eyebrow {
		margin: 0 0 8px;
		color: #4d6b57;
		font-size: 0.78rem;
		font-weight: 700;
		text-transform: uppercase;
	}

	h1 {
		max-width: 680px;
		margin: 0;
		font-size: clamp(2rem, 7vw, 4.5rem);
		line-height: 1;
		letter-spacing: 0;
	}

	.area-grid {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 16px;
	}

	.area-card {
		display: grid;
		gap: 12px;
		min-height: 156px;
		padding: 24px;
		color: inherit;
		text-decoration: none;
		background: #ffffff;
		border: 1px solid #dfe4dc;
		border-radius: 8px;
	}

	.area-card:hover {
		border-color: #78977f;
	}

	.area-card span {
		font-size: 1.2rem;
		font-weight: 800;
	}

	.area-card p {
		max-width: 34ch;
		margin: 0;
		color: #5b6470;
		line-height: 1.5;
	}

	@media (max-width: 720px) {
		.area-grid {
			grid-template-columns: 1fr;
		}
	}

	@media (min-width: 721px) and (max-width: 980px) {
		.area-grid {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
	}
</style>
