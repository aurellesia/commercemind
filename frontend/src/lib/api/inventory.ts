const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export type InventoryReservationStatus = 'active' | 'released' | 'committed' | 'expired';

export type InventoryMovementType =
	| 'inbound'
	| 'reservation'
	| 'release'
	| 'deduction'
	| 'adjustment'
	| 'return';

export interface InventoryItem {
	id: number;
	product_id: number;
	on_hand_quantity: number;
	reserved_quantity: number;
	low_stock_threshold: number;
	available_quantity: number;
	is_low_stock: boolean;
	created_at: string;
	updated_at: string;
}

export interface InventoryMovement {
	id: number;
	product_id: number;
	quantity: number;
	movement_type: InventoryMovementType;
	reference_type: string | null;
	reference_id: number | null;
	notes: string | null;
	created_at: string;
	updated_at: string;
}

export interface InventoryReservation {
	id: number;
	product_id: number;
	order_id: number;
	order_item_id: number | null;
	quantity: number;
	status: InventoryReservationStatus;
	expires_at: string | null;
	created_at: string;
	updated_at: string;
}

export interface ReceiveStockCommand {
	product_id: number;
	quantity: number;
	reference_type?: string | null;
	reference_id?: number | null;
	notes?: string | null;
}

export interface AdjustStockCommand {
	product_id: number;
	delta: number;
	reference_type?: string | null;
	reference_id?: number | null;
	notes?: string | null;
}

export interface ReserveStockCommand {
	product_id: number;
	order_id: number;
	order_item_id?: number | null;
	quantity: number;
	expires_at?: string | null;
	notes?: string | null;
}

export interface ReleaseReservationCommand {
	reservation_id: number;
	notes?: string | null;
}

export interface CommitReservationCommand {
	reservation_id: number;
	notes?: string | null;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
	const res = await fetch(`${BASE_URL}${path}`, {
		headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
		...init
	});
	if (!res.ok) {
		const body = await res.text();
		throw new Error(`${res.status} ${res.statusText}: ${body}`);
	}
	return res.json() as Promise<T>;
}

function paginationQuery(skip: number, limit: number): string {
	return `skip=${skip}&limit=${limit}`;
}

export const inventoryApi = {
	list: (skip = 0, limit = 100): Promise<InventoryItem[]> =>
		request(`/inventory-items/?${paginationQuery(skip, limit)}`),

	getByProduct: (productId: number): Promise<InventoryItem> =>
		request(`/inventory-items/by-product/${productId}`),

	lowStock: (skip = 0, limit = 100): Promise<InventoryItem[]> =>
		request(`/inventory-items/low-stock?${paginationQuery(skip, limit)}`),

	movementsByProduct: (
		productId: number,
		skip = 0,
		limit = 100
	): Promise<InventoryMovement[]> =>
		request(`/inventory-items/by-product/${productId}/movements?${paginationQuery(skip, limit)}`),

	activeReservationsByProduct: (
		productId: number,
		skip = 0,
		limit = 100
	): Promise<InventoryReservation[]> =>
		request(
			`/inventory-items/by-product/${productId}/reservations/active?${paginationQuery(skip, limit)}`
		),

	activeReservationsByOrder: (
		orderId: number,
		skip = 0,
		limit = 100
	): Promise<InventoryReservation[]> =>
		request(`/inventory-items/by-order/${orderId}/reservations/active?${paginationQuery(skip, limit)}`),

	receiveStock: (data: ReceiveStockCommand): Promise<InventoryItem> =>
		request('/inventory-items/actions/receive', { method: 'POST', body: JSON.stringify(data) }),

	adjustStock: (data: AdjustStockCommand): Promise<InventoryItem> =>
		request('/inventory-items/actions/adjust', { method: 'POST', body: JSON.stringify(data) }),

	reserveStock: (data: ReserveStockCommand): Promise<InventoryReservation> =>
		request('/inventory-items/actions/reserve', { method: 'POST', body: JSON.stringify(data) }),

	releaseReservation: (data: ReleaseReservationCommand): Promise<InventoryReservation> =>
		request('/inventory-items/actions/release-reservation', {
			method: 'POST',
			body: JSON.stringify(data)
		}),

	commitReservation: (data: CommitReservationCommand): Promise<InventoryReservation> =>
		request('/inventory-items/actions/commit-reservation', {
			method: 'POST',
			body: JSON.stringify(data)
		})
};
