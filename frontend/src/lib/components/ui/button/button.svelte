<script lang="ts">
	import type { Snippet } from 'svelte';
	import { cn } from '$lib/utils';

	type Props = {
		children?: Snippet;
		class?: string;
		href?: string;
		type?: 'button' | 'submit' | 'reset';
		variant?: 'default' | 'outline' | 'secondary' | 'ghost';
		size?: 'default' | 'sm' | 'icon';
		onclick?: (event: MouseEvent) => void;
		[key: string]: unknown;
	};

	let {
		children,
		class: className,
		href,
		type = 'button',
		variant = 'default',
		size = 'default',
		onclick,
		...rest
	}: Props = $props();

	const variants = {
		default: 'bg-slate-950 text-white hover:bg-slate-800',
		outline: 'border border-slate-200 bg-white text-slate-950 hover:bg-slate-100',
		secondary: 'bg-slate-100 text-slate-950 hover:bg-slate-200',
		ghost: 'text-slate-700 hover:bg-slate-100 hover:text-slate-950'
	};

	const sizes = {
		default: 'h-10 px-4 py-2',
		sm: 'h-9 px-3',
		icon: 'h-10 w-10'
	};

	const classes = $derived(
		cn(
			'inline-flex items-center justify-center gap-2 rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-400 disabled:pointer-events-none disabled:opacity-50',
			variants[variant],
			sizes[size],
			className
		)
	);
</script>

{#if href}
	<a class={classes} {href} {...rest}>
		{@render children?.()}
	</a>
{:else}
	<button class={classes} {type} {onclick} {...rest}>
		{@render children?.()}
	</button>
{/if}
