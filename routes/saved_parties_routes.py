# saved_parties_routes.py - Saved Party Directory CRUD
"""
Reusable party directory. Users save counterparty details once and pick them
in any future contract's Party selection, eliminating re-entry.

Endpoints:
    GET    /api/saved-parties          — List all saved parties for current user
    POST   /api/saved-parties          — Save a new party
    PUT    /api/saved-parties/{id}     — Update a saved party
    DELETE /api/saved-parties/{id}     — Delete a saved party
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from psycopg2.extras import RealDictCursor
from datetime import datetime

from config import get_connection
from auth_middleware import get_current_user

router = APIRouter(prefix="/api/saved-parties", tags=["saved-parties"])


# ==================== TABLE AUTO-CREATION ====================

def _ensure_table():
    """Create saved_parties table if it doesn't exist. Called once at startup."""
    DDL = """
    CREATE TABLE IF NOT EXISTS saved_parties (
        id                  SERIAL PRIMARY KEY,
        user_id             UUID NOT NULL,
        party_name          TEXT NOT NULL,
        legal_entity_type   TEXT,
        address_line1       TEXT,
        address_line2       TEXT,
        city                TEXT,
        state               TEXT,
        postal_code         TEXT,
        country             TEXT NOT NULL DEFAULT 'India',
        contact_person      TEXT,
        email               TEXT,
        phone               TEXT,
        created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        CONSTRAINT uq_saved_party_user_name UNIQUE (user_id, party_name)
    );
    CREATE INDEX IF NOT EXISTS idx_saved_parties_user_id ON saved_parties (user_id);
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
        conn.commit()


# ==================== PYDANTIC MODELS ====================

class SavedPartyRequest(BaseModel):
    party_name: str
    legal_entity_type: Optional[str] = None    # company/llp/individual/partnership
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = "India"
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class SavedPartyUpdateRequest(BaseModel):
    party_name: Optional[str] = None
    legal_entity_type: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class SavedPartyResponse(BaseModel):
    id: int
    user_id: str
    party_name: str
    legal_entity_type: Optional[str]
    address_line1: Optional[str]
    address_line2: Optional[str]
    city: Optional[str]
    state: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]
    contact_person: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    created_at: datetime


# ==================== ROUTES ====================

@router.get("", response_model=List[SavedPartyResponse])
async def list_saved_parties(user=Depends(get_current_user)):
    """List all saved parties for the current user, ordered alphabetically."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM saved_parties WHERE user_id = %s ORDER BY party_name ASC",
                (user["id"],)
            )
            return [dict(row) for row in cur.fetchall()]


@router.post("", response_model=SavedPartyResponse, status_code=201)
async def create_saved_party(request: SavedPartyRequest, user=Depends(get_current_user)):
    """
    Save a new party to the directory.
    If a party with the same name already exists for this user, returns 409.
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Check for duplicate name
            cur.execute(
                "SELECT id FROM saved_parties WHERE user_id = %s AND party_name = %s",
                (user["id"], request.party_name)
            )
            if cur.fetchone():
                raise HTTPException(
                    status_code=409,
                    detail=f"A saved party named '{request.party_name}' already exists."
                )

            cur.execute("""
                INSERT INTO saved_parties (
                    user_id, party_name, legal_entity_type,
                    address_line1, address_line2, city, state, postal_code, country,
                    contact_person, email, phone
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (
                user["id"],
                request.party_name,
                request.legal_entity_type,
                request.address_line1,
                request.address_line2,
                request.city,
                request.state,
                request.postal_code,
                request.country or "India",
                request.contact_person,
                request.email,
                request.phone,
            ))
            party = cur.fetchone()
            conn.commit()

    return dict(party)


@router.put("/{party_id}", response_model=SavedPartyResponse)
async def update_saved_party(
    party_id: int,
    request: SavedPartyUpdateRequest,
    user=Depends(get_current_user)
):
    """Update an existing saved party. Only provided fields are updated."""
    # Build dynamic update
    updates = []
    params = []

    field_map = {
        "party_name": request.party_name,
        "legal_entity_type": request.legal_entity_type,
        "address_line1": request.address_line1,
        "address_line2": request.address_line2,
        "city": request.city,
        "state": request.state,
        "postal_code": request.postal_code,
        "country": request.country,
        "contact_person": request.contact_person,
        "email": request.email,
        "phone": request.phone,
    }

    for field, value in field_map.items():
        if value is not None:
            updates.append(f"{field} = %s")
            params.append(value)

    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    params.extend([user["id"], party_id])

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"""
                UPDATE saved_parties
                SET {', '.join(updates)}, updated_at = NOW()
                WHERE user_id = %s AND id = %s
                RETURNING *
            """, params)
            party = cur.fetchone()
            if not party:
                raise HTTPException(status_code=404, detail="Saved party not found")
            conn.commit()

    return dict(party)


@router.delete("/{party_id}")
async def delete_saved_party(party_id: int, user=Depends(get_current_user)):
    """Delete a saved party from the directory."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM saved_parties WHERE id = %s AND user_id = %s RETURNING id",
                (party_id, user["id"])
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Saved party not found")
            conn.commit()

    return {"message": "Saved party deleted successfully", "id": party_id}
