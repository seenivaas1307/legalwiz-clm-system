# esign_routes.py - DocuSign E-Signature Integration
"""
Send contracts for electronic signature via DocuSign.

Flow: Generate PDF → Create Envelope → Get Signing URL → Webhook Status Update

Endpoints:
- POST /{id}/esign/send           — Create DocuSign envelope and send for signing
- GET  /{id}/esign/signing-url    — Get embedded signing URL for iframe/redirect
- GET  /{id}/esign/status         — Check envelope status
- POST /api/esign/webhook         — DocuSign Connect webhook callback

Requires DocuSign developer account credentials in .env:
  DOCUSIGN_INTEGRATION_KEY, DOCUSIGN_USER_ID, DOCUSIGN_ACCOUNT_ID,
  DOCUSIGN_RSA_PRIVATE_KEY (base64 encoded)
"""

import os
import base64
import json
import hmac
import hashlib
import logging
from io import BytesIO
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field, EmailStr

from config import get_db, DB_CONFIG, verify_contract_ownership
from auth_middleware import get_current_user
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger("legalwiz.esign")

router = APIRouter(tags=["e-signature"])


# ==================== DOCUSIGN CONFIG ====================

DOCUSIGN_CONFIG = {
    "integration_key": os.getenv("DOCUSIGN_INTEGRATION_KEY", ""),
    "user_id": os.getenv("DOCUSIGN_USER_ID", ""),
    "account_id": os.getenv("DOCUSIGN_ACCOUNT_ID", ""),
    "private_key": os.getenv("DOCUSIGN_RSA_PRIVATE_KEY", ""),  # Base64 encoded
    "base_url": os.getenv("DOCUSIGN_BASE_URL", "https://demo.docusign.net/restapi"),
    "oauth_host": os.getenv("DOCUSIGN_OAUTH_HOST", "account-d.docusign.com"),
    "return_url": os.getenv("DOCUSIGN_RETURN_URL", "http://localhost:3000/signing-complete"),
}


def _is_configured() -> bool:
    """Check if DocuSign credentials are set."""
    return bool(
        DOCUSIGN_CONFIG["integration_key"]
        and DOCUSIGN_CONFIG["user_id"]
        and DOCUSIGN_CONFIG["account_id"]
    )


def _get_docusign_client():
    """Create and authenticate a DocuSign API client."""
    if not _is_configured():
        raise HTTPException(
            status_code=503,
            detail={
                "message": "DocuSign is not configured",
                "hint": "Add DOCUSIGN_INTEGRATION_KEY, DOCUSIGN_USER_ID, "
                        "DOCUSIGN_ACCOUNT_ID, and DOCUSIGN_RSA_PRIVATE_KEY to .env",
                "docs": "https://developers.docusign.com/docs/esign-rest-api/quickstart",
            }
        )

    try:
        from docusign_esign import ApiClient
        from docusign_esign.client.api_exception import ApiException

        client = ApiClient()
        client.set_oauth_host_name(DOCUSIGN_CONFIG["oauth_host"])

        # Resolve private key — supports 3 formats:
        #   1. File path: /path/to/private.pem
        #   2. Base64-encoded full PEM (single line in .env)
        #   3. PEM content with literal \n (e.g. "-----BEGIN...-----\nMIIE...\n-----END...-----")
        raw_key = DOCUSIGN_CONFIG["private_key"]
        if not raw_key:
            raise HTTPException(
                status_code=503,
                detail="DOCUSIGN_RSA_PRIVATE_KEY not set in .env"
            )

        private_key_bytes = None

        # Format 1: File path
        if os.path.isfile(raw_key):
            with open(raw_key, "rb") as f:
                private_key_bytes = f.read()

        # Format 3: PEM with literal \n (from .env)
        elif "-----BEGIN" in raw_key:
            private_key_bytes = raw_key.replace("\\n", "\n").encode()

        # Format 2: Base64-encoded full PEM
        else:
            try:
                decoded = base64.b64decode(raw_key)
                # Check if it decoded into a valid PEM
                if b"-----BEGIN" in decoded:
                    private_key_bytes = decoded
                else:
                    # Raw base64 might be the key body — wrap it in PEM headers
                    private_key_bytes = (
                        b"-----BEGIN RSA PRIVATE KEY-----\n"
                        + decoded
                        + b"\n-----END RSA PRIVATE KEY-----\n"
                    )
            except Exception:
                private_key_bytes = raw_key.encode()

        # Validate key length (RSA private key PEM is typically 1600+ bytes)
        if len(private_key_bytes) < 500:
            raise HTTPException(
                status_code=503,
                detail={
                    "message": f"Private key appears truncated ({len(private_key_bytes)} bytes). "
                               "An RSA private key is typically 1600+ bytes.",
                    "hint": "Option 1: Save the key as a file and set DOCUSIGN_RSA_PRIVATE_KEY=/path/to/private.pem\n"
                            "Option 2: Base64 encode the ENTIRE PEM file: "
                            "cat private.pem | base64 | tr -d '\\n' > key.b64\n"
                            "Option 3: Use literal \\n: "
                            'DOCUSIGN_RSA_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\\nMIIE...\\n-----END RSA PRIVATE KEY-----"',
                }
            )

        # Get JWT token
        token_response = client.request_jwt_user_token(
            client_id=DOCUSIGN_CONFIG["integration_key"],
            user_id=DOCUSIGN_CONFIG["user_id"],
            oauth_host_name=DOCUSIGN_CONFIG["oauth_host"],
            private_key_bytes=private_key_bytes,
            expires_in=3600,
            scopes=["signature", "impersonation"],
        )

        # IMPORTANT: The JWT auth flow corrupts the auth client's host.
        # Create a NEW client for API operations with the correct base URI.
        base_uri = "https://demo.docusign.net"
        try:
            user_info = client.get_user_info(token_response.access_token)
            accounts = user_info.get_accounts()
            for acc in accounts:
                if acc.account_id == DOCUSIGN_CONFIG["account_id"]:
                    base_uri = acc.base_uri
                    break
            else:
                if accounts:
                    base_uri = accounts[0].base_uri
        except Exception:
            pass

        api_client = ApiClient()
        api_client.host = f"{base_uri}/restapi"
        api_client.set_default_header(
            "Authorization", f"Bearer {token_response.access_token}"
        )

        return api_client

    except ImportError:
        raise HTTPException(
            status_code=503,
            detail="docusign-esign not installed. Run: pip install docusign-esign"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"DocuSign authentication failed: {str(e)}"
        )


# ==================== TABLE SETUP ====================


def _ensure_columns():
    """Add e-signature columns to contracts table if they don't exist. Called once at startup."""

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                ALTER TABLE contracts ADD COLUMN IF NOT EXISTS envelope_id TEXT;
                ALTER TABLE contracts ADD COLUMN IF NOT EXISTS signing_status TEXT DEFAULT 'not_sent';
                ALTER TABLE contracts ADD COLUMN IF NOT EXISTS signed_at TIMESTAMPTZ;
                ALTER TABLE contracts ADD COLUMN IF NOT EXISTS signer_email TEXT;
                ALTER TABLE contracts ADD COLUMN IF NOT EXISTS signer_name TEXT;
                ALTER TABLE contracts ADD COLUMN IF NOT EXISTS creator_signature_name TEXT;
                ALTER TABLE contracts ADD COLUMN IF NOT EXISTS creator_signature_date TEXT;
            """)
            conn.commit()
    finally:
        conn.close()


# ==================== PYDANTIC MODELS ====================

class SendForSigningRequest(BaseModel):
    signer_email: EmailStr = Field(..., description="Email of the signer")
    signer_name: str = Field(..., description="Name of the signer")
    email_subject: Optional[str] = Field(None, description="Custom email subject")
    email_body: Optional[str] = Field(None, description="Custom email body")


class CreatorSignRequest(BaseModel):
    """Step 1: Creator signs first (embedded), then Party B signs via email."""
    party_b_email: Optional[EmailStr] = Field(None, description="Party B email (can be added later)")
    party_b_name: Optional[str] = Field(None, description="Party B name")


class CreatorSignatureRequest(BaseModel):
    """Save creator's in-app signature."""
    signature_name: str = Field(..., description="Creator's typed signature (full name)")


class SigningStatusResponse(BaseModel):
    contract_id: str
    envelope_id: Optional[str]
    signing_status: str
    signer_email: Optional[str]
    signer_name: Optional[str]
    signed_at: Optional[datetime]
    signers: Optional[list] = None  # Per-signer status details
    sent_at: Optional[str] = None
    status_changed_at: Optional[str] = None


# ==================== HELPERS ====================



def _get_contract_pdf(contract_id: str) -> bytes:
    """Generate PDF for the contract using export_routes logic."""
    from export_routes import _get_contract_data, _build_pdf
    data = _get_contract_data(contract_id)
    buf = _build_pdf(data)
    return buf.getvalue()


def _update_signing_status(
    contract_id: str = None,
    envelope_id: str = None,
    status: str = None,
    signer_email: str = None,
    signer_name: str = None,
    signed_at: datetime = None,
):
    """Update signing status in the contracts table."""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            updates = []
            params = []

            if status:
                updates.append("signing_status = %s")
                params.append(status)
            if signer_email:
                updates.append("signer_email = %s")
                params.append(signer_email)
            if signer_name:
                updates.append("signer_name = %s")
                params.append(signer_name)
            if signed_at:
                updates.append("signed_at = %s")
                params.append(signed_at)

            updates.append("updated_at = NOW()")

            # Determine WHERE clause — avoid double-appending envelope_id
            if contract_id:
                # When looking up by contract_id, also SET envelope_id if provided
                if envelope_id:
                    updates.insert(0, "envelope_id = %s")
                    params.insert(0, envelope_id)
                where = "id = %s"
                params.append(contract_id)
            elif envelope_id:
                # Looking up by envelope_id — do NOT also set it (was the bug)
                where = "envelope_id = %s"
                params.append(envelope_id)
            else:
                return

            sql = f"UPDATE contracts SET {', '.join(updates)} WHERE {where}"
            cur.execute(sql, params)
            conn.commit()
    finally:
        conn.close()


# ==================== ROUTES ====================

@router.post("/api/contracts/{contract_id}/esign/send")
async def send_for_signing(contract_id: str, request: SendForSigningRequest, user=Depends(get_current_user)):
    """
    Create a DocuSign envelope and send the contract for e-signature.

    1. Generates the contract PDF
    2. Creates a DocuSign envelope with the PDF
    3. Sends to the specified signer via email
    4. Stores the envelope_id in the contracts table
    """
    verify_contract_ownership(contract_id, user["id"])


    # Check contract exists and isn't already sent
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, title, signing_status, envelope_id
                FROM contracts WHERE id = %s
            """, (contract_id,))
            contract = cur.fetchone()
    finally:
        conn.close()

    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    if contract.get("signing_status") in ("sent", "delivered", "signed"):
        raise HTTPException(
            status_code=409,
            detail=f"Contract already has signing status: {contract['signing_status']}. "
                   f"Envelope: {contract.get('envelope_id')}"
        )

    # Generate PDF
    try:
        pdf_bytes = _get_contract_pdf(contract_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate contract PDF: {str(e)}"
        )

    # Create DocuSign envelope
    client = _get_docusign_client()

    try:
        from docusign_esign import EnvelopesApi, EnvelopeDefinition, Document
        from docusign_esign import Signer, SignHere, Tabs, Recipients

        # Create document from PDF
        doc_b64 = base64.b64encode(pdf_bytes).decode("ascii")
        document = Document(
            document_base64=doc_b64,
            name=contract["title"] or "Contract",
            file_extension="pdf",
            document_id="1",
        )

        # Define signer with sign-here tab
        sign_here = SignHere(
            anchor_string="/sig1/",
            anchor_units="pixels",
            anchor_y_offset="10",
            anchor_x_offset="20",
        )

        signer = Signer(
            email=request.signer_email,
            name=request.signer_name,
            recipient_id="1",
            routing_order="1",
            tabs=Tabs(sign_here_tabs=[sign_here]),
        )

        # Create envelope
        envelope_definition = EnvelopeDefinition(
            email_subject=request.email_subject or f"Please sign: {contract['title']}",
            email_blurb=request.email_body or "Please review and sign this contract.",
            documents=[document],
            recipients=Recipients(signers=[signer]),
            status="sent",
        )

        envelopes_api = EnvelopesApi(client)
        result = envelopes_api.create_envelope(
            account_id=DOCUSIGN_CONFIG["account_id"],
            envelope_definition=envelope_definition,
        )

        envelope_id = result.envelope_id

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"DocuSign envelope creation failed: {str(e)}"
        )

    # Update contract with envelope info
    _update_signing_status(
        contract_id=contract_id,
        envelope_id=envelope_id,
        status="sent",
        signer_email=request.signer_email,
        signer_name=request.signer_name,
    )

    # Auto-version: snapshot after sending for signature
    try:
        from version_routes import create_version_snapshot
        create_version_snapshot(
            contract_id,
            f"Sent for e-signature to {request.signer_email}"
        )
    except Exception:
        pass

    return {
        "message": "Contract sent for e-signature",
        "contract_id": contract_id,
        "envelope_id": envelope_id,
        "signer_email": request.signer_email,
        "signer_name": request.signer_name,
        "status": "sent",
    }


@router.post("/api/contracts/{contract_id}/esign/creator-signature")
async def save_creator_signature(contract_id: str, request: CreatorSignatureRequest, user=Depends(get_current_user)):
    """
    Save the creator's in-app signature. Updates the contract with the
    creator's name and date, which appears in the PDF signature block.
    """
    verify_contract_ownership(contract_id, user["id"])

    sig_date = datetime.now().strftime("%B %d, %Y")

    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                UPDATE contracts
                SET creator_signature_name = %s,
                    creator_signature_date = %s,
                    signing_status = 'creator_signed',
                    updated_at = NOW()
                WHERE id = %s
                RETURNING id, creator_signature_name, creator_signature_date, signing_status
            """, (request.signature_name, sig_date, contract_id))
            result = cur.fetchone()
            conn.commit()
    finally:
        conn.close()

    if not result:
        raise HTTPException(status_code=404, detail="Contract not found")

    return {
        "message": "Creator signature saved",
        "contract_id": contract_id,
        "signature_name": result["creator_signature_name"],
        "signature_date": result["creator_signature_date"],
        "status": "creator_signed",
    }


@router.post("/api/contracts/{contract_id}/esign/creator-sign")
async def creator_sign(contract_id: str, request: CreatorSignRequest, user=Depends(get_current_user)):
    """
    Two-step signing flow:
    Step 1 — Creator signs via embedded signing (in-app).
    Step 2 — Party B receives email to sign remotely.

    Creates a DocuSign envelope with:
    - Signer 1 (creator): embedded signing with client_user_id → returns signing URL
    - Signer 2 (Party B): remote email signing (if email provided, otherwise added later)

    Returns a signing URL for the creator to sign immediately.
    """
    verify_contract_ownership(contract_id, user["id"])

    # Get contract + creator info
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT c.id, c.title, c.signing_status, c.envelope_id,
                       u.email AS creator_email, u.full_name AS creator_name
                FROM contracts c
                JOIN users u ON c.created_by = u.id
                WHERE c.id = %s
            """, (contract_id,))
            contract = cur.fetchone()
    finally:
        conn.close()

    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    if contract.get("signing_status") in ("sent", "delivered", "signed"):
        raise HTTPException(
            status_code=409,
            detail=f"Contract already has signing status: {contract['signing_status']}"
        )

    # Generate PDF
    try:
        pdf_bytes = _get_contract_pdf(contract_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

    # Create DocuSign envelope with 2 signers
    client = _get_docusign_client()

    try:
        from docusign_esign import (
            EnvelopesApi, EnvelopeDefinition, Document,
            Signer, SignHere, Tabs, Recipients, RecipientViewRequest,
        )

        doc_b64 = base64.b64encode(pdf_bytes).decode("ascii")
        document = Document(
            document_base64=doc_b64,
            name=contract["title"] or "Contract",
            file_extension="pdf",
            document_id="1",
        )

        # Signer 1: Creator (embedded — signs in-app)
        creator_sign_here = SignHere(
            anchor_string="/sig1/",
            anchor_units="pixels",
            anchor_y_offset="10",
            anchor_x_offset="20",
        )
        creator_signer = Signer(
            email=contract["creator_email"],
            name=contract["creator_name"],
            recipient_id="1",
            routing_order="1",
            client_user_id="creator",  # Required for embedded signing
            tabs=Tabs(sign_here_tabs=[creator_sign_here]),
        )

        signers = [creator_signer]

        # Signer 2: Party B (remote — signs via email)
        if request.party_b_email and request.party_b_name:
            party_b_sign_here = SignHere(
                anchor_string="/sig2/",
                anchor_units="pixels",
                anchor_y_offset="10",
                anchor_x_offset="20",
            )
            party_b_signer = Signer(
                email=request.party_b_email,
                name=request.party_b_name,
                recipient_id="2",
                routing_order="2",  # Signs after creator
                tabs=Tabs(sign_here_tabs=[party_b_sign_here]),
            )
            signers.append(party_b_signer)

        envelope_definition = EnvelopeDefinition(
            email_subject=f"Please sign: {contract['title']}",
            email_blurb="Please review and sign this contract.",
            documents=[document],
            recipients=Recipients(signers=signers),
            status="sent",
        )

        envelopes_api = EnvelopesApi(client)
        result = envelopes_api.create_envelope(
            account_id=DOCUSIGN_CONFIG["account_id"],
            envelope_definition=envelope_definition,
        )
        envelope_id = result.envelope_id

        # Get embedded signing URL for creator
        return_url = DOCUSIGN_CONFIG.get("return_url", "http://localhost:5173/signing-complete")
        view_request = RecipientViewRequest(
            return_url=return_url,
            authentication_method="none",
            email=contract["creator_email"],
            user_name=contract["creator_name"],
            client_user_id="creator",
        )

        view_result = envelopes_api.create_recipient_view(
            account_id=DOCUSIGN_CONFIG["account_id"],
            envelope_id=envelope_id,
            recipient_view_request=view_request,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DocuSign error: {str(e)}")

    # Update contract
    _update_signing_status(
        contract_id=contract_id,
        envelope_id=envelope_id,
        status="creator_signing",
        signer_email=request.party_b_email or contract["creator_email"],
        signer_name=request.party_b_name or contract["creator_name"],
    )

    try:
        from version_routes import create_version_snapshot
        create_version_snapshot(contract_id, "Creator signing initiated")
    except Exception:
        pass

    return {
        "message": "Envelope created. Sign as creator now.",
        "contract_id": contract_id,
        "envelope_id": envelope_id,
        "signing_url": view_result.url,
        "creator_email": contract["creator_email"],
        "creator_name": contract["creator_name"],
        "party_b_email": request.party_b_email,
        "party_b_name": request.party_b_name,
        "status": "creator_signing",
    }


@router.post("/api/contracts/{contract_id}/esign/send-to-party-b")
async def send_to_party_b(contract_id: str, request: SendForSigningRequest, user=Depends(get_current_user)):
    """
    Step 2: After creator has signed, add Party B as a remote signer.
    If Party B was already added during creator-sign, this just returns the status.
    """
    verify_contract_ownership(contract_id, user["id"])

    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, title, envelope_id, signing_status
                FROM contracts WHERE id = %s
            """, (contract_id,))
            contract = cur.fetchone()
    finally:
        conn.close()

    if not contract or not contract.get("envelope_id"):
        raise HTTPException(status_code=400, detail="Creator must sign first")

    # Update signer info
    _update_signing_status(
        contract_id=contract_id,
        status="sent",
        signer_email=request.signer_email,
        signer_name=request.signer_name,
    )

    return {
        "message": f"Contract sent to {request.signer_email} for signing",
        "contract_id": contract_id,
        "envelope_id": contract["envelope_id"],
        "party_b_email": request.signer_email,
        "status": "sent",
    }


@router.get("/api/contracts/{contract_id}/esign/signing-url")
async def get_signing_url(contract_id: str, user=Depends(get_current_user)):
    """
    Get an embedded signing URL for the signer.
    Use this to open DocuSign signing in an iframe or redirect.
    URL is valid for 5 minutes.
    """
    verify_contract_ownership(contract_id, user["id"])


    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, envelope_id, signing_status, signer_email, signer_name
                FROM contracts WHERE id = %s
            """, (contract_id,))
            contract = cur.fetchone()
    finally:
        conn.close()

    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    if not contract.get("envelope_id"):
        raise HTTPException(
            status_code=400,
            detail="Contract has not been sent for signing yet. Use POST /esign/send first."
        )

    if contract.get("signing_status") in ("signed", "declined", "voided"):
        raise HTTPException(
            status_code=409,
            detail=f"Cannot get signing URL — contract status is '{contract['signing_status']}'"
        )

    client = _get_docusign_client()

    try:
        from docusign_esign import EnvelopesApi, RecipientViewRequest

        view_request = RecipientViewRequest(
            return_url=DOCUSIGN_CONFIG["return_url"],
            authentication_method="none",
            email=contract["signer_email"],
            user_name=contract["signer_name"],
            client_user_id="1",  # Required for embedded signing
        )

        envelopes_api = EnvelopesApi(client)
        result = envelopes_api.create_recipient_view(
            account_id=DOCUSIGN_CONFIG["account_id"],
            envelope_id=contract["envelope_id"],
            recipient_view_request=view_request,
        )

        return {
            "signing_url": result.url,
            "expires_in_minutes": 5,
            "contract_id": contract_id,
            "envelope_id": contract["envelope_id"],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get signing URL: {str(e)}"
        )


@router.get("/api/contracts/{contract_id}/esign/status", response_model=SigningStatusResponse)
async def get_signing_status(contract_id: str, user=Depends(get_current_user)):
    """
    Get the current e-signature status for a contract.

    If DocuSign is configured and an envelope exists, also queries
    DocuSign for the latest status and updates the local DB.
    """
    verify_contract_ownership(contract_id, user["id"])


    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, envelope_id, signing_status, signer_email,
                       signer_name, signed_at
                FROM contracts WHERE id = %s
            """, (contract_id,))
            contract = cur.fetchone()
    finally:
        conn.close()

    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    # If we have an envelope and DocuSign is configured, get live status
    signers_detail = []
    sent_at = None
    status_changed_at = None

    if contract.get("envelope_id") and _is_configured():
        try:
            client = _get_docusign_client()
            from docusign_esign import EnvelopesApi

            envelopes_api = EnvelopesApi(client)
            envelope = envelopes_api.get_envelope(
                account_id=DOCUSIGN_CONFIG["account_id"],
                envelope_id=contract["envelope_id"],
            )

            ds_status = envelope.status  # sent, delivered, completed, declined, voided
            local_status = _map_docusign_status(ds_status)
            sent_at = envelope.sent_date_time
            status_changed_at = envelope.status_changed_date_time

            # Get per-signer/recipient status
            try:
                recipients = envelopes_api.list_recipients(
                    account_id=DOCUSIGN_CONFIG["account_id"],
                    envelope_id=contract["envelope_id"],
                )
                for signer in (recipients.signers or []):
                    signers_detail.append({
                        "name": signer.name,
                        "email": signer.email,
                        "status": signer.status,  # sent, delivered, completed, declined
                        "signed_at": signer.signed_date_time,
                        "delivered_at": signer.delivered_date_time,
                    })
            except Exception:
                pass

            # Update local DB if status changed
            if local_status != contract.get("signing_status"):
                signed_at_val = None
                if local_status == "signed":
                    signed_at_val = datetime.now()
                _update_signing_status(
                    contract_id=contract_id,
                    status=local_status,
                    signed_at=signed_at_val,
                )
                contract["signing_status"] = local_status
                contract["signed_at"] = signed_at_val

                # When fully signed, update contract status to "active"
                if local_status == "signed":
                    try:
                        conn2 = get_db()
                        with conn2.cursor() as cur2:
                            cur2.execute(
                                "UPDATE contracts SET status = 'active', updated_at = NOW() WHERE id = %s",
                                (contract_id,)
                            )
                            conn2.commit()
                        conn2.close()
                    except Exception:
                        pass

        except Exception:
            pass  # Fall through to return cached status

    return {
        "contract_id": str(contract["id"]),
        "envelope_id": contract.get("envelope_id"),
        "signing_status": contract.get("signing_status", "not_sent"),
        "signer_email": contract.get("signer_email"),
        "signer_name": contract.get("signer_name"),
        "signed_at": contract.get("signed_at"),
        "signers": signers_detail if signers_detail else None,
        "sent_at": sent_at,
        "status_changed_at": status_changed_at,
    }


@router.post("/api/esign/webhook")
async def docusign_webhook(request: Request):
    """
    DocuSign Connect webhook callback.

    DocuSign sends POST notifications when envelope status changes.
    Configure this URL in DocuSign Admin → Connect → Add Configuration.

    Webhook URL: https://your-domain.com/api/esign/webhook
    """
    # --- HMAC signature verification (mandatory) ---
    hmac_key = os.getenv("DOCUSIGN_HMAC_KEY", "")
    if not hmac_key:
        logger.error(
            "DOCUSIGN_HMAC_KEY not configured — rejecting webhook. "
            "Set it in .env to enable DocuSign webhook processing."
        )
        raise HTTPException(
            status_code=503,
            detail="Webhook signature verification not configured"
        )

    raw_body = await request.body()
    sig_header = request.headers.get("X-DocuSign-Signature-1", "")
    expected = base64.b64encode(
        hmac.new(hmac_key.encode(), raw_body, hashlib.sha256).digest()
    ).decode()
    if not hmac.compare_digest(sig_header, expected):
        logger.warning("DocuSign webhook HMAC verification failed")
        raise HTTPException(status_code=403, detail="Invalid webhook signature")
    try:
        body = json.loads(raw_body)
    except Exception:
        return {"message": "Received", "format": "non-json", "size": len(raw_body)}

    # Extract envelope info from DocuSign webhook payload
    envelope_id = body.get("envelopeId") or body.get("envelope_id")
    status = body.get("status") or body.get("envelope_status")

    if not envelope_id:
        return {"message": "No envelope ID in payload"}

    local_status = _map_docusign_status(status)

    signed_at = None
    if local_status == "signed":
        signed_at = datetime.now()

    _update_signing_status(
        envelope_id=envelope_id,
        status=local_status,
        signed_at=signed_at,
    )

    return {
        "message": "Status updated",
        "envelope_id": envelope_id,
        "status": local_status,
    }


def _map_docusign_status(ds_status: str) -> str:
    """Map DocuSign envelope status to local status."""
    if not ds_status:
        return "not_sent"
    status_map = {
        "created": "draft",
        "sent": "sent",
        "delivered": "delivered",
        "completed": "signed",
        "signed": "signed",
        "declined": "declined",
        "voided": "voided",
    }
    return status_map.get(ds_status.lower(), ds_status.lower())
