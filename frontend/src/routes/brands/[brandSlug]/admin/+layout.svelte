<script lang="ts">
	import { page } from '$app/state';
	import {
		BadgeDollarSign,
		Boxes,
		ChartNoAxesCombined,
		Images,
		LayoutDashboard,
		Package,
		ShoppingCart,
		Users
	} from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	import { cn } from '$lib/utils';

	let { children } = $props();
	const brandSlug = $derived(page.params.brandSlug ?? 'default');
	const adminSubtitle = $derived(
		brandSlug === 'default' ? 'Default demo admin' : `Brand admin: ${brandSlug}`
	);
	const headerTitle = $derived(
		brandSlug === 'default' ? 'CommerceMind default brand' : `CommerceMind brand: ${brandSlug}`
	);
	const navItems = $derived([
		{ href: `/brands/${brandSlug}/admin`, label: 'Overview', icon: LayoutDashboard },
		{
			href: `/brands/${brandSlug}/admin/products`,
			label: 'Products',
			icon: Package,
			children: [
				{ href: `/brands/${brandSlug}/admin/products`, label: 'Product List', icon: Package },
				{ href: '/admin/products/images', label: 'Product Images', icon: Images }
			]
		},
		{ href: `/brands/${brandSlug}/admin/inventory`, label: 'Inventory', icon: Boxes },
		{ href: `/brands/${brandSlug}/admin/customers`, label: 'Customers', icon: Users },
		{ href: `/brands/${brandSlug}/admin/orders`, label: 'Orders', icon: ShoppingCart },
		{ href: '/admin/payments', label: 'Payments', icon: BadgeDollarSign }
	]);

	function isActive(href: string) {
		if (href === `/brands/${brandSlug}/admin`) return page.url.pathname === href;
		return page.url.pathname === href || page.url.pathname.startsWith(`${href}/`);
	}
</script>

<div class="min-h-screen bg-slate-50 text-slate-950">
	<aside
		class="fixed inset-y-0 left-0 hidden w-64 border-r border-slate-200 bg-white px-4 py-5 lg:block"
		aria-label="Admin navigation"
	>
		<a class="flex items-center gap-3 px-2 text-slate-950" href={`/brands/${brandSlug}/admin`}>
			<span class="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-950 text-white">
				<ChartNoAxesCombined size={20} />
			</span>
			<span>
				<span class="block text-sm font-semibold">CommerceMind</span>
				<span class="block text-xs text-slate-500">{adminSubtitle}</span>
			</span>
		</a>

		<nav class="mt-8 grid gap-1">
			{#each navItems as item}
				{@const active = isActive(item.href)}
				{@const Icon = item.icon}
				<a
					href={item.href}
					aria-current={active ? 'page' : undefined}
					class={cn(
						'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-950',
						active && 'bg-slate-100 text-slate-950'
					)}
				>
					<Icon size={18} />
					{item.label}
				</a>
				{#if item.children && active}
					<div class="ml-6 grid gap-1 border-l border-slate-200 pl-3">
						{#each item.children as child}
							{@const childActive = page.url.pathname === child.href}
							{@const ChildIcon = child.icon}
							<a
								href={child.href}
								aria-current={childActive ? 'page' : undefined}
								class={cn(
									'flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-950',
									childActive && 'bg-slate-100 text-slate-950'
								)}
							>
								<ChildIcon size={16} />
								{child.label}
							</a>
						{/each}
					</div>
				{/if}
			{/each}
		</nav>
	</aside>

	<header class="sticky top-0 z-10 border-b border-slate-200 bg-white/90 backdrop-blur lg:ml-64">
		<div class="flex h-16 items-center justify-between gap-3 px-4 sm:px-6 lg:px-8">
			<div>
				<p class="text-xs font-medium uppercase text-slate-500">Admin</p>
				<p class="text-sm font-semibold text-slate-900">{headerTitle}</p>
			</div>
			<Button variant="outline" size="sm" href={`/brands/${brandSlug}`}>View Storefront</Button>
		</div>
	</header>

	<main class="lg:ml-64">
		<div class="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
			<nav class="mb-6 grid grid-cols-2 gap-2 lg:hidden" aria-label="Mobile admin navigation">
				{#each navItems as item}
					{@const active = isActive(item.href)}
					{@const Icon = item.icon}
					<a
						href={item.href}
						class={cn(
							'flex items-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-600',
							active && 'border-slate-950 text-slate-950'
						)}
					>
						<Icon size={16} />
						{item.label}
					</a>
					{#if item.children && active}
						{#each item.children as child}
							{@const childActive = page.url.pathname === child.href}
							{@const ChildIcon = child.icon}
							<a
								href={child.href}
								class={cn(
									'flex items-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-600',
									childActive && 'border-slate-950 text-slate-950'
								)}
							>
								<ChildIcon size={16} />
								{child.label}
							</a>
						{/each}
					{/if}
				{/each}
			</nav>
			{@render children()}
		</div>
	</main>
</div>
