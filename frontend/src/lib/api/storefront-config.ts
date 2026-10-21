const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export interface PublicStorefrontModules {
	products_enabled: boolean;
	inventory_enabled: boolean;
	cart_enabled: boolean;
	guest_checkout_enabled: boolean;
	customer_accounts_enabled: boolean;
	payments_enabled: boolean;
	shipping_enabled: boolean;
}

export interface PublicStorefrontConfig {
	brand_id: number;
	brand_slug: string;
	brand_name: string;
	tagline: string | null;
	logo_url: string | null;
	contact_whatsapp: string | null;
	storefront_enabled: boolean;
	homepage_headline: string;
	homepage_description: string | null;
	featured_product_limit: number;
	show_out_of_stock_products: boolean;
	show_sku: boolean;
	site_url: string;
	default_title: string;
	default_description: string | null;
	social_image_url: string | null;
	public_catalog_enabled: boolean;
	allow_checkout: boolean;
	modules: PublicStorefrontModules;
}

export const fallbackPublicStorefrontConfig: PublicStorefrontConfig = {
	brand_id: 1,
	brand_slug: 'default',
	brand_name: 'CommerceMind',
	tagline: 'Template toko online untuk katalog produk yang rapi.',
	logo_url: null,
	contact_whatsapp: null,
	storefront_enabled: true,
	homepage_headline: 'Katalog produk dengan stok dan harga yang jelas.',
	homepage_description:
		'Gunakan storefront ini sebagai template toko untuk skincare, fashion, aksesoris, atau brand lain.',
	featured_product_limit: 3,
	show_out_of_stock_products: true,
	show_sku: true,
	site_url: 'http://localhost:5173',
	default_title: 'CommerceMind',
	default_description:
		'CommerceMind adalah template storefront ecommerce untuk menampilkan produk, harga, stok, dan detail katalog secara rapi.',
	social_image_url: null,
	public_catalog_enabled: true,
	allow_checkout: false,
	modules: {
		products_enabled: true,
		inventory_enabled: true,
		cart_enabled: false,
		guest_checkout_enabled: false,
		customer_accounts_enabled: false,
		payments_enabled: true,
		shipping_enabled: false
	}
};

const configCache = new Map<string, Promise<PublicStorefrontConfig>>();

export async function getPublicStorefrontConfig(
	brandSlug = 'default'
): Promise<PublicStorefrontConfig> {
	const cacheKey = brandSlug || 'default';
	const cached = configCache.get(cacheKey);
	if (cached) return cached;

	const request = fetchPublicStorefrontConfig(cacheKey);
	configCache.set(cacheKey, request);
	return request;
}

async function fetchPublicStorefrontConfig(brandSlug: string): Promise<PublicStorefrontConfig> {
	try {
		const res = await fetch(`${BASE_URL}/storefront/${brandSlug}/config`);
		if (!res.ok) {
			const body = await res.text();
			throw new Error(`${res.status} ${res.statusText}: ${body}`);
		}
		return res.json() as Promise<PublicStorefrontConfig>;
	} catch (error) {
		if (error instanceof Error && /^\d{3}\s/.test(error.message)) {
			throw error;
		}
		return {
			...fallbackPublicStorefrontConfig,
			brand_slug: brandSlug,
			brand_name:
				brandSlug === 'default'
					? fallbackPublicStorefrontConfig.brand_name
					: brandSlug.replace(/-/g, ' ')
		};
	}
}
