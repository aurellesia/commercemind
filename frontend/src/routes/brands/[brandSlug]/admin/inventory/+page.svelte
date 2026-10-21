<script lang="ts">
	import { page } from '$app/state';
	const brandSlug = $derived(page.params.brandSlug ?? 'default');
</script>

<section class="rounded-lg border border-slate-200 bg-white p-6">
	<h1 class="text-3xl font-bold text-slate-950">Inventory</h1>
	<p class="mt-2 text-sm text-slate-600">
		Brand context: {brandSlug}. Inventory scoping masuk fase porting admin brand-scoped.
		Legacy panel sementara selalu memakai brand default CommerceMind sebagai demo data.
	</p>
	<a class="mt-4 inline-flex rounded-md bg-slate-950 px-4 py-2 text-sm font-semibold text-white" href="/admin/inventory">Buka legacy CommerceMind inventory</a>
</section>
