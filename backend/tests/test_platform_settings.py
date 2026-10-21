import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend import schemas
from backend.crud import (
    create_brand,
    get_platform_settings,
    get_public_storefront_config,
    update_brand_settings,
    update_module_settings,
    update_storefront_settings,
    update_system_settings,
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


def test_get_platform_settings_creates_defaults(db_session):
    settings = get_platform_settings(db_session)

    assert settings.brand.brand_name == "CommerceMind"
    assert settings.storefront.storefront_enabled is True
    assert settings.modules.cart_enabled is False
    assert settings.system.public_catalog_enabled is True


def test_update_settings_and_public_config_exposes_only_safe_fields(db_session):
    update_brand_settings(
        db_session,
        schemas.BrandSettingsUpdate(
            brand_name="Acme Store",
            contact_whatsapp="6281234567890",
            support_email="private@example.test",
        ),
    )
    update_storefront_settings(
        db_session,
        schemas.StorefrontSettingsUpdate(
            homepage_headline="Produk pilihan Acme",
            featured_product_limit=6,
            show_sku=False,
        ),
    )
    update_module_settings(
        db_session,
        schemas.ModuleSettingsUpdate(cart_enabled=True, reports_enabled=False),
    )
    update_system_settings(
        db_session,
        schemas.SystemSettingsUpdate(
            public_catalog_enabled=False,
            maintenance_mode=True,
        ),
    )

    public_config = get_public_storefront_config(db_session)

    assert public_config.brand_name == "Acme Store"
    assert public_config.contact_whatsapp == "6281234567890"
    assert public_config.homepage_headline == "Produk pilihan Acme"
    assert public_config.featured_product_limit == 6
    assert public_config.show_sku is False
    assert public_config.modules.cart_enabled is True
    assert public_config.public_catalog_enabled is False
    assert not hasattr(public_config, "support_email")
    assert not hasattr(public_config, "maintenance_mode")
    assert not hasattr(public_config.modules, "reports_enabled")


def test_brand_scoped_settings_are_isolated(db_session):
    default_settings = get_platform_settings(db_session)
    acme = create_brand(
        db_session,
        schemas.BrandCreate(
            name="Acme Store",
            slug="acme",
            status="active",
            plan="starter",
        ),
    )

    update_brand_settings(
        db_session,
        schemas.BrandSettingsUpdate(brand_name="Acme Public"),
        brand_id=acme.id,
    )

    default_config = get_public_storefront_config(
        db_session,
        brand_slug=default_settings.tenant_brand.slug,
    )
    acme_config = get_public_storefront_config(db_session, brand_slug="acme")

    assert default_config.brand_name == "CommerceMind"
    assert acme_config.brand_name == "Acme Public"
    assert acme_config.storefront_enabled is True
