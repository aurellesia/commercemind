import {
	productsApi,
	type ProductAvailability,
	type ProductImage,
	type ProductStorefrontDetail
} from '$lib/api/products';

export type StorefrontProduct = ProductAvailability;
export type StorefrontProductDetail = ProductStorefrontDetail;
export type StorefrontProductImage = ProductImage;

export const storefrontProductsApi = {
	catalog: productsApi.catalog,
	detailBySlug: productsApi.getDetailBySlug
};

export function formatPrice(raw: string | number | null): string {
	if (raw === null) return 'Harga segera hadir';

	const value = typeof raw === 'string' ? parseFloat(raw) : raw;
	if (!Number.isFinite(value)) return 'Harga segera hadir';

	return new Intl.NumberFormat('id-ID', {
		style: 'currency',
		currency: 'IDR',
		minimumFractionDigits: 0
	}).format(value);
}

export function storefrontPrice(product: StorefrontProduct): string {
	return formatPrice(product.effective_price ?? product.base_price);
}

export function stockLabel(product: StorefrontProduct): string {
	if (product.is_purchasable) return `${product.available_quantity} tersedia`;
	return product.not_purchasable_reason ?? 'Belum tersedia';
}

export function availabilityBadgeLabel(product: StorefrontProduct): string {
	if (product.is_purchasable) return 'Tersedia';
	if (product.status === 'active') return 'Preview';
	return 'Tidak tersedia';
}

export function productImageAlt(
	image: StorefrontProductImage | null,
	productName: string
): string {
	return image?.alt_text ?? productName;
}

export function isPubliclyVisibleProduct(product: StorefrontProduct): boolean {
	return product.status === 'active';
}

export function friendlyStorefrontError(error: unknown, fallback: string): string {
	const message = error instanceof Error ? error.message : String(error);

	if (message.includes('404')) {
		return 'Produk tidak ditemukan atau belum tersedia untuk publik.';
	}
	if (message.includes('Failed to fetch') || message.includes('NetworkError')) {
		return 'Katalog belum bisa dimuat karena server tidak terhubung. Coba lagi sebentar.';
	}
	if (message.includes('500')) {
		return 'Ada kendala di server saat memuat katalog. Coba lagi beberapa saat lagi.';
	}

	return fallback;
}
