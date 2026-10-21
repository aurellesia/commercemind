<script lang="ts">
	import {
		ArrowUpRight,
		CircleDollarSign,
		PackageCheck,
		ShoppingBag,
		UsersRound
	} from 'lucide-svelte';
	import { Badge } from '$lib/components/ui/badge';
	import { Button } from '$lib/components/ui/button';
	import { Card } from '$lib/components/ui/card';

	const metrics = [
		{
			label: 'Revenue',
			value: 'Rp128.4M',
			change: '+12.5%',
			icon: CircleDollarSign,
			tone: 'text-emerald-600'
		},
		{
			label: 'Orders',
			value: '1,248',
			change: '+8.2%',
			icon: ShoppingBag,
			tone: 'text-sky-600'
		},
		{
			label: 'Customers',
			value: '8,492',
			change: '+5.1%',
			icon: UsersRound,
			tone: 'text-violet-600'
		},
		{
			label: 'Fulfillment',
			value: '96.8%',
			change: '+2.4%',
			icon: PackageCheck,
			tone: 'text-amber-600'
		}
	];

	const recentOrders = [
		{ id: '#CM-1028', customer: 'Nadia Putri', total: 'Rp1.240.000', status: 'Paid' },
		{ id: '#CM-1027', customer: 'Arga Wibowo', total: 'Rp780.000', status: 'Packing' },
		{ id: '#CM-1026', customer: 'Maya Lestari', total: 'Rp2.450.000', status: 'Paid' },
		{ id: '#CM-1025', customer: 'Rafi Hakim', total: 'Rp560.000', status: 'Review' }
	];

	const stockAlerts = [
		{ item: 'Premium Hoodie', remaining: 8 },
		{ item: 'Canvas Tote', remaining: 11 },
		{ item: 'Daily Sneakers', remaining: 14 }
	];
</script>

<section class="mb-6 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
	<div>
		<p class="text-sm font-medium text-slate-500">Admin Dashboard</p>
		<h1 class="mt-1 text-3xl font-bold tracking-tight text-slate-950">Commerce operations</h1>
		<p class="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
			Monitor orders, customers, inventory, and payment health from one command center.
		</p>
	</div>

	<div class="flex gap-2">
		<Button variant="outline">Export</Button>
		<Button>New Product</Button>
	</div>
</section>

<section class="grid gap-4 md:grid-cols-2 xl:grid-cols-4" aria-label="Business metrics">
	{#each metrics as metric}
		{@const Icon = metric.icon}
		<Card class="p-5">
			<div class="flex items-start justify-between gap-4">
				<div>
					<p class="text-sm font-medium text-slate-500">{metric.label}</p>
					<p class="mt-2 text-2xl font-bold">{metric.value}</p>
				</div>
				<div class="rounded-md bg-slate-100 p-2 {metric.tone}">
					<Icon size={20} />
				</div>
			</div>
			<p class="mt-4 flex items-center gap-1 text-sm font-medium text-emerald-600">
				<ArrowUpRight size={16} />
				{metric.change} from last month
			</p>
		</Card>
	{/each}
</section>

<section class="mt-6 grid gap-6 xl:grid-cols-[1fr_360px]">
	<Card class="overflow-hidden">
		<div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
			<div>
				<h2 class="text-base font-semibold">Recent orders</h2>
				<p class="text-sm text-slate-500">Latest checkout activity requiring admin attention.</p>
			</div>
			<Button variant="ghost" size="sm" href="/admin/orders">View all</Button>
		</div>

		<div class="overflow-x-auto">
			<table class="w-full text-left text-sm">
				<thead class="bg-slate-50 text-xs uppercase text-slate-500">
					<tr>
						<th class="px-5 py-3 font-semibold">Order</th>
						<th class="px-5 py-3 font-semibold">Customer</th>
						<th class="px-5 py-3 font-semibold">Total</th>
						<th class="px-5 py-3 font-semibold">Status</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-slate-100">
					{#each recentOrders as order}
						<tr class="hover:bg-slate-50">
							<td class="px-5 py-4 font-medium text-slate-950">{order.id}</td>
							<td class="px-5 py-4 text-slate-600">{order.customer}</td>
							<td class="px-5 py-4 text-slate-600">{order.total}</td>
							<td class="px-5 py-4">
								<Badge variant={order.status === 'Review' ? 'warning' : 'success'}>{order.status}</Badge>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</Card>

	<div class="grid gap-6">
		<Card class="p-5">
			<div class="flex items-center justify-between">
				<h2 class="text-base font-semibold">Inventory watch</h2>
				<Badge variant="secondary">3 alerts</Badge>
			</div>

			<div class="mt-4 grid gap-3">
				{#each stockAlerts as alert}
					<div class="rounded-md border border-slate-200 p-3">
						<div class="flex items-center justify-between gap-3">
							<p class="font-medium">{alert.item}</p>
							<Badge variant="warning">{alert.remaining} left</Badge>
						</div>
						<div class="mt-3 h-2 overflow-hidden rounded-full bg-slate-100">
							<div class="h-full rounded-full bg-amber-500" style={`width: ${alert.remaining * 5}%`}></div>
						</div>
					</div>
				{/each}
			</div>
		</Card>

		<Card class="p-5">
			<h2 class="text-base font-semibold">Channel health</h2>
			<div class="mt-4 grid gap-4">
				<div>
					<div class="mb-1 flex justify-between text-sm">
						<span class="text-slate-600">Storefront conversion</span>
						<span class="font-medium">4.8%</span>
					</div>
					<div class="h-2 rounded-full bg-slate-100">
						<div class="h-2 w-[72%] rounded-full bg-slate-950"></div>
					</div>
				</div>
				<div>
					<div class="mb-1 flex justify-between text-sm">
						<span class="text-slate-600">Payment success</span>
						<span class="font-medium">98.2%</span>
					</div>
					<div class="h-2 rounded-full bg-slate-100">
						<div class="h-2 w-[92%] rounded-full bg-emerald-500"></div>
					</div>
				</div>
			</div>
		</Card>
	</div>
</section>
