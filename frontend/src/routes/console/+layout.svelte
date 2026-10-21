<script lang="ts">
	import { page } from '$app/state';
	import {
		Flag,
		LayoutDashboard,
		MonitorCog,
		Network,
		Settings,
		ShoppingBag,
		SlidersHorizontal
	} from 'lucide-svelte';
	import { cn } from '$lib/utils';

	let { children } = $props();

	const navItems = [
		{ href: '/console', label: 'Overview', icon: LayoutDashboard },
		{ href: '/console/brands', label: 'Brands', icon: Network },
		{ href: '/console/settings', label: 'Settings', icon: Settings },
		{ href: '/console/storefront', label: 'Storefront', icon: ShoppingBag },
		{ href: '/console/modules', label: 'Modules', icon: Flag },
		{ href: '/console/system', label: 'System', icon: SlidersHorizontal }
	];
</script>

<div class="min-h-screen bg-zinc-950 text-zinc-50">
	<aside
		class="fixed inset-y-0 left-0 hidden w-64 border-r border-zinc-800 bg-zinc-950 px-4 py-5 lg:block"
		aria-label="Platform console navigation"
	>
		<a class="flex items-center gap-3 px-2 text-zinc-50" href="/console">
			<span class="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-400 text-zinc-950">
				<MonitorCog size={20} />
			</span>
			<span>
				<span class="block text-sm font-semibold">CommerceMind</span>
				<span class="block text-xs text-zinc-400">Platform Console</span>
			</span>
		</a>

		<nav class="mt-8 grid gap-1">
			{#each navItems as item}
				{@const active =
					item.href === '/console'
						? page.url.pathname === item.href
						: page.url.pathname.startsWith(item.href)}
				{@const Icon = item.icon}
				<a
					href={item.href}
					aria-current={active ? 'page' : undefined}
					class={cn(
						'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-zinc-400 transition-colors hover:bg-zinc-900 hover:text-zinc-50',
						active && 'bg-zinc-900 text-zinc-50'
					)}
				>
					<Icon size={18} />
					{item.label}
				</a>
			{/each}
		</nav>
	</aside>

	<header class="sticky top-0 z-10 border-b border-zinc-800 bg-zinc-950/90 backdrop-blur lg:ml-64">
		<div class="flex h-16 items-center justify-between gap-3 px-4 sm:px-6 lg:px-8">
			<div>
				<p class="text-xs font-medium uppercase text-emerald-300">Platform</p>
				<p class="text-sm font-semibold text-zinc-100">CommerceMind Console</p>
			</div>

			<div class="flex items-center gap-2">
				<a
					class="rounded-md border border-zinc-700 px-3 py-2 text-sm font-semibold text-zinc-200 hover:bg-zinc-900"
					href="/admin"
				>
					Merchant Admin
				</a>
				<a
					class="rounded-md border border-zinc-700 px-3 py-2 text-sm font-semibold text-zinc-200 hover:bg-zinc-900"
					href="/storefront"
				>
					Storefront
				</a>
			</div>
		</div>
	</header>

	<main class="lg:ml-64">
		<div class="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
			<nav class="mb-6 grid grid-cols-2 gap-2 lg:hidden" aria-label="Mobile console navigation">
				{#each navItems as item}
					{@const active =
						item.href === '/console'
							? page.url.pathname === item.href
							: page.url.pathname.startsWith(item.href)}
					{@const Icon = item.icon}
					<a
						href={item.href}
						class={cn(
							'flex items-center gap-2 rounded-md border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm font-medium text-zinc-300',
							active && 'border-emerald-300 text-emerald-200'
						)}
					>
						<Icon size={16} />
						{item.label}
					</a>
				{/each}
			</nav>

			{@render children()}
		</div>
	</main>
</div>
