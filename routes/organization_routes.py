# organization_routes.py - Organization Profile CRUD
"""
Per-user organization profile.  Stored once, auto-fills Party A on every new contract.

Endpoints:
    GET    /api/organization          — Get current user's profile (404 if none yet)
    PUT    /api/organization          — Upsert profile (create or update)
    DELETE /api/organization          — Delete profile
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from psycopg2.extras import RealDictCursor

from config import get_connection
from auth_middleware import get_current_user

router = APIRouter(prefix="/api/organization", tags=["organization"])


# ==================== TABLE AUTO-CREATION ====================

def _ensure_table():
    """Create organization_profiles table if it doesn't exist. Called once at startup."""
    DDL = """
    CREATE TABLE IF NOT EXISTS organization_profiles (
        id                  SERIAL PRIMARY KEY,
        user_id             UUID NOT NULL,
        company_name        TEXT NOT NULL,
        legal_entity_type   TEXT,
        registration_number TEXT,
        address_line1       TEXT,
        address_line2       TEXT,
        city                TEXT,
        state               TEXT,
        postal_code         TEXT,
        country             TEXT NOT NULL DEFAULT 'India',
        signatory_name          TEXT,
        signatory_designation   TEXT,
        email               TEXT,
        phone               TEXT,
        pan                 TEXT,
        gst                 TEXT,
        created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        CONSTRAINT uq_org_profile_user UNIQUE (user_id)
    );
    CREATE INDEX IF NOT EXISTS idx_org_profiles_user_id ON organization_profiles (user_id);
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
        conn.commit()


# ==================== PYDANTIC MODELS ====================

class OrgProfileRequest(BaseModel):
    company_name: str
    legal_entity_type: Optional[str] = None       # company/llp/individual/partnership
    registration_number: Optional[str] = None      # CIN, LLPIN, etc.
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = "India"
    signatory_name: Optional[str] = None
    signatory_designation: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    pan: Optional[str] = None
    gst: Optional[str] = None


class OrgProfileResponse(BaseModel):
    id: int
    user_id: str
    company_name: str
    legal_entity_type: Optional[str]
    registration_number: Optional[str]
    address_line1: Optional[str]
    address_line2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]
    signatory_name: Optional[str]
    signatory_designation: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    pan: Optional[str]
    gst: Optional[str]


# ==================== ROUTES ====================

@router.get("", response_model=OrgProfileResponse)
async def get_org_profile(user=Depends(get_current_user)):
    """
    Get the current user's organization profile.
    Returns 404 if no profile has been created yet.
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM organization_profiles WHERE user_id = %s",
                (user["id"],)
            )
            profile = cur.fetchone()

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="No organization profile found. Create one with PUT /api/organization."
        )
    return dict(profile)


@router.put("", response_model=OrgProfileResponse)
async def upsert_org_profile(request: OrgProfileRequest, user=Depends(get_current_user)):
    """
    Create or update the current user's organization profile.
    Uses INSERT ... ON CONFLICT DO UPDATE (upsert).
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO organization_profiles (
                    user_id, company_name, legal_entity_type, registration_number,
                    address_line1, address_line2, city, state, postal_code, country,
                    signatory_name, signatory_designation,
                    email, phone, pan, gst
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    company_name         = EXCLUDED.company_name,
                    legal_entity_type    = EXCLUDED.legal_entity_type,
                    registration_number  = EXCLUDED.registration_number,
                    address_line1        = EXCLUDED.address_line1,
                    address_line2        = EXCLUDED.address_line2,
                    city                 = EXCLUDED.city,
                    state                = EXCLUDED.state,
                    postal_code          = EXCLUDED.postal_code,
                    country              = EXCLUDED.country,
                    signatory_name       = EXCLUDED.signatory_name,
                    signatory_designation= EXCLUDED.signatory_designation,
                    email                = EXCLUDED.email,
                    phone                = EXCLUDED.phone,
                    pan                  = EXCLUDED.pan,
                    gst                  = EXCLUDED.gst,
                    updated_at           = NOW()
                RETURNING *
            """, (
                user["id"],
                request.company_name,
                request.legal_entity_type,
                request.registration_number,
                request.address_line1,
                request.address_line2,
                request.city,
                request.state,
                request.postal_code,
                request.country or "India",
                request.signatory_name,
                request.signatory_designation,
                request.email,
                request.phone,
                request.pan,
                request.gst,
            ))
            profile = cur.fetchone()
            conn.commit()

    return dict(profile)


@router.delete("")
async def delete_org_profile(user=Depends(get_current_user)):
    """Delete the current user's organization profile."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM organization_profiles WHERE user_id = %s RETURNING id",
                (user["id"],)
            )
            deleted = cur.fetchone()
            if not deleted:
                raise HTTPException(status_code=404, detail="No organization profile found")
            conn.commit()

    return {"message": "Organization profile deleted successfully"}
