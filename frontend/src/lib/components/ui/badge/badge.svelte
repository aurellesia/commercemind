<script lang="ts">
	import type { Snippet } from 'svelte';
	import { cn } from '$lib/utils';

	type Props = {
		children?: Snippet;
		class?: string;
		variant?: 'default' | 'secondary' | 'outline' | 'success' | 'warning';
	};

	let { children, class: className, variant = 'default' }: Props = $props();

	const variants = {
		default: 'bg-slate-950 text-white',
		secondary: 'bg-slate-100 text-slate-700',
		outline: 'border border-slate-200 text-slate-700',
		success: 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200',
		warning: 'bg-amber-50 text-amber-700 ring-1 ring-amber-200'
	};
</script>

<span
	class={cn(
		'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold',
		variants[variant],
		className
	)}
>
	{@render children?.()}
</span>
