# auto_fill_routes.py - Parameter Auto-Fill, Smart Defaults & Cascade (Tasks 1.3, 1.4, 1.6)
"""
Three endpoints that dramatically reduce the number of parameters users must fill manually:

1. POST /api/contracts/{id}/parameters/auto-fill
   Maps contract_parties fields → matching {{PLACEHOLDER}} parameters.
   Typically eliminates 15-25 parameters automatically.

2. POST /api/contracts/{id}/parameters/apply-defaults
   Pre-fills parameters with intelligent defaults based on contract type + jurisdiction.
   Typically eliminates 10-25 more parameters.

3. POST /api/contracts/{id}/parameters/cascade
   When one parameter changes, derives related parameters automatically.
   e.g., EFFECTIVE_DATE + TERM_DURATION_MONTHS → TERM_END_DATE
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from psycopg2.extras import RealDictCursor
from datetime import date
from dateutil.relativedelta import relativedelta

from config import get_connection, get_neo4j_driver
from auth_middleware import get_current_user
from parameters_routes import fetch_parameters_for_active_clauses

router = APIRouter(prefix="/api/contracts", tags=["auto-fill"])


# ==================== CONSTANTS ====================

# Maps party_role prefix → party field → parameter placeholder suffix
# e.g., party_a.party_name → {{PARTY_A_NAME}}
ROLE_PREFIX_MAP = {
    "party_a": "PARTY_A",
    "party_b": "PARTY_B",
    "party_c": "PARTY_C",
    "witness_1": "WITNESS_1",
    "witness_2": "WITNESS_2",
}

PARTY_FIELD_MAP = {
    "party_name": "NAME",
    "email": "EMAIL",
    "address_line1": "ADDRESS",
    "city": "CITY",
    "state": "STATE",
    "postal_code": "POSTAL_CODE",
    "country": "COUNTRY",
    "contact_person": "CONTACT_PERSON",
    "phone": "PHONE",
    "legal_entity_type": "ENTITY_TYPE",
}

# Smart defaults — ONLY truly universal legal conventions.
# Context-specific values (city, dates, amounts) come from auto-fill or LLM inference.
SMART_DEFAULTS: dict = {
    # --- Jurisdiction-based (legal conventions) ---
    "India": {
        "GOVERNING_LAW": "Laws of India",
        "CURRENCY": "INR",
        "STAMP_DUTY": "As per applicable state stamp act",
        "ARBITRATION_RULES": "Indian Arbitration and Conciliation Act, 1996",
    },
    "USA": {
        "GOVERNING_LAW": "Laws of the United States",
        "CURRENCY": "USD",
    },
    "UK": {
        "GOVERNING_LAW": "Laws of England and Wales",
        "CURRENCY": "GBP",
        "ARBITRATION_RULES": "Arbitration Act 1996 (UK)",
    },
}

# LLM prompt for inferring smart defaults dynamically
SMART_DEFAULTS_PROMPT = """You are a legal contract assistant. Given the contract context below, suggest sensible default values for the unfilled parameters.

## Contract Context
- Contract Type: {contract_type}
- Jurisdiction: {jurisdiction}
- Description: {description}

## Already Filled Parameters
{filled_params}

## Unfilled Parameters (need defaults)
{unfilled_params}

## Rules
1. Only suggest values for parameters where a reasonable industry-standard default exists.
2. Do NOT guess user-specific values like company names, addresses, specific dates, or monetary amounts.
3. For durations/periods, use common legal standards (e.g., "30 days" for notice, "2 years" for confidentiality).
4. For numeric fields like NUMBER_ARBITRATORS, use common practice (e.g., "1" or "3").
5. Skip any parameter where the value truly depends on negotiation (like CONTRACT_VALUE, LIABILITY_CAP amounts).
6. Return ONLY parameters you are confident about.

Respond in this JSON format:
{{
  "defaults": [
    {{"parameter_name": "NOTICE_PERIOD", "value": "30 days", "reason": "Industry standard for SaaS agreements"}},
    {{"parameter_name": "CURE_PERIOD", "value": "15 days", "reason": "Typically half the notice period"}}
  ]
}}
"""

# Cascade rules: when trigger_param changes, derive related params
# Each rule is a dict with: trigger, derives, compute_fn
# compute_fn(new_value: str, all_filled_params: dict) -> str | None
CASCADE_RULES = [
    {
        "trigger": "EFFECTIVE_DATE",
        "derives": "TERM_END_DATE",
        "compute_fn": lambda val, params: _add_months_to_date(
            val, int(params.get("TERM_DURATION_MONTHS", "12"))
        ) if params.get("TERM_DURATION_MONTHS") else None,
    },
    {
        "trigger": "TERM_DURATION_MONTHS",
        "derives": "TERM_END_DATE",
        "compute_fn": lambda val, params: _add_months_to_date(
            params.get("EFFECTIVE_DATE", ""), int(val)
        ) if params.get("EFFECTIVE_DATE") else None,
    },
    {
        "trigger": "CONTRACT_VALUE",
        "derives": "LIABILITY_CAP",
        "compute_fn": lambda val, params: val,  # default: liability cap = contract value
    },
    {
        "trigger": "PARTY_A_CITY",
        "derives": "ARBITRATION_SEAT",
        "compute_fn": lambda val, params: val,
    },
    {
        "trigger": "NOTICE_PERIOD",
        "derives": "CURE_PERIOD",
        "compute_fn": lambda val, params: _halve_day_period(val),
    },
]


# ==================== HELPERS ====================

def _upsert_parameter(cur, contract_id: str, parameter_id: str, value: str, provided_by: str):
    """Upsert a single string parameter value, tracking provenance."""
    cur.execute("""
        INSERT INTO contract_parameters (
            contract_id, parameter_id, value_text, provided_by
        )
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (contract_id, parameter_id) DO UPDATE SET
            value_text   = EXCLUDED.value_text,
            provided_by  = EXCLUDED.provided_by,
            updated_at   = NOW()
    """, (contract_id, parameter_id, str(value), provided_by))


def _get_contract(cur, contract_id: str) -> dict:
    cur.execute(
        "SELECT id, contract_type, jurisdiction FROM contracts WHERE id = %s",
        (contract_id,)
    )
    contract = cur.fetchone()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return dict(contract)


def _add_months_to_date(date_str: str, months: int) -> Optional[str]:
    """Add N months to a YYYY-MM-DD string. Returns None on parse error."""
    try:
        d = date.fromisoformat(date_str)
        result = d + relativedelta(months=months)
        return result.isoformat()
    except (ValueError, TypeError):
        return None


def _halve_day_period(period_str: str) -> Optional[str]:
    """Turn '30 days' → '15 days'. Returns None if parsing fails."""
    try:
        parts = period_str.strip().split()
        if len(parts) >= 1 and parts[0].isdigit():
            halved = int(parts[0]) // 2
            unit = parts[1] if len(parts) > 1 else "days"
            return f"{halved} {unit}"
    except Exception:
        pass
    return None


def _get_filled_param_names(contract_id: str) -> dict:
    """
    Return {param_placeholder_name: value} for all currently filled parameters.
    Used by the cascade engine to look up sibling values.
    """
    # Get param_id -> param_name map
    driver = get_neo4j_driver()
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT cp.parameter_id, cp.value_text, cp.value_date, cp.value_integer
                FROM contract_parameters cp
                WHERE cp.contract_id = %s
            """, (contract_id,))
            rows = {r["parameter_id"]: r for r in cur.fetchall()}

            cur.execute("""
                SELECT DISTINCT clause_id FROM contract_clauses
                WHERE contract_id = %s AND is_active = true
            """, (contract_id,))
            clause_ids = [r["clause_id"] for r in cur.fetchall()]

    if not clause_ids:
        return {}

    with driver.session() as session:
        result = session.run("""
            MATCH (c:Clause)-[:CONTAINS_PARAM]->(p:Parameter)
            WHERE c.id IN $clause_ids
            RETURN DISTINCT p.id AS param_id, p.name AS param_name
        """, {"clause_ids": clause_ids})
        param_name_map = {rec["param_id"]: rec["param_name"] for rec in result}

    # Build name → value dict, stripping {{ }}
    filled = {}
    for param_id, name in param_name_map.items():
        if param_id in rows:
            row = rows[param_id]
            val = row["value_text"] or (
                row["value_date"].isoformat() if row["value_date"] else None
            ) or (
                str(row["value_integer"]) if row["value_integer"] is not None else None
            )
            if val is not None:
                # Strip {{ }} to get the bare placeholder name
                bare_name = name.strip("{}").strip()
                filled[bare_name] = val

    return filled


# ==================== PYDANTIC MODELS ====================

class CascadeRequest(BaseModel):
    changed_parameter: str   # bare placeholder name, e.g. "EFFECTIVE_DATE"
    value: str               # the new value as a string


# ==================== ROUTES ====================

@router.post("/{contract_id}/parameters/auto-fill")
async def auto_fill_from_parties(contract_id: str, user=Depends(get_current_user)):
    """
    Task 1.3 — Layer 1: Party-to-Parameter Auto-Fill

    Maps fields from contract_parties to matching {{PLACEHOLDER}} parameters.
    Only fills parameters that exist in the contract's active clauses.
    Does NOT overwrite values already set by the user (provided_by = 'user').

    Returns a summary of what was filled and what remains.
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Verify contract
            _get_contract(cur, contract_id)

            # Get all parties for this contract
            cur.execute(
                "SELECT * FROM contract_parties WHERE contract_id = %s",
                (contract_id,)
            )
            parties = [dict(r) for r in cur.fetchall()]

    if not parties:
        return {
            "auto_filled": 0,
            "message": "No parties found. Add parties before running auto-fill.",
            "filled_parameters": [],
        }

    # Fetch all parameters for active clauses with their names from Neo4j
    parameters = fetch_parameters_for_active_clauses(contract_id)
    if not parameters:
        return {
            "auto_filled": 0,
            "message": "No parameters found. Generate clauses before running auto-fill.",
            "filled_parameters": [],
        }

    # Build a map of placeholder_name → parameter_id
    # Try both {{PARTY_A_NAME}} and PARTY_A_NAME formats
    placeholder_to_id: dict[str, str] = {}
    for p in parameters:
        placeholder_to_id[p["name"]] = p["id"]
        # Also map the bare name (without braces)
        bare = p["name"].strip("{}")
        if bare:
            placeholder_to_id[bare] = p["id"]

    # Get already-user-filled param IDs to avoid overwriting
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT parameter_id, provided_by FROM contract_parameters
                WHERE contract_id = %s
            """, (contract_id,))
            existing = {r["parameter_id"]: r["provided_by"] for r in cur.fetchall()}

    filled_count = 0
    filled_list = []

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # --- Map party fields to parameters ---
            for party in parties:
                role = party.get("party_role", "")
                prefix = ROLE_PREFIX_MAP.get(role)
                if not prefix:
                    continue

                for field, suffix in PARTY_FIELD_MAP.items():
                    value = party.get(field)
                    if not value:
                        continue

                    placeholder = f"{{{{{prefix}_{suffix}}}}}"
                    bare_name = f"{prefix}_{suffix}"
                    param_id = placeholder_to_id.get(placeholder) or placeholder_to_id.get(bare_name)
                    if not param_id:
                        continue

                    # Don't overwrite user-entered values
                    if existing.get(param_id) == "user":
                        continue

                    _upsert_parameter(cur, contract_id, param_id, str(value), "auto_fill")
                    filled_count += 1
                    filled_list.append({
                        "parameter_id": param_id,
                        "placeholder": placeholder,
                        "value": str(value),
                        "source": f"{role}.{field}",
                    })

            # --- Derive contextual params from Party A ---
            party_a = next((p for p in parties if p.get("party_role") == "party_a"), None)
            if party_a:
                # JURISDICTION_CITY ← Party A's city
                city = party_a.get("city")
                if city:
                    for key in ("JURISDICTION_CITY", "ARBITRATION_SEAT"):
                        for fmt in (f"{{{{{key}}}}}", key):
                            pid = placeholder_to_id.get(fmt)
                            if pid and existing.get(pid) != "user":
                                _upsert_parameter(cur, contract_id, pid, city, "auto_fill")
                                filled_count += 1
                                filled_list.append({
                                    "parameter_id": pid,
                                    "placeholder": f"{{{{{key}}}}}",
                                    "value": city,
                                    "source": "party_a.city (derived)",
                                })
                                break

            conn.commit()

    remaining = len(parameters) - filled_count
    return {
        "auto_filled": filled_count,
        "remaining": remaining,
        "total_parameters": len(parameters),
        "filled_parameters": filled_list,
        "message": f"Auto-filled {filled_count} parameters from party data.",
    }


@router.post("/{contract_id}/parameters/apply-defaults")
async def apply_smart_defaults(contract_id: str, user=Depends(get_current_user)):
    """
    Smart Defaults Engine — two layers:
    
    Layer 1: Static jurisdiction defaults (governing law, currency) — instant, no LLM.
    Layer 2: LLM-inferred defaults for remaining unfilled params — uses contract context
             to suggest sensible industry-standard values dynamically.
    
    Only fills parameters that are NOT already filled.
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            contract = _get_contract(cur, contract_id)

    contract_type = contract["contract_type"]
    jurisdiction = contract["jurisdiction"]

    # Fetch parameters for active clauses
    parameters = fetch_parameters_for_active_clauses(contract_id)
    if not parameters:
        return {
            "defaults_applied": 0,
            "message": "No parameters found. Generate clauses first.",
        }

    # Build placeholder → param_id map (both {{NAME}} and bare NAME)
    placeholder_to_id: dict[str, str] = {}
    for p in parameters:
        placeholder_to_id[p["name"]] = p["id"]
        bare = p["name"].strip("{}")
        if bare:
            placeholder_to_id[bare] = p["id"]

    # Get already-filled param IDs
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT parameter_id FROM contract_parameters
                WHERE contract_id = %s
                  AND (value_text IS NOT NULL AND value_text != '')
            """, (contract_id,))
            already_filled = {r["parameter_id"] for r in cur.fetchall()}

    applied_count = 0
    applied_list = []

    # --- Layer 1: Static jurisdiction defaults ---
    static_defaults = SMART_DEFAULTS.get(jurisdiction, {})

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            for placeholder_name, default_value in static_defaults.items():
                placeholder_braced = f"{{{{{placeholder_name}}}}}"
                param_id = placeholder_to_id.get(placeholder_braced) or placeholder_to_id.get(placeholder_name)
                if not param_id:
                    continue
                if param_id in already_filled:
                    continue

                _upsert_parameter(cur, contract_id, param_id, default_value, "system_default")
                already_filled.add(param_id)
                applied_count += 1
                applied_list.append({
                    "parameter_id": param_id,
                    "placeholder": placeholder_braced,
                    "value": default_value,
                    "source": "jurisdiction_default",
                })

            conn.commit()

    # --- Layer 2: LLM-inferred defaults for remaining unfilled params ---
    # Build lists of filled and unfilled parameter names
    filled_display = []
    unfilled_display = []
    for p in parameters:
        bare = p["name"].strip("{}").strip()
        if p["id"] in already_filled:
            filled_display.append(bare)
        else:
            desc = p.get("description", "")
            dtype = p.get("data_type", "String")
            unfilled_display.append(f"- {bare} (type: {dtype}){f' — {desc}' if desc else ''}")

    if unfilled_display:
        try:
            from graph_rag_engine import llm_client
            if llm_client.is_configured():
                prompt = SMART_DEFAULTS_PROMPT.format(
                    contract_type=contract_type.replace("_", " ").title(),
                    jurisdiction=jurisdiction,
                    description=contract.get("description", "N/A")[:500],
                    filled_params=", ".join(filled_display) if filled_display else "None",
                    unfilled_params="\n".join(unfilled_display),
                )

                llm_response = llm_client.generate(prompt, "You are a legal contract assistant.")
                llm_defaults = llm_response.get("defaults", [])

                with get_connection() as conn:
                    with conn.cursor(cursor_factory=RealDictCursor) as cur:
                        for item in llm_defaults:
                            pname = item.get("parameter_name", "")
                            pval = item.get("value", "")
                            if not pname or not pval:
                                continue

                            placeholder_braced = f"{{{{{pname}}}}}"
                            param_id = placeholder_to_id.get(placeholder_braced) or placeholder_to_id.get(pname)
                            if not param_id:
                                continue
                            if param_id in already_filled:
                                continue

                            _upsert_parameter(cur, contract_id, param_id, pval, "system_default")
                            already_filled.add(param_id)
                            applied_count += 1
                            applied_list.append({
                                "parameter_id": param_id,
                                "placeholder": placeholder_braced,
                                "value": pval,
                                "source": "llm_inferred",
                                "reason": item.get("reason", ""),
                            })

                        conn.commit()
        except Exception as e:
            import logging
            logging.getLogger("legalwiz").warning(f"LLM smart defaults failed (non-fatal): {e}")

    return {
        "defaults_applied": applied_count,
        "applied_parameters": applied_list,
        "message": f"Applied {applied_count} smart defaults for {contract_type} / {jurisdiction}.",
    }


@router.post("/{contract_id}/parameters/cascade")
async def cascade_parameter(
    contract_id: str,
    request: CascadeRequest,
    user=Depends(get_current_user)
):
    """
    Task 1.6 — Layer 4: Cascade Inference

    Given a changed parameter (e.g., EFFECTIVE_DATE = "2026-01-01"), derives
    related parameters (e.g., TERM_END_DATE = "2026-12-31").

    Called by the frontend on every parameter save.
    Returns a list of derived updates so the UI can reflect them immediately.
    """
    # Fetch parameters for active clauses — needed to resolve placeholder → param_id
    parameters = fetch_parameters_for_active_clauses(contract_id)
    if not parameters:
        return {"cascaded": [], "message": "No parameters available."}

    placeholder_to_id: dict[str, str] = {
        p["name"].strip("{}").strip(): p["id"] for p in parameters
    }

    # Get current filled param values (by bare name) for use in cascade rules
    filled_params = _get_filled_param_names(contract_id)

    # Run all matching cascade rules
    cascaded = []

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            for rule in CASCADE_RULES:
                if rule["trigger"] != request.changed_parameter:
                    continue

                derived_name = rule["derives"]
                derived_param_id = placeholder_to_id.get(derived_name)
                if not derived_param_id:
                    continue  # Parameter doesn't exist in this contract

                derived_value = rule["compute_fn"](request.value, filled_params)
                if derived_value is None:
                    continue

                _upsert_parameter(
                    cur, contract_id, derived_param_id, derived_value, "cascade"
                )
                cascaded.append({
                    "parameter": derived_name,
                    "parameter_id": derived_param_id,
                    "value": derived_value,
                    "source": f"cascade from {request.changed_parameter}",
                })

            if cascaded:
                conn.commit()

    return {
        "cascaded": cascaded,
        "trigger": request.changed_parameter,
        "message": f"Derived {len(cascaded)} parameter(s) from {request.changed_parameter}.",
    }


# ==================== EXTRACT PARTIES FROM DESCRIPTION ====================

EXTRACT_PARTIES_PROMPT = """You are a legal contract assistant. Extract party information from the contract description below.

## Contract Details
- Title: {title}
- Contract Type: {contract_type}
- Jurisdiction: {jurisdiction}
- Description: {description}

## Rules
1. Extract all parties mentioned in the description.
2. Party A is typically the service provider / vendor / licensor / employer / disclosing party.
3. Party B is typically the client / customer / licensee / employee / receiving party.
4. Extract as much detail as you can find: company name, entity type (company/individual/LLP), city, contact person name.
5. If the description mentions specific people by name, use them as contact_person.
6. If entity type is not clear, infer from context (e.g., "Pvt Ltd" = company, a person's name alone = individual).
7. Only extract what is explicitly stated or strongly implied. Do NOT invent details.
8. If you can only find party names and nothing else, that's fine — return just the names.

Respond in this JSON format:
{{
  "parties": [
    {{
      "party_role": "party_a",
      "party_name": "Company or Person Name",
      "legal_entity_type": "company" | "individual" | "llp" | "partnership" | null,
      "city": "City name or null",
      "state": "State name or null",
      "country": "Country or null",
      "contact_person": "Person name or null",
      "email": null,
      "phone": null
    }}
  ],
  "confidence": "high" | "medium" | "low",
  "notes": "Any observations about what was extracted"
}}
"""


@router.post("/{contract_id}/parties/extract-from-description")
async def extract_parties_from_description(contract_id: str, user=Depends(get_current_user)):
    """
    Extract party information from the contract description using LLM.
    Creates parties automatically if extraction succeeds.
    Only works if the contract has a description.
    Does NOT overwrite existing parties.
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, title, contract_type, jurisdiction, description FROM contracts WHERE id = %s AND created_by = %s",
                (contract_id, user["id"])
            )
            contract = cur.fetchone()
            if not contract:
                raise HTTPException(status_code=404, detail="Contract not found")

    description = (contract.get("description") or "").strip()
    if not description:
        return {
            "extracted": 0,
            "parties": [],
            "message": "No description provided. Add a description in Setup to enable auto-extraction.",
        }

    # Check existing parties
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT party_role FROM contract_parties WHERE contract_id = %s",
                (contract_id,)
            )
            existing_roles = {r["party_role"] for r in cur.fetchall()}

    # Call LLM to extract parties
    try:
        from graph_rag_engine import llm_client
        if not llm_client.is_configured():
            raise HTTPException(
                status_code=503,
                detail="LLM not configured. Set LLM_API_KEY in .env to enable party extraction."
            )

        prompt = EXTRACT_PARTIES_PROMPT.format(
            title=contract.get("title", ""),
            contract_type=contract["contract_type"].replace("_", " ").title(),
            jurisdiction=contract["jurisdiction"],
            description=description[:2000],
        )

        result = llm_client.generate(prompt, "You are a legal contract assistant.")
        extracted_parties = result.get("parties", [])

    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.getLogger("legalwiz").error(f"Party extraction failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract parties from description.")

    # Insert extracted parties (skip roles that already exist)
    created = []
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            for party in extracted_parties:
                role = party.get("party_role", "")
                if role in existing_roles:
                    continue
                if not role or not party.get("party_name"):
                    continue

                # Validate role
                valid_roles = {"party_a", "party_b", "party_c", "witness_1", "witness_2"}
                if role not in valid_roles:
                    continue

                cur.execute("""
                    INSERT INTO contract_parties (
                        contract_id, party_role, party_name, legal_entity_type,
                        address_line1, city, state, postal_code, country,
                        contact_person, email, phone
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                """, (
                    contract_id,
                    role,
                    party.get("party_name", ""),
                    party.get("legal_entity_type"),
                    party.get("address_line1"),
                    party.get("city"),
                    party.get("state"),
                    party.get("postal_code"),
                    party.get("country", contract["jurisdiction"]),
                    party.get("contact_person"),
                    party.get("email"),
                    party.get("phone"),
                ))
                row = cur.fetchone()
                if row:
                    created.append(dict(row))
                    existing_roles.add(role)

            conn.commit()

    return {
        "extracted": len(created),
        "parties": created,
        "confidence": result.get("confidence", "medium"),
        "notes": result.get("notes", ""),
        "message": f"Extracted {len(created)} party/parties from description."
            if created else "No new parties could be extracted (roles may already exist).",
    }
