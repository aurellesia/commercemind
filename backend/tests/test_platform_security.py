import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend import schemas
from backend.api.settings import update_brand_scoped_storefront_settings
from backend.crud import create_brand, get_audit_logs
from backend.database import Base
from backend.security import AuthContext, require_merchant_brand_access, require_platform_access


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


def test_platform_access_requires_platform_operator_role():
    with pytest.raises(HTTPException) as missing_role:
        require_platform_access(x_cm_role=None, x_cm_actor=None, x_cm_brand_id=None)
    with pytest.raises(HTTPException) as merchant_role:
        require_platform_access(x_cm_role="merchant_admin", x_cm_actor="merchant")

    context = require_platform_access(x_cm_role="platform_operator", x_cm_actor="aurel")

    assert missing_role.value.status_code == 401
    assert merchant_role.value.status_code == 403
    assert context.actor == "aurel"


def test_merchant_brand_access_requires_matching_brand():
    context = AuthContext(role="merchant_admin", actor="merchant", brand_id=7)

    assert require_merchant_brand_access(7, context) == context
    with pytest.raises(HTTPException) as exc:
        require_merchant_brand_access(8, context)

    assert exc.value.status_code == 403


def test_platform_setting_update_writes_audit_log(db_session):
    brand = create_brand(
        db_session,
        schemas.BrandCreate(name="Audit Brand", slug="audit-brand"),
    )
    auth = AuthContext(role="platform_operator", actor="aurel")

    updated = update_brand_scoped_storefront_settings(
        brand.id,
        schemas.StorefrontSettingsUpdate(homepage_headline="New public headline"),
        db=db_session,
        auth=auth,
    )
    audit_logs = get_audit_logs(db_session, brand_id=brand.id)

    assert updated.homepage_headline == "New public headline"
    assert audit_logs[0].actor == "aurel"
    assert audit_logs[0].action == "storefront_settings.update"
    assert audit_logs[0].before_value["homepage_headline"] != "New public headline"
    assert audit_logs[0].after_value["homepage_headline"] == "New public headline"
