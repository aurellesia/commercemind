from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend import models
from backend import schemas
from backend.crud import (
    create_brand,
    get_product_availability_by_slug,
    get_product_catalog,
    get_product_storefront_detail_by_slug,
)
from backend.database import Base


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    TestingSession = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


def create_product(db, name: str, status: str, brand_id: int = 1):
    product = models.Product(
        brand_id=brand_id,
        name=name,
        slug=name.lower().replace(" ", "-"),
        base_price=Decimal("10000"),
        status=status,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def test_public_catalog_only_returns_active_products(db_session):
    active = create_product(db_session, "Active Product", "active")
    create_product(db_session, "Draft Product", "draft")
    create_product(db_session, "Archived Product", "archived")
    create_product(db_session, "Discontinued Product", "discontinued")

    catalog = get_product_catalog(db_session)

    assert [product.id for product in catalog] == [active.id]
    assert all(not hasattr(product, "cost_price") for product in catalog)


def test_admin_catalog_can_include_non_public_products(db_session):
    active = create_product(db_session, "Active Product", "active")
    draft = create_product(db_session, "Draft Product", "draft")
    archived = create_product(db_session, "Archived Product", "archived")
    discontinued = create_product(db_session, "Discontinued Product", "discontinued")

    catalog = get_product_catalog(db_session, include_non_public=True)

    assert {product.id for product in catalog} == {
        active.id,
        draft.id,
        archived.id,
        discontinued.id,
    }


def test_storefront_slug_detail_rejects_non_active_products(db_session):
    active = create_product(db_session, "Active Product", "active")
    draft = create_product(db_session, "Draft Product", "draft")
    archived = create_product(db_session, "Archived Product", "archived")
    discontinued = create_product(db_session, "Discontinued Product", "discontinued")

    assert get_product_availability_by_slug(db_session, active.slug) is not None
    assert get_product_storefront_detail_by_slug(db_session, active.slug) is not None

    for product in (draft, archived, discontinued):
        assert get_product_availability_by_slug(db_session, product.slug) is None
        assert get_product_storefront_detail_by_slug(db_session, product.slug) is None


def test_public_catalog_keeps_active_out_of_stock_with_clear_label(db_session):
    product = create_product(db_session, "Out Of Stock Product", "active")

    catalog = get_product_catalog(db_session)
    catalog_product = next(item for item in catalog if item.id == product.id)

    assert catalog_product.available_quantity == 0
    assert catalog_product.is_purchasable is False
    assert catalog_product.not_purchasable_reason == "Product is out of stock"


def test_public_catalog_uses_effective_price_with_base_price_fallback(db_session):
    with_price_set = create_product(db_session, "Price Set Product", "active")
    fallback = create_product(db_session, "Fallback Price Product", "active")
    price_set = models.PriceSet(
        product_id=with_price_set.id,
        name="Public price",
        is_active=True,
    )
    db_session.add(price_set)
    db_session.flush()
    db_session.add(
        models.PriceSetItem(
            price_set_id=price_set.id,
            price=Decimal("7500"),
            currency="IDR",
            priority=10,
            is_active=True,
        )
    )
    db_session.commit()

    catalog_by_id = {item.id: item for item in get_product_catalog(db_session)}

    assert catalog_by_id[with_price_set.id].effective_price == Decimal("7500")
    assert catalog_by_id[fallback.id].effective_price == fallback.base_price


def test_storefront_detail_returns_primary_image_and_gallery(db_session):
    product = create_product(db_session, "Gallery Product", "active")
    secondary = models.ProductImage(
        product_id=product.id,
        image_url="https://example.test/secondary.jpg",
        alt_text="Secondary image",
        sort_order=2,
        is_primary=False,
    )
    primary = models.ProductImage(
        product_id=product.id,
        image_url="https://example.test/primary.jpg",
        alt_text="Primary image",
        sort_order=1,
        is_primary=True,
    )
    db_session.add_all([secondary, primary])
    db_session.commit()

    detail = get_product_storefront_detail_by_slug(db_session, product.slug)

    assert detail is not None
    assert detail.primary_image is not None
    assert detail.primary_image.image_url == "https://example.test/primary.jpg"
    assert [image.image_url for image in detail.images] == [
        "https://example.test/primary.jpg",
        "https://example.test/secondary.jpg",
    ]


def test_brand_scoped_catalog_allows_same_slug_and_isolates_products(db_session):
    brand_a = create_brand(
        db_session,
        schemas.BrandCreate(name="Brand A", slug="brand-a", status="active", plan="starter"),
    )
    brand_b = create_brand(
        db_session,
        schemas.BrandCreate(name="Brand B", slug="brand-b", status="active", plan="starter"),
    )
    product_a = create_product(db_session, "Shared Product", "active", brand_id=brand_a.id)
    product_b = create_product(db_session, "Shared Product", "active", brand_id=brand_b.id)

    catalog_a = get_product_catalog(db_session, brand_id=brand_a.id)
    catalog_b = get_product_catalog(db_session, brand_id=brand_b.id)
    detail_a = get_product_storefront_detail_by_slug(
        db_session,
        product_a.slug,
        brand_id=brand_a.id,
    )
    detail_b = get_product_storefront_detail_by_slug(
        db_session,
        product_b.slug,
        brand_id=brand_b.id,
    )

    assert product_a.slug == product_b.slug
    assert [product.id for product in catalog_a] == [product_a.id]
    assert [product.id for product in catalog_b] == [product_b.id]
    assert detail_a is not None and detail_a.id == product_a.id
    assert detail_b is not None and detail_b.id == product_b.id
