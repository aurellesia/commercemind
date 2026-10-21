from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db


router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=schemas.Product, status_code=201)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db=db, product=product)


@router.get("/", response_model=List[schemas.Product])
def read_products(
    skip: int = 0,
    limit: int = 100,
    brand_id: int = 1,
    db: Session = Depends(get_db),
):
    return crud.get_products(db, skip=skip, limit=limit, brand_id=brand_id)


@router.get("/catalog", response_model=List[schemas.ProductAvailability])
def read_product_catalog(
    skip: int = 0,
    limit: int = 100,
    include_non_public: bool = False,
    brand_id: int = 1,
    db: Session = Depends(get_db),
):
    settings = crud.get_platform_settings(db, brand_id=brand_id)
    if settings is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    if not include_non_public and (
        not settings.system.public_catalog_enabled or not settings.modules.products_enabled
    ):
        raise HTTPException(status_code=403, detail="Public catalog is disabled")

    return crud.get_product_catalog(
        db,
        skip=skip,
        limit=limit,
        include_non_public=include_non_public,
        brand_id=brand_id,
    )


@router.get("/by-slug/{slug}", response_model=schemas.ProductAvailability)
def read_product_by_slug(slug: str, brand_id: int = 1, db: Session = Depends(get_db)):
    product_availability = crud.get_product_availability_by_slug(
        db,
        slug=slug,
        brand_id=brand_id,
    )
    if product_availability is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product_availability


@router.get("/by-slug/{slug}/detail", response_model=schemas.ProductStorefrontDetail)
def read_product_storefront_detail_by_slug(
    slug: str,
    brand_id: int = 1,
    db: Session = Depends(get_db),
):
    product_detail = crud.get_product_storefront_detail_by_slug(
        db,
        slug=slug,
        brand_id=brand_id,
    )
    if product_detail is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product_detail


@router.get("/{product_id}/availability", response_model=schemas.ProductAvailability)
def read_product_availability(product_id: int, db: Session = Depends(get_db)):
    product_availability = crud.get_product_availability(db, product_id=product_id)
    if product_availability is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product_availability


@router.get("/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/{product_id}/images", response_model=List[schemas.ProductImage])
def read_product_images(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return crud.get_product_images_by_product_id(db, product_id=product_id)


@router.post(
    "/{product_id}/images",
    response_model=schemas.ProductImage,
    status_code=201,
)
def create_product_image(
    product_id: int,
    product_image: schemas.ProductImageCreate,
    db: Session = Depends(get_db),
):
    product = crud.get_product(db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if product_image.product_id != product_id:
        raise HTTPException(status_code=400, detail="Image product_id does not match path")
    return crud.create_product_image(db=db, product_image=product_image)


@router.put("/{product_id}/images/{image_id}", response_model=schemas.ProductImage)
def update_product_image(
    product_id: int,
    image_id: int,
    product_image: schemas.ProductImageUpdate,
    db: Session = Depends(get_db),
):
    _require_product_image(db, product_id=product_id, image_id=image_id)
    updated_product_image = crud.update_product_image(
        db,
        product_image_id=image_id,
        product_image=product_image,
    )
    if updated_product_image is None:
        raise HTTPException(status_code=404, detail="Product image not found")
    return updated_product_image


@router.patch(
    "/{product_id}/images/{image_id}/primary",
    response_model=schemas.ProductImage,
)
def set_primary_product_image(
    product_id: int,
    image_id: int,
    db: Session = Depends(get_db),
):
    _require_product_image(db, product_id=product_id, image_id=image_id)
    primary_product_image = crud.set_primary_product_image(db, product_image_id=image_id)
    if primary_product_image is None:
        raise HTTPException(status_code=404, detail="Product image not found")
    return primary_product_image


@router.delete("/{product_id}/images/{image_id}", response_model=schemas.ProductImage)
def delete_product_image(product_id: int, image_id: int, db: Session = Depends(get_db)):
    _require_product_image(db, product_id=product_id, image_id=image_id)
    deleted_product_image = crud.delete_product_image(db, product_image_id=image_id)
    if deleted_product_image is None:
        raise HTTPException(status_code=404, detail="Product image not found")
    return deleted_product_image


@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int,
    product: schemas.ProductUpdate,
    db: Session = Depends(get_db),
):
    updated_product = crud.update_product(db, product_id=product_id, product=product)
    if updated_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product


@router.patch("/{product_id}/archive", response_model=schemas.Product)
def archive_product(product_id: int, db: Session = Depends(get_db)):
    archived_product = crud.archive_product(db, product_id=product_id)
    if archived_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return archived_product


@router.patch("/{product_id}/discontinue", response_model=schemas.Product)
def discontinue_product(product_id: int, db: Session = Depends(get_db)):
    discontinued_product = crud.discontinue_product(db, product_id=product_id)
    if discontinued_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return discontinued_product


@router.patch("/{product_id}/reactivate", response_model=schemas.Product)
def reactivate_product(product_id: int, db: Session = Depends(get_db)):
    reactivated_product = crud.reactivate_product(db, product_id=product_id)
    if reactivated_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return reactivated_product


@router.delete("/{product_id}", response_model=schemas.Product)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    try:
        deleted_product = crud.delete_product(db, product_id=product_id)
    except crud.ProductDeleteBlockedError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if deleted_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return deleted_product


def _require_product_image(db: Session, product_id: int, image_id: int):
    product = crud.get_product(db, product_id=product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    product_image = crud.get_product_image(db, product_image_id=image_id)
    if product_image is None:
        raise HTTPException(status_code=404, detail="Product image not found")
    if product_image.product_id != product_id:
        raise HTTPException(status_code=404, detail="Product image not found")
    return product_image
