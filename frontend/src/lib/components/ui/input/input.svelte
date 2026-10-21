<script lang="ts">
	import { cn } from '$lib/utils';

	type Props = {
		class?: string;
		placeholder?: string;
		type?: string;
		value?: string;
		[key: string]: unknown;
	};

	let { class: className, type = 'text', value = $bindable(''), ...rest }: Props = $props();
</script>

<input
	class={cn(
		'flex h-10 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm text-slate-950 shadow-sm transition-colors placeholder:text-slate-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-400',
		className
	)}
	{type}
	bind:value
	{...rest}
/>
