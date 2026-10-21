<script lang="ts">
	import type { Snippet } from 'svelte';
	import { cn } from '$lib/utils';

	type Props = {
		children?: Snippet;
		class?: string;
	};

	let { children, class: className }: Props = $props();
</script>

<div class={cn('rounded-lg border border-slate-200 bg-white text-slate-950 shadow-sm', className)}>
	{@render children?.()}
</div>
