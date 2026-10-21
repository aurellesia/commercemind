from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from fastapi import Header, HTTPException


PLATFORM_OPERATOR = "platform_operator"
MERCHANT_ADMIN = "merchant_admin"
MERCHANT_STAFF = "merchant_staff"
CUSTOMER = "customer"

MERCHANT_ROLES = {MERCHANT_ADMIN, MERCHANT_STAFF}
KNOWN_ROLES = {PLATFORM_OPERATOR, MERCHANT_ADMIN, MERCHANT_STAFF, CUSTOMER}


@dataclass(frozen=True)
class AuthContext:
    role: str
    actor: str
    brand_id: Optional[int] = None


def get_auth_context(
    x_cm_role: Optional[str] = Header(default=None),
    x_cm_actor: Optional[str] = Header(default=None),
    x_cm_brand_id: Optional[int] = Header(default=None),
) -> AuthContext:
    role = (x_cm_role or "").strip()
    if role not in KNOWN_ROLES:
        raise HTTPException(status_code=401, detail="Authentication role is required")
    return AuthContext(
        role=role,
        actor=(x_cm_actor or role).strip() or role,
        brand_id=x_cm_brand_id,
    )


def require_platform_access(
    x_cm_role: Optional[str] = Header(default=None),
    x_cm_actor: Optional[str] = Header(default=None),
    x_cm_brand_id: Optional[int] = Header(default=None),
) -> AuthContext:
    context = get_auth_context(
        x_cm_role=x_cm_role,
        x_cm_actor=x_cm_actor,
        x_cm_brand_id=x_cm_brand_id,
    )
    if context.role != PLATFORM_OPERATOR:
        raise HTTPException(status_code=403, detail="Platform operator access required")
    return context


def require_merchant_brand_access(
    brand_id: int,
    context: AuthContext,
) -> AuthContext:
    if context.role == PLATFORM_OPERATOR:
        return context
    if context.role not in MERCHANT_ROLES:
        raise HTTPException(status_code=403, detail="Merchant access required")
    if context.brand_id != brand_id:
        raise HTTPException(status_code=403, detail="Brand access denied")
    return context
