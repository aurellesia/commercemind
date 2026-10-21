const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export type CustomerType = 'guest' | 'registered';
export type CustomerFilterType = CustomerType | 'all';

export interface Customer {
	id: number;
	brand_id: number;
	name: string;
	email: string | null;
	phone: string | null;
	address: string | null;
	customer_type: CustomerType;
	created_at: string;
	updated_at: string;
}

export interface CustomerCreate {
	brand_id?: number;
	name: string;
	email?: string | null;
	phone?: string | null;
	address?: string | null;
	customer_type?: CustomerType;
}

export interface CustomerUpdate {
	brand_id?: number;
	name?: string;
	email?: string | null;
	phone?: string | null;
	address?: string | null;
	customer_type?: CustomerType;
}

export interface CustomerAddress {
	id: number;
	brand_id: number;
	customer_id: number;
	recipient_name: string;
	phone: string;
	address_line: string;
	district: string;
	city: string;
	province: string;
	postal_code: string;
	notes: string | null;
	is_default: boolean;
	created_at: string;
	updated_at: string;
}

export interface CustomerAddressCreate {
	recipient_name: string;
	phone: string;
	address_line: string;
	district: string;
	city: string;
	province: string;
	postal_code: string;
	notes?: string | null;
	is_default?: boolean;
}

export type CustomerAddressUpdate = Partial<CustomerAddressCreate>;

export interface CustomerSummary extends Customer {
	total_orders: number;
	last_order_date: string | null;
	total_spent: string;
}

export interface CustomerOrderSummary {
	id: number;
	status: string;
	total_amount: string;
	created_at: string;
}

export interface CustomerDetail extends Customer {
	addresses: CustomerAddress[];
	recent_orders: CustomerOrderSummary[];
}

export interface CustomerListFilters {
	search?: string;
	customerType?: CustomerFilterType;
	skip?: number;
	limit?: number;
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

function customerQuery(brandId: number, filters: CustomerListFilters = {}): string {
	const params = new URLSearchParams({
		brand_id: String(brandId),
		skip: String(filters.skip ?? 0),
		limit: String(filters.limit ?? 100)
	});
	const search = filters.search?.trim();
	if (search) params.set('search', search);
	if (filters.customerType && filters.customerType !== 'all') {
		params.set('customer_type', filters.customerType);
	}
	return params.toString();
}

function brandQuery(brandId: number): string {
	return new URLSearchParams({ brand_id: String(brandId) }).toString();
}

export const customersApi = {
	list: (brandId: number, filters?: CustomerListFilters): Promise<Customer[]> =>
		request(`/customers/?${customerQuery(brandId, filters)}`),

	summary: (brandId: number, filters?: CustomerListFilters): Promise<CustomerSummary[]> =>
		request(`/customers/summary?${customerQuery(brandId, filters)}`),

	get: (customerId: number, brandId: number): Promise<Customer> =>
		request(`/customers/${customerId}?${brandQuery(brandId)}`),

	detail: (customerId: number, brandId: number): Promise<CustomerDetail> =>
		request(`/customers/${customerId}/detail?${brandQuery(brandId)}`),

	create: (brandId: number, data: CustomerCreate): Promise<Customer> =>
		request('/customers/', {
			method: 'POST',
			body: JSON.stringify({ ...data, brand_id: brandId })
		}),

	update: (customerId: number, brandId: number, data: CustomerUpdate): Promise<Customer> =>
		request(`/customers/${customerId}?${brandQuery(brandId)}`, {
			method: 'PUT',
			body: JSON.stringify(data)
		}),

	remove: (customerId: number, brandId: number): Promise<Customer> =>
		request(`/customers/${customerId}?${brandQuery(brandId)}`, { method: 'DELETE' }),

	listAddresses: (customerId: number, brandId: number): Promise<CustomerAddress[]> =>
		request(`/customers/${customerId}/addresses?${brandQuery(brandId)}`),

	createAddress: (
		customerId: number,
		brandId: number,
		data: CustomerAddressCreate
	): Promise<CustomerAddress> =>
		request(`/customers/${customerId}/addresses?${brandQuery(brandId)}`, {
			method: 'POST',
			body: JSON.stringify(data)
		}),

	updateAddress: (
		addressId: number,
		brandId: number,
		data: CustomerAddressUpdate
	): Promise<CustomerAddress> =>
		request(`/customers/addresses/${addressId}?${brandQuery(brandId)}`, {
			method: 'PUT',
			body: JSON.stringify(data)
		}),

	removeAddress: (addressId: number, brandId: number): Promise<CustomerAddress> =>
		request(`/customers/addresses/${addressId}?${brandQuery(brandId)}`, { method: 'DELETE' })
};
