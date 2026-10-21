<script lang="ts">
	import { page } from '$app/state';
	const brandSlug = $derived(page.params.brandSlug ?? 'default');
</script>

<section class="rounded-lg border border-slate-200 bg-white p-6">
	<p class="text-sm font-semibold uppercase text-slate-500">Brand-scoped admin</p>
	<h1 class="mt-2 text-3xl font-bold text-slate-950">Admin untuk {brandSlug}</h1>
	<p class="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
		Route admin sudah brand-scoped. Data operasional akan benar-benar dipisah per brand di Fase 7.
	</p>
</section>
