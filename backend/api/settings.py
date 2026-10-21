from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..security import AuthContext, require_platform_access


platform_settings_router = APIRouter(
    prefix="/platform/settings",
    tags=["platform settings"],
)
platform_brands_router = APIRouter(
    prefix="/platform/brands",
    tags=["platform brands"],
)
storefront_router = APIRouter(prefix="/storefront", tags=["storefront"])


@platform_settings_router.get("", response_model=schemas.PlatformSettings)
def read_platform_settings(
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_platform_access),
):
    return crud.get_platform_settings(db)


@platform_settings_router.put("/brand", response_model=schemas.BrandSettings)
def update_brand_settings(
    settings: schemas.BrandSettingsUpdate,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_platform_access),
):
    return crud.update_brand_settings(db, settings=settings, actor=auth.actor, role=auth.role)


@platform_settings_router.put("/storefront", response_model=schemas.StorefrontSettings)
def update_storefront_settings(
    settings: schemas.StorefrontSettingsUpdate,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_platform_access),
):
    return crud.update_storefront_settings(db, settings=settings, actor=auth.actor, role=auth.role)


@platform_settings_router.put("/seo", response_model=schemas.SeoSettings)
def update_seo_settings(
    settings: schemas.SeoSettingsUpdate,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_platform_access),
):
    return crud.update_seo_settings(db, settings=settings, actor=auth.actor, role=auth.role)


@platform_settings_router.put("/modules", response_model=schemas.ModuleSettings)
def update_module_settings(
    settings: schemas.ModuleSettingsUpdate,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_platform_access),
):
    return crud.update_module_settings(db, settings=settings, actor=auth.actor, role=auth.role)


@platform_settings_router.put("/system", response_model=schemas.SystemSettings)
def update_system_settings(
    settings: schemas.SystemSettingsUpdate,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_platform_access),
):
    return crud.update_system_settings(db, settings=settings, actor=auth.actor, role=auth.role)


@platform_settings_router.get("/audit-logs", response_model=List[schemas.AuditLog])
def read_audit_logs(
    brand_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_platform_access),
):
    return crud.get_audit_logs(db, brand_id=brand_id, skip=skip, limit=limit)


@platform_brands_router.get("", response_model=List[schemas.Brand])
def read_brands(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_platform_access),
):
    return crud.get_brands(db, skip=skip, limit=limit)


@platform_brands_router.post("", response_model=schemas.Brand, status_code=201)
def create_brand(
    brand: schemas.BrandCreate,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_platform_access),
):
    return crud.create_brand(db, brand=brand, actor=auth.actor, role=auth.role)


@platform_brands_router.get("/{brand_id}", response_model=schemas.Brand)
def read_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_platform_access),
):
    brand = crud.get_brand(db, brand_id=brand_id)
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@platform_brands_router.put("/{brand_id}", response_model=schemas.Brand)
def update_brand(
    brand_id: int,
    brand: schemas.BrandUpdate,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_platform_access),
):
    updated_brand = crud.update_brand(
        db,
        brand_id=brand_id,
        brand=brand,
        actor=auth.actor,
        role=auth.role,
    )
    if updated_brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return updated_brand


@platform_brands_router.get("/{brand_id}/settings", response_model=schemas.PlatformSettings)
def read_brand_platform_settings(
    brand_id: int,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_platform_access),
):
    settings = crud.get_platform_settings(db, brand_id=brand_id)
    if settings is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return settings


@platform_brands_router.put("/{brand_id}/settings/brand", response_model=schemas.BrandSettings)
def update_brand_scoped_brand_settings(
    brand_id: int,
    settings: schemas.BrandSettingsUpdate,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_platform_access),
):
    updated = crud.update_brand_settings(
        db,
        settings=settings,
        brand_id=brand_id,
        actor=auth.actor,
        role=auth.role,
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return updated


@platform_brands_router.put("/{brand_id}/settings/storefront", response_model=schemas.StorefrontSettings)
def update_brand_scoped_storefront_settings(
    brand_id: int,
    settings: schemas.StorefrontSettingsUpdate,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_platform_access),
):
    updated = crud.update_storefront_settings(
        db,
        settings=settings,
        brand_id=brand_id,
        actor=auth.actor,
        role=auth.role,
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return updated


@platform_brands_router.put("/{brand_id}/settings/seo", response_model=schemas.SeoSettings)
def update_brand_scoped_seo_settings(
    brand_id: int,
    settings: schemas.SeoSettingsUpdate,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_platform_access),
):
    updated = crud.update_seo_settings(
        db,
        settings=settings,
        brand_id=brand_id,
        actor=auth.actor,
        role=auth.role,
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return updated


@platform_brands_router.put("/{brand_id}/settings/modules", response_model=schemas.ModuleSettings)
def update_brand_scoped_module_settings(
    brand_id: int,
    settings: schemas.ModuleSettingsUpdate,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_platform_access),
):
    updated = crud.update_module_settings(
        db,
        settings=settings,
        brand_id=brand_id,
        actor=auth.actor,
        role=auth.role,
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return updated


@platform_brands_router.put("/{brand_id}/settings/system", response_model=schemas.SystemSettings)
def update_brand_scoped_system_settings(
    brand_id: int,
    settings: schemas.SystemSettingsUpdate,
    db: Session = Depends(get_db),
    auth: AuthContext = Depends(require_platform_access),
):
    updated = crud.update_system_settings(
        db,
        settings=settings,
        brand_id=brand_id,
        actor=auth.actor,
        role=auth.role,
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return updated


@storefront_router.get("/config", response_model=schemas.PublicStorefrontConfig)
def read_public_storefront_config(db: Session = Depends(get_db)):
    return crud.get_public_storefront_config(db)


@storefront_router.get("/{brand_slug}/config", response_model=schemas.PublicStorefrontConfig)
def read_brand_public_storefront_config(
    brand_slug: str,
    db: Session = Depends(get_db),
):
    config = crud.get_public_storefront_config(db, brand_slug=brand_slug)
    if config is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return config
