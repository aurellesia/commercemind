const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
const PLATFORM_AUTH_HEADERS = {
	'x-cm-role': 'platform_operator',
	'x-cm-actor': 'dev-platform-console'
};

export interface BrandSettings {
	id: number;
	brand_id: number;
	brand_name: string;
	tagline: string | null;
	logo_url: string | null;
	contact_whatsapp: string | null;
	support_email: string | null;
	business_address: string | null;
	created_at: string;
	updated_at: string;
}

export interface StorefrontSettings {
	id: number;
	brand_id: number;
	storefront_enabled: boolean;
	homepage_headline: string;
	homepage_description: string | null;
	featured_product_limit: number;
	show_out_of_stock_products: boolean;
	show_sku: boolean;
	created_at: string;
	updated_at: string;
}

export interface SeoSettings {
	id: number;
	brand_id: number;
	site_url: string;
	default_title: string;
	default_description: string | null;
	social_image_url: string | null;
	created_at: string;
	updated_at: string;
}

export interface ModuleSettings {
	id: number;
	brand_id: number;
	products_enabled: boolean;
	inventory_enabled: boolean;
	cart_enabled: boolean;
	guest_checkout_enabled: boolean;
	customer_accounts_enabled: boolean;
	payments_enabled: boolean;
	shipping_enabled: boolean;
	reports_enabled: boolean;
	created_at: string;
	updated_at: string;
}

export interface SystemSettings {
	id: number;
	brand_id: number;
	maintenance_mode: boolean;
	test_mode: boolean;
	public_catalog_enabled: boolean;
	allow_checkout: boolean;
	created_at: string;
	updated_at: string;
}

export interface Brand {
	id: number;
	name: string;
	slug: string;
	status: 'draft' | 'active' | 'suspended' | 'archived';
	plan: string;
	primary_domain: string | null;
	created_at: string;
	updated_at: string;
}

export interface BrandCreate {
	name: string;
	slug: string;
	status?: 'draft' | 'active' | 'suspended' | 'archived';
	plan?: string;
	primary_domain?: string | null;
}

export type BrandUpdate = Partial<BrandCreate>;

export interface PlatformSettings {
	tenant_brand: Brand;
	brand: BrandSettings;
	storefront: StorefrontSettings;
	seo: SeoSettings;
	modules: ModuleSettings;
	system: SystemSettings;
}

export type BrandSettingsUpdate = Partial<
	Pick<
		BrandSettings,
		'brand_name' | 'tagline' | 'logo_url' | 'contact_whatsapp' | 'support_email' | 'business_address'
	>
>;

export type StorefrontSettingsUpdate = Partial<
	Pick<
		StorefrontSettings,
		| 'storefront_enabled'
		| 'homepage_headline'
		| 'homepage_description'
		| 'featured_product_limit'
		| 'show_out_of_stock_products'
		| 'show_sku'
	>
>;

export type SeoSettingsUpdate = Partial<
	Pick<SeoSettings, 'site_url' | 'default_title' | 'default_description' | 'social_image_url'>
>;

export type ModuleSettingsUpdate = Partial<
	Pick<
		ModuleSettings,
		| 'products_enabled'
		| 'inventory_enabled'
		| 'cart_enabled'
		| 'guest_checkout_enabled'
		| 'customer_accounts_enabled'
		| 'payments_enabled'
		| 'shipping_enabled'
		| 'reports_enabled'
	>
>;

export type SystemSettingsUpdate = Partial<
	Pick<SystemSettings, 'maintenance_mode' | 'test_mode' | 'public_catalog_enabled' | 'allow_checkout'>
>;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
	const res = await fetch(`${BASE_URL}${path}`, {
		headers: {
			'Content-Type': 'application/json',
			...PLATFORM_AUTH_HEADERS,
			...(init?.headers ?? {})
		},
		...init
	});
	if (!res.ok) {
		const body = await res.text();
		throw new Error(`${res.status} ${res.statusText}: ${body}`);
	}
	return res.json() as Promise<T>;
}

function put<T>(path: string, data: unknown): Promise<T> {
	return request<T>(path, { method: 'PUT', body: JSON.stringify(data) });
}

export const platformSettingsApi = {
	get: (): Promise<PlatformSettings> => request('/platform/settings'),
	listBrands: (): Promise<Brand[]> => request('/platform/brands'),
	createBrand: (data: BrandCreate): Promise<Brand> =>
		request('/platform/brands', { method: 'POST', body: JSON.stringify(data) }),
	getBrand: (brandId: number): Promise<Brand> => request(`/platform/brands/${brandId}`),
	updateTenantBrand: (brandId: number, data: BrandUpdate): Promise<Brand> =>
		put(`/platform/brands/${brandId}`, data),
	getBrandSettings: (brandId: number): Promise<PlatformSettings> =>
		request(`/platform/brands/${brandId}/settings`),
	updateBrandScopedBrand: (brandId: number, data: BrandSettingsUpdate): Promise<BrandSettings> =>
		put(`/platform/brands/${brandId}/settings/brand`, data),
	updateBrandScopedStorefront: (
		brandId: number,
		data: StorefrontSettingsUpdate
	): Promise<StorefrontSettings> => put(`/platform/brands/${brandId}/settings/storefront`, data),
	updateBrandScopedSeo: (brandId: number, data: SeoSettingsUpdate): Promise<SeoSettings> =>
		put(`/platform/brands/${brandId}/settings/seo`, data),
	updateBrandScopedModules: (brandId: number, data: ModuleSettingsUpdate): Promise<ModuleSettings> =>
		put(`/platform/brands/${brandId}/settings/modules`, data),
	updateBrandScopedSystem: (brandId: number, data: SystemSettingsUpdate): Promise<SystemSettings> =>
		put(`/platform/brands/${brandId}/settings/system`, data),
	updateBrand: (data: BrandSettingsUpdate): Promise<BrandSettings> =>
		put('/platform/settings/brand', data),
	updateStorefront: (data: StorefrontSettingsUpdate): Promise<StorefrontSettings> =>
		put('/platform/settings/storefront', data),
	updateSeo: (data: SeoSettingsUpdate): Promise<SeoSettings> =>
		put('/platform/settings/seo', data),
	updateModules: (data: ModuleSettingsUpdate): Promise<ModuleSettings> =>
		put('/platform/settings/modules', data),
	updateSystem: (data: SystemSettingsUpdate): Promise<SystemSettings> =>
		put('/platform/settings/system', data)
};
