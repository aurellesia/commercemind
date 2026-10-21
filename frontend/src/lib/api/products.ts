const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export type ProductStatus = 'draft' | 'active' | 'archived' | 'discontinued';

export interface Product {
	id: number;
	brand_id: number;
	name: string;
	slug: string;
	sku: string | null;
	description: string | null;
	bpom_number: string | null;
	usage_instructions: string | null;
	ingredients: string | null;
	storage_instructions: string | null;
	warnings: string | null;
	net_weight: string | null;
	cost_price: string; // Internal numeric value, never show on storefront
	base_price: string; // Numeric comes back as string from JSON
	status: ProductStatus;
	created_at: string;
	updated_at: string;
}

export interface ProductImage {
	id: number;
	product_id: number;
	image_url: string;
	alt_text: string | null;
	sort_order: number;
	is_primary: boolean;
	created_at: string;
	updated_at: string;
}

export interface ProductAvailability {
	id: number;
	brand_id: number;
	name: string;
	slug: string;
	sku: string | null;
	description: string | null;
	status: ProductStatus;
	base_price: string;
	effective_price: string | null;
	primary_image: ProductImage | null;
	on_hand_quantity: number;
	reserved_quantity: number;
	available_quantity: number;
	is_low_stock: boolean;
	is_purchasable: boolean;
	not_purchasable_reason: string | null;
}

export interface ProductStorefrontDetail extends ProductAvailability {
	bpom_number: string | null;
	usage_instructions: string | null;
	ingredients: string | null;
	storage_instructions: string | null;
	warnings: string | null;
	net_weight: string | null;
	images: ProductImage[];
}

export interface ProductCreate {
	brand_id?: number;
	name: string;
	slug?: string | null;
	sku?: string | null;
	description?: string | null;
	bpom_number?: string | null;
	usage_instructions?: string | null;
	ingredients?: string | null;
	storage_instructions?: string | null;
	warnings?: string | null;
	net_weight?: string | null;
	cost_price?: number;
	base_price: number;
	status?: ProductStatus;
}

export interface ProductUpdate {
	brand_id?: number;
	name?: string;
	slug?: string | null;
	sku?: string | null;
	description?: string | null;
	bpom_number?: string | null;
	usage_instructions?: string | null;
	ingredients?: string | null;
	storage_instructions?: string | null;
	warnings?: string | null;
	net_weight?: string | null;
	cost_price?: number;
	base_price?: number;
	status?: ProductStatus;
}

export interface ProductImageCreate {
	product_id: number;
	image_url: string;
	alt_text?: string | null;
	sort_order?: number;
	is_primary?: boolean;
}

export interface ProductImageUpdate {
	image_url?: string;
	alt_text?: string | null;
	sort_order?: number;
	is_primary?: boolean;
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

export const productsApi = {
	list: (skip = 0, limit = 100, brandId = 1): Promise<Product[]> =>
		request(`/products/?skip=${skip}&limit=${limit}&brand_id=${brandId}`),

	get: (id: number): Promise<Product> => request(`/products/${id}`),

	catalog: (
		skip = 0,
		limit = 100,
		includeNonPublic = false,
		brandId = 1
	): Promise<ProductAvailability[]> =>
		request(
			`/products/catalog?skip=${skip}&limit=${limit}&include_non_public=${includeNonPublic}&brand_id=${brandId}`
		),

	getAvailability: (id: number): Promise<ProductAvailability> =>
		request(`/products/${id}/availability`),

	getBySlug: (slug: string, brandId = 1): Promise<ProductAvailability> =>
		request(`/products/by-slug/${slug}?brand_id=${brandId}`),

	getDetailBySlug: (slug: string, brandId = 1): Promise<ProductStorefrontDetail> =>
		request(`/products/by-slug/${slug}/detail?brand_id=${brandId}`),

	create: (data: ProductCreate): Promise<Product> =>
		request('/products/', { method: 'POST', body: JSON.stringify(data) }),

	update: (id: number, data: ProductUpdate): Promise<Product> =>
		request(`/products/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

	archive: (id: number): Promise<Product> =>
		request(`/products/${id}/archive`, { method: 'PATCH' }),

	discontinue: (id: number): Promise<Product> =>
		request(`/products/${id}/discontinue`, { method: 'PATCH' }),

	reactivate: (id: number): Promise<Product> =>
		request(`/products/${id}/reactivate`, { method: 'PATCH' }),

	remove: (id: number): Promise<Product> =>
		request(`/products/${id}`, { method: 'DELETE' }),

	listImages: (productId: number): Promise<ProductImage[]> =>
		request(`/products/${productId}/images`),

	addImage: (productId: number, data: ProductImageCreate): Promise<ProductImage> =>
		request(`/products/${productId}/images`, { method: 'POST', body: JSON.stringify(data) }),

	updateImage: (
		productId: number,
		imageId: number,
		data: ProductImageUpdate
	): Promise<ProductImage> =>
		request(`/products/${productId}/images/${imageId}`, {
			method: 'PUT',
			body: JSON.stringify(data)
		}),

	removeImage: (productId: number, imageId: number): Promise<ProductImage> =>
		request(`/products/${productId}/images/${imageId}`, { method: 'DELETE' }),

	setPrimaryImage: (productId: number, imageId: number): Promise<ProductImage> =>
		request(`/products/${productId}/images/${imageId}/primary`, { method: 'PATCH' })
};
