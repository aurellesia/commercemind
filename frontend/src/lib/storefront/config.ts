import { fallbackPublicStorefrontConfig } from '$lib/api/storefront-config';

export const storefrontConfig = {
	brandName: fallbackPublicStorefrontConfig.brand_name,
	categoryLabel: 'Produk pilihan',
	tagline: fallbackPublicStorefrontConfig.tagline ?? '',
	primaryCatalogCta: 'Lihat Produk',
	siteUrl: fallbackPublicStorefrontConfig.site_url,
	defaultDescription: fallbackPublicStorefrontConfig.default_description ?? ''
};
