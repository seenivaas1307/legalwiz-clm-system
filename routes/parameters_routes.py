# parameters_routes.py - Step 4: Parameter Management (FINAL)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime, date
from neo4j import GraphDatabase
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from config import DB_CONFIG, NEO4J_CONFIG

router = APIRouter(prefix="/api/contracts", tags=["parameters"])

# ==================== PYDANTIC MODELS ====================

class ParameterDefinition(BaseModel):
    """Parameter definition from Neo4j"""
    id: str
    name: str
    data_type: str
    is_required: bool
    created_at: Optional[str] = None
    used_in_clauses: List[str]

class ParameterValue(BaseModel):
    """Single parameter value - flexible for template compatibility"""
    parameter_id: str
    value: Any
    
    # Optional fields (ignored but allowed for template compatibility)
    name: Optional[str] = None
    data_type: Optional[str] = None
    is_required: Optional[bool] = None
    
    class Config:
        extra = "ignore"  # Ignore any extra fields
class BulkSetParametersRequest(BaseModel):
    """Bulk set multiple parameters"""
    parameters: List[ParameterValue]

class ContractParameterResponse(BaseModel):
    """Saved parameter response"""
    id: int
    contract_id: str
    parameter_id: str
    value_text: Optional[str]
    value_integer: Optional[int]
    value_decimal: Optional[float]
    value_date: Optional[date]
    value_currency: Optional[Dict]
    provided_by: Optional[str]
    created_at: datetime
    updated_at: datetime

# ==================== DATABASE HELPERS ====================
from config import get_connection, get_neo4j_driver

def get_db():
    """Legacy shim — callers should migrate to get_connection() context manager."""
    import psycopg2
    from config import DB_CONFIG
    return psycopg2.connect(**DB_CONFIG)

# ==================== NEO4J QUERIES ====================

def fetch_parameters_for_active_clauses(contract_id: str) -> List[Dict]:
    """
    Fetch parameters from Neo4j for ACTIVE clauses only.
    Also scans clause texts for orphan {{PLACEHOLDER}} patterns not tracked in Neo4j
    and includes them as synthetic parameters so users can fill them.
    """
    import re

    # Get active clause_ids from Supabase
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT clause_id 
                FROM contract_clauses
                WHERE contract_id = %s AND is_active = true
                ORDER BY sequence
            """, (contract_id,))
            
            clause_rows = cur.fetchall()
            clause_ids = [row["clause_id"] for row in clause_rows]
    finally:
        conn.close()
    
    if not clause_ids:
        return []
    
    # Fetch parameters from Neo4j using EXACT property names
    driver = get_neo4j_driver()
    
    cypher_query = """
    MATCH (c:Clause)-[:CONTAINS_PARAM]->(p:Parameter)
    WHERE c.id IN $clause_ids
    RETURN DISTINCT
      p.id AS id,
      p.name AS name,
      p.data_type AS data_type,
      p.is_required AS is_required,
      p.created_at AS created_at,
      p.description AS description,
      p.example_value AS example_value,
      collect(DISTINCT c.id) AS used_in_clauses
    ORDER BY 
      CASE WHEN p.is_required = true THEN 1 ELSE 2 END,
      p.name
    """
    
    with driver.session() as session:
        result = session.run(cypher_query, {"clause_ids": clause_ids})
        parameters = []
        for record in result:
            parameters.append({
                "id": record["id"],
                "name": record["name"],
                "data_type": record["data_type"],
                "is_required": record["is_required"],
                "created_at": str(record["created_at"]) if record["created_at"] else None,
                "description": record.get("description") or "",
                "example_value": record.get("example_value") or "",
                "used_in_clauses": list(record["used_in_clauses"])
            })

    # --- Detect orphan placeholders in clause texts not tracked in Neo4j ---
    known_names = {p["name"] for p in parameters}  # e.g. {{PARTY_A_NAME}}

    with driver.session() as session:
        texts_result = session.run("""
            MATCH (c:Clause)
            WHERE c.id IN $clause_ids
            RETURN c.id AS clause_id, c.raw_text AS raw_text
        """, {"clause_ids": clause_ids})

        # Also check overridden texts from Supabase
        overridden = {}
        conn2 = get_db()
        try:
            with conn2.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT clause_id, overridden_text FROM contract_clauses
                    WHERE contract_id = %s AND is_active = true AND overridden_text IS NOT NULL
                """, (contract_id,))
                overridden = {r["clause_id"]: r["overridden_text"] for r in cur.fetchall()}
        finally:
            conn2.close()

        orphan_counter = 0
        for rec in texts_result:
            cid = rec["clause_id"]
            text = overridden.get(cid) or rec.get("raw_text") or ""
            # Find all {{PLACEHOLDER}} patterns
            found = re.findall(r'\{\{([A-Z_0-9]+)\}\}', text)
            for placeholder in set(found):
                full_name = f"{{{{{placeholder}}}}}"
                if full_name not in known_names:
                    orphan_counter += 1
                    synthetic_id = f"ORPHAN_{placeholder}"
                    parameters.append({
                        "id": synthetic_id,
                        "name": full_name,
                        "data_type": "String",
                        "is_required": True,
                        "created_at": None,
                        "description": f"Parameter found in clause text but not in knowledge graph",
                        "example_value": "",
                        "used_in_clauses": [cid],
                    })
                    known_names.add(full_name)

    return parameters

# ==================== PARAMETER DESCRIPTION GENERATOR ====================

_description_cache: dict = {}  # Cleared on server restart

def _generate_missing_descriptions(parameters: list, contract_id: str):
    """
    Generate short descriptions for parameters that don't have them.
    Uses a single LLM call for all missing descriptions (token-efficient).
    Results are cached in memory.
    """
    # Find params needing descriptions
    needs_desc = []
    for p in parameters:
        bare_name = p["name"].strip("{}").replace("_", " ").title()
        if p["id"] in _description_cache:
            p["description"] = _description_cache[p["id"]]
            continue
        if not p.get("description") or p["description"] in ("", "Parameter found in clause text but not in knowledge graph"):
            needs_desc.append(p)

    if not needs_desc:
        return

    # Try LLM batch generation
    try:
        from graph_rag_engine import llm_client
        if not llm_client.is_configured():
            # Fallback: generate simple descriptions from the name
            for p in needs_desc:
                bare = p["name"].strip("{}").replace("_", " ")
                p["description"] = f"Enter the {bare.lower()} for this contract"
                _description_cache[p["id"]] = p["description"]
            return

        # Get contract info for context
        conn = get_db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT contract_type, jurisdiction FROM contracts WHERE id = %s", (contract_id,))
                contract = cur.fetchone() or {}
        finally:
            conn.close()

        param_names = [p["name"].strip("{}") for p in needs_desc]
        prompt = f"""Generate a short user-friendly description for each contract parameter below.
The contract is a {contract.get('contract_type', 'service agreement').replace('_', ' ')} under {contract.get('jurisdiction', 'India')} jurisdiction.

IMPORTANT RULES:
1. Write for a non-lawyer. Explain legal terms in plain English.
2. If the parameter name contains legal jargon, explain what it means in simple words.
3. Include what kind of value to enter (e.g., "Enter a number of days", "Enter a date like 2026-01-01").
4. Keep each description to 1-2 sentences max.

Examples of GOOD descriptions:
- CURE_PERIOD: "How many days the other party gets to fix a problem before you can cancel the contract. Example: 15 days"
- FM_NOTICE_DAYS: "Days to notify the other party when an unforeseeable event (like a natural disaster, pandemic, or government order) prevents you from fulfilling the contract. Example: 5 days"
- NON_SOLICIT_PERIOD: "How long after the contract ends you agree not to recruit or hire the other party's employees. Example: 1 year"
- LATE_PAYMENT_RATE: "Interest charged on overdue payments. Example: 1.5% per month"
- ARBITRATION_SEAT: "The city where any legal disputes will be resolved through arbitration. Example: Mumbai"

Parameters: {', '.join(param_names)}

Respond in JSON format:
{{{', '.join(f'"{n}": "description"' for n in param_names)}}}"""

        result = llm_client.generate(prompt, "You are a legal contract assistant. Give brief, clear descriptions.")

        for p in needs_desc:
            bare = p["name"].strip("{}")
            desc = result.get(bare, "")
            if desc:
                p["description"] = desc
                _description_cache[p["id"]] = desc
            else:
                p["description"] = f"Enter the {bare.replace('_', ' ').lower()} for this contract"
                _description_cache[p["id"]] = p["description"]

    except Exception:
        # Fallback: simple name-based descriptions
        for p in needs_desc:
            bare = p["name"].strip("{}").replace("_", " ")
            p["description"] = f"Enter the {bare.lower()} for this contract"
            _description_cache[p["id"]] = p["description"]


# ==================== VALUE CONVERSION HELPER ====================

def convert_parameter_value(data_type: str, value: Any) -> tuple:
    """
    Convert value to appropriate column based on data_type.
    Falls back to text storage if conversion fails (e.g., "2 days" for an integer field).
    Returns: (value_text, value_integer, value_decimal, value_date, value_currency)
    """
    if value is None or value == "":
        return None, None, None, None, None
    
    # Normalize data_type (case-insensitive)
    data_type_lower = data_type.lower()
    
    if data_type_lower == "string" or data_type_lower == "text":
        return str(value), None, None, None, None
    
    elif data_type_lower == "integer" or data_type_lower == "int" or data_type_lower == "number":
        try:
            return None, int(value), None, None, None
        except (ValueError, TypeError):
            return str(value), None, None, None, None
    
    elif data_type_lower == "decimal" or data_type_lower == "float" or data_type_lower == "double":
        try:
            return None, None, float(value), None, None
        except (ValueError, TypeError):
            return str(value), None, None, None, None
    
    elif data_type_lower == "date" or data_type_lower == "datetime":
        try:
            if isinstance(value, str):
                from datetime import datetime
                parsed_date = datetime.strptime(value, "%Y-%m-%d").date()
                return None, None, None, parsed_date, None
            elif isinstance(value, date):
                return None, None, None, value, None
            else:
                return str(value), None, None, None, None
        except (ValueError, TypeError):
            return str(value), None, None, None, None
    
    elif data_type_lower == "currency" or data_type_lower == "money":
        if isinstance(value, dict):
            return None, None, None, None, value
        else:
            return str(value), None, None, None, None
    
    elif data_type_lower == "boolean" or data_type_lower == "bool":
        return str(value).lower(), None, None, None, None
    
    else:
        # Default: store as text
        return str(value), None, None, None, None

# ==================== ROUTES ====================
# ==================== TEMPLATE ROUTES FOR TESTING ====================

@router.get("/{contract_id}/parameters/grouped")
async def get_parameters_grouped(
    contract_id: str,
    format: str = "display",   # "display" | "template"
    group_by: str = "clause",  # "clause" | "semantic"
):
    """
    Get parameters grouped for UI rendering.

    Query params:
    - format=display (default): Full parameter details for the stepper UI
    - format=template: Simplified flat list ready for POST /bulk
    - group_by=clause (default): Grouped by clause type (existing behaviour)
    - group_by=semantic: Grouped by semantic category (People/Dates/Financial/…)
      Each parameter is enriched with its current value + provenance (provided_by).

    Examples:
    - GET /api/contracts/{id}/parameters/grouped
    - GET /api/contracts/{id}/parameters/grouped?group_by=semantic
    - GET /api/contracts/{id}/parameters/grouped?format=template
    """
    # Verify contract exists
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id FROM contracts WHERE id = %s", (contract_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Contract not found")
    finally:
        conn.close()

    # Fetch parameter definitions for active clauses from Neo4j
    parameters = fetch_parameters_for_active_clauses(contract_id)

    if not parameters:
        return {
            "groups": [],
            "total_parameters": 0,
            "filled_parameters": 0,
            "auto_filled_count": 0,
            "defaulted_count": 0,
            "user_filled_count": 0,
            "cascade_filled_count": 0,
            "remaining_count": 0,
            "message": "No parameters found for active clauses",
        }

    # ── Fetch saved values + provenance from Postgres ──────────────────────
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    parameter_id,
                    value_text, value_integer, value_decimal,
                    value_date, value_currency,
                    provided_by
                FROM contract_parameters
                WHERE contract_id = %s
            """, (contract_id,))
            rows = cur.fetchall()
    finally:
        conn.close()

    # Build lookup: param_id → {value, provided_by}
    saved: dict = {}
    for row in rows:
        pid = row["parameter_id"]
        if row["value_text"] is not None:
            val = row["value_text"]
        elif row["value_integer"] is not None:
            val = row["value_integer"]
        elif row["value_decimal"] is not None:
            val = float(row["value_decimal"])
        elif row["value_date"] is not None:
            val = row["value_date"].isoformat()
        elif row["value_currency"] is not None:
            val = row["value_currency"]
        else:
            val = None
        saved[pid] = {"value": val, "provided_by": row["provided_by"]}

    # ── Enrich each parameter with saved data ──────────────────────────────
    for param in parameters:
        entry = saved.get(param["id"], {})
        param["current_value"] = entry.get("value")
        param["provided_by"] = entry.get("provided_by")   # None = unfilled
        raw_name = param["name"].strip("{}").replace("_", " ").title()
        param["display_name"] = raw_name
        if not param.get("description"):
            param["description"] = ""
        if not param.get("example_value"):
            param["example_value"] = ""

    # ── Generate descriptions for parameters missing them ──────────────────
    _generate_missing_descriptions(parameters, contract_id)

    # ── Summary counters ───────────────────────────────────────────────────
    total = len(parameters)
    filled = sum(1 for p in parameters if p["current_value"] is not None)
    auto_filled = sum(1 for p in parameters if p.get("provided_by") == "auto_fill")
    defaulted = sum(1 for p in parameters if p.get("provided_by") == "system_default")
    cascaded = sum(1 for p in parameters if p.get("provided_by") == "cascade")
    user_filled = sum(1 for p in parameters if p.get("provided_by") == "user")
    remaining = total - filled

    # ── template format ────────────────────────────────────────────────────
    if format == "template":
        clause_groups = _group_by_clause(parameters)
        flat = [
            {
                "parameter_id": param["id"],
                "name": param["name"],
                "data_type": param["data_type"],
                "is_required": param["is_required"],
                "value": param["current_value"] if param["current_value"] is not None else "",
            }
            for group in clause_groups
            for param in group["parameters"]
        ]
        return {
            "instructions": "Fill in the 'value' field for each parameter, then POST to the endpoint below",
            "post_url": f"/api/contracts/{contract_id}/parameters/bulk",
            "post_method": "POST",
            "parameters": flat,
        }

    # ── semantic grouping ──────────────────────────────────────────────────
    if group_by == "semantic":
        groups = _group_by_semantic(parameters)
        return {
            "groups": groups,
            "total_parameters": total,
            "filled_parameters": filled,
            "auto_filled_count": auto_filled,
            "defaulted_count": defaulted,
            "cascade_filled_count": cascaded,
            "user_filled_count": user_filled,
            "remaining_count": remaining,
            "required_parameters": sum(1 for p in parameters if p["is_required"]),
            "optional_parameters": sum(1 for p in parameters if not p["is_required"]),
            "completion_percentage": round(filled / total * 100) if total else 100,
        }

    # ── clause grouping (default) ──────────────────────────────────────────
    sorted_groups = _group_by_clause(parameters)
    return {
        "groups": sorted_groups,
        "total_parameters": total,
        "total_groups": len(sorted_groups),
        "filled_parameters": filled,
        "required_parameters": sum(1 for p in parameters if p["is_required"]),
        "optional_parameters": sum(1 for p in parameters if not p["is_required"]),
        "auto_filled_count": auto_filled,
        "defaulted_count": defaulted,
        "cascade_filled_count": cascaded,
        "remaining_count": remaining,
        "completion_percentage": round(filled / total * 100) if total else 100,
    }


# ==================== GROUPING HELPERS ====================

SEMANTIC_CATEGORIES: dict = {
    "core":             {"label": "People & Parties",      "icon": "Users",        "color": "blue",   "order": 1},
    "scope":            {"label": "Scope & Deliverables",  "icon": "FileText",     "color": "purple", "order": 2},
    "payment":          {"label": "Financial Terms",       "icon": "DollarSign",   "color": "green",  "order": 3},
    "term":             {"label": "Dates & Duration",      "icon": "Calendar",     "color": "orange", "order": 4},
    "confidentiality":  {"label": "Confidentiality",       "icon": "Lock",         "color": "red",    "order": 5},
    "non_compete":      {"label": "Non-Compete",           "icon": "ShieldOff",    "color": "red",    "order": 6},
    "ip":               {"label": "Intellectual Property", "icon": "Lightbulb",    "color": "yellow", "order": 7},
    "termination":      {"label": "Termination",           "icon": "XCircle",      "color": "red",    "order": 8},
    "liability":        {"label": "Liability & Indemnity", "icon": "Shield",       "color": "slate",  "order": 9},
    "dispute_resolution": {"label": "Dispute Resolution", "icon": "Scale",        "color": "slate",  "order": 10},
    "governing_law":    {"label": "Governing Law",         "icon": "BookOpen",     "color": "slate",  "order": 11},
    "data_protection":  {"label": "Data Protection",      "icon": "Database",     "color": "blue",   "order": 12},
    "sla":              {"label": "SLA & Performance",    "icon": "Activity",     "color": "green",  "order": 13},
    "other":            {"label": "Other",                 "icon": "MoreHorizontal","color": "gray",  "order": 99},
}

_NAME_TO_CATEGORY = {
    "PARTY": "core", "WITNESS": "core", "SIGNATORY": "core", "NAME": "core",
    "EMAIL": "core", "PHONE": "core", "ADDRESS": "core", "CITY": "core",
    "STATE": "core", "COUNTRY": "core", "ENTITY": "core",
    "DATE": "term", "DURATION": "term", "TERM": "term", "PERIOD": "term",
    "RENEWAL": "term", "EXPIRY": "term",
    "AMOUNT": "payment", "VALUE": "payment", "FEE": "payment",
    "PAYMENT": "payment", "CURRENCY": "payment", "PRICE": "payment",
    "RATE": "payment", "SALARY": "payment", "COMPENSATION": "payment", "PENALTY": "payment",
    "CONFIDENTIAL": "confidentiality", "DISCLOSURE": "confidentiality",
    "RETAIN": "confidentiality", "SECRET": "confidentiality",
    "COMPETE": "non_compete", "NON_COMPETE": "non_compete",
    "SOLICIT": "non_compete", "GEOGRAPHIC": "non_compete",
    "IP": "ip", "INTELLECTUAL": "ip", "COPYRIGHT": "ip",
    "PATENT": "ip", "TRADEMARK": "ip", "LICENSE": "ip",
    "WORK": "scope", "SCOPE": "scope", "DELIVERABLE": "scope",
    "SERVICE": "scope", "MILESTONE": "scope", "ACCEPTANCE": "scope",
    "TERMINATION": "termination", "NOTICE": "termination",
    "CURE": "termination", "DISSOLUTION": "termination",
    "LIABILITY": "liability", "INDEMNIF": "liability", "INDEMN": "liability",
    "WARRANTY": "liability", "INSURANCE": "liability",
    "ARBITRATION": "dispute_resolution", "DISPUTE": "dispute_resolution",
    "MEDIATION": "dispute_resolution", "FORUM": "dispute_resolution",
    "JURISDICTION": "dispute_resolution",
    "GOVERNING": "governing_law", "LAW": "governing_law", "STAMP": "governing_law",
    "DATA": "data_protection", "BREACH": "data_protection",
    "GDPR": "data_protection", "PROCESSING": "data_protection",
    "SLA": "sla", "UPTIME": "sla", "RESPONSE": "sla", "SUPPORT": "sla",
}


def _infer_category(placeholder_name: str) -> str:
    """Infer semantic category from {{PLACEHOLDER_NAME}}."""
    bare = placeholder_name.strip("{}").upper()
    for keyword, cat in _NAME_TO_CATEGORY.items():
        if keyword in bare:
            return cat
    return "other"


def _group_by_semantic(parameters: list) -> list:
    """Group parameters by semantic category, ordered by display priority."""
    buckets: dict = {}
    for param in parameters:
        cat = param.get("category") or _infer_category(param["name"])
        if cat not in SEMANTIC_CATEGORIES:
            cat = "other"
        if cat not in buckets:
            meta = SEMANTIC_CATEGORIES[cat]
            buckets[cat] = {
                "category": cat,
                "label": meta["label"],
                "icon": meta["icon"],
                "color": meta["color"],
                "order": meta["order"],
                "parameters": [],
                "total_count": 0,
                "filled_count": 0,
                "required_count": 0,
                "auto_filled_count": 0,
                "defaulted_count": 0,
                "all_auto_filled": False,
            }
        if not any(p["id"] == param["id"] for p in buckets[cat]["parameters"]):
            buckets[cat]["parameters"].append(param)
            buckets[cat]["total_count"] += 1
            if param["current_value"] is not None:
                buckets[cat]["filled_count"] += 1
            if param["is_required"]:
                buckets[cat]["required_count"] += 1
            if param.get("provided_by") == "auto_fill":
                buckets[cat]["auto_filled_count"] += 1
            if param.get("provided_by") == "system_default":
                buckets[cat]["defaulted_count"] += 1

    auto_sources = {"auto_fill", "system_default", "cascade"}
    for bucket in buckets.values():
        fully_filled = bucket["filled_count"] == bucket["total_count"]
        all_auto = all(
            p["provided_by"] in auto_sources
            for p in bucket["parameters"]
            if p["current_value"] is not None
        )
        bucket["all_auto_filled"] = fully_filled and all_auto

    return sorted(buckets.values(), key=lambda x: x["order"])


def _group_by_clause(parameters: list) -> list:
    """Original behaviour: group by clause type prefix (PART, CONF, PAY, …)."""
    grouped: dict = {}
    for param in parameters:
        for clause_id in param["used_in_clauses"]:
            clause_type = clause_id.split("_")[0]
            if clause_type not in grouped:
                grouped[clause_type] = {
                    "clause_type": clause_type,
                    "clause_type_label": get_clause_type_label(clause_type),
                    "parameters": [],
                    "required_count": 0,
                    "optional_count": 0,
                    "filled_count": 0,
                }
            param_ids = [p["id"] for p in grouped[clause_type]["parameters"]]
            if param["id"] not in param_ids:
                grouped[clause_type]["parameters"].append(param)
                if param["is_required"]:
                    grouped[clause_type]["required_count"] += 1
                else:
                    grouped[clause_type]["optional_count"] += 1
                if param["current_value"] is not None:
                    grouped[clause_type]["filled_count"] += 1
    return sorted(grouped.values(), key=lambda x: x["clause_type"])


def get_clause_type_label(clause_type: str) -> str:
    """
    Convert clause type code to human-readable label
    """
    labels = {
        "PART": "Parties & Recitals",
        "DEFN": "Definitions",
        "SCOPE": "Scope of Agreement",
        "CONF": "Confidentiality",
        "NDISC": "Non-Disclosure",
        "NONCOMP": "Non-Compete",
        "NONSOL": "Non-Solicitation",
        "IP": "Intellectual Property",
        "PAY": "Payment Terms",
        "TERM": "Term & Renewal",
        "TERMB": "Termination for Cause",
        "TERMC": "Termination for Convenience",
        "SURV": "Survival & Effect of Termination",
        "REP": "Representations & Warranties",
        "INDEM": "Indemnification",
        "LIAB": "Limitation of Liability",
        "FORCE": "Force Majeure",
        "GOV": "Governing Law",
        "DISP": "Dispute Resolution",
        "AMEND": "Amendments",
        "ENTIRE": "Entire Agreement",
        "SEVER": "Severability",
        "NOTICE": "Notices",
        "ASSIGN": "Assignment",
        "WAIVER": "Waiver"
    }
    return labels.get(clause_type, clause_type)
@router.get("/{contract_id}/parameters/required", response_model=List[ParameterDefinition])
async def get_required_parameters(contract_id: str):
    """
    Step 4.1: Get all parameters needed for active clauses
    
    Returns parameter definitions from Neo4j for frontend form rendering
    """
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id FROM contracts WHERE id = %s", (contract_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Contract not found")
    finally:
        conn.close()
    
    parameters = fetch_parameters_for_active_clauses(contract_id)
    return parameters


@router.get("/{contract_id}/parameters/values", response_model=List[ContractParameterResponse])
async def get_parameter_values(contract_id: str):
    """
    Get saved parameter values for a contract
    """
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM contract_parameters
                WHERE contract_id = %s
                ORDER BY created_at
            """, (contract_id,))
            return cur.fetchall()
    finally:
        conn.close()


@router.get("/{contract_id}/parameters/form", response_model=Dict)
async def get_parameter_form(contract_id: str):
    """
    Step 4.2: Get complete form data (definitions + saved values)
    
    Perfect for frontend to render a form with pre-filled values
    """
    # Get parameter definitions
    parameters = fetch_parameters_for_active_clauses(contract_id)
    
    # Get saved values
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    parameter_id,
                    value_text,
                    value_integer,
                    value_decimal,
                    value_date,
                    value_currency
                FROM contract_parameters
                WHERE contract_id = %s
            """, (contract_id,))
            
            saved_rows = cur.fetchall()
            saved_values = {}
            for row in saved_rows:
                param_id = row["parameter_id"]
                # Get actual value from appropriate column
                if row["value_text"] is not None:
                    saved_values[param_id] = row["value_text"]
                elif row["value_integer"] is not None:
                    saved_values[param_id] = row["value_integer"]
                elif row["value_decimal"] is not None:
                    saved_values[param_id] = float(row["value_decimal"])
                elif row["value_date"] is not None:
                    saved_values[param_id] = row["value_date"].isoformat()
                elif row["value_currency"] is not None:
                    saved_values[param_id] = row["value_currency"]
    finally:
        conn.close()
    
    # Calculate completion
    required_params = [p for p in parameters if p["is_required"]]
    filled_required = sum(1 for p in required_params if p["id"] in saved_values)
    
    return {
        "parameter_definitions": parameters,
        "saved_values": saved_values,
        "total_parameters": len(parameters),
        "total_required": len(required_params),
        "filled_required": filled_required,
        "completion_percentage": (filled_required / len(required_params) * 100) if required_params else 100
    }


@router.post("/{contract_id}/parameters", response_model=ContractParameterResponse)
async def set_parameter_value(contract_id: str, request: ParameterValue, provided_by: Optional[str] = None):
    """
    Step 4.3: Set a single parameter value
    
    Automatically determines which column to use based on data_type from Neo4j
    """
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id FROM contracts WHERE id = %s", (contract_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Contract not found")
    finally:
        conn.close()
    
    # Get parameter data_type from Neo4j (default to String for orphan params)
    driver = get_neo4j_driver()
    data_type = "String"
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Parameter {id: $parameter_id})
            RETURN p.data_type AS data_type
        """, {"parameter_id": request.parameter_id})
        
        param_def = result.single()
        if param_def:
            data_type = param_def["data_type"]
    
    # Convert value to appropriate columns
    value_text, value_integer, value_decimal, value_date, value_currency = convert_parameter_value(
        data_type, request.value
    )
    
    # Upsert parameter value
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO contract_parameters (
                    contract_id, parameter_id,
                    value_text, value_integer, value_decimal, 
                    value_date, value_currency, provided_by
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (contract_id, parameter_id) 
                DO UPDATE SET
                    value_text = EXCLUDED.value_text,
                    value_integer = EXCLUDED.value_integer,
                    value_decimal = EXCLUDED.value_decimal,
                    value_date = EXCLUDED.value_date,
                    value_currency = EXCLUDED.value_currency,
                    provided_by = EXCLUDED.provided_by,
                    updated_at = NOW()
                RETURNING *
            """, (
                contract_id, request.parameter_id,
                value_text, value_integer, value_decimal, value_date,
                json.dumps(value_currency) if value_currency else None,
                provided_by
            ))
            
            result = cur.fetchone()
            conn.commit()
            return result
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving parameter: {str(e)}")
    finally:
        conn.close()


@router.post("/{contract_id}/parameters/bulk", response_model=List[ContractParameterResponse])
async def set_parameters_bulk(contract_id: str, request: BulkSetParametersRequest, provided_by: Optional[str] = None):
    """
    Step 4.4: Set multiple parameters at once
    
    Frontend submits entire form in one request
    """
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id FROM contracts WHERE id = %s", (contract_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Contract not found")
    finally:
        conn.close()
    
    # Get all parameter data_types from Neo4j
    driver = get_neo4j_driver()
    param_ids = [p.parameter_id for p in request.parameters]
    
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Parameter)
            WHERE p.id IN $param_ids
            RETURN p.id AS id, p.data_type AS data_type
        """, {"param_ids": param_ids})
        
        param_types = {rec["id"]: rec["data_type"] for rec in result}
    
    # Insert/update all parameters
    conn = get_db()
    saved_params = []
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            for param in request.parameters:
                # Get data type — default to "String" for orphan params not in Neo4j
                data_type = param_types.get(param.parameter_id, "String")
                
                # Convert value
                value_text, value_integer, value_decimal, value_date, value_currency = convert_parameter_value(
                    data_type, param.value
                )
                
                # Upsert
                cur.execute("""
                    INSERT INTO contract_parameters (
                        contract_id, parameter_id,
                        value_text, value_integer, value_decimal, 
                        value_date, value_currency, provided_by
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (contract_id, parameter_id) 
                    DO UPDATE SET
                        value_text = EXCLUDED.value_text,
                        value_integer = EXCLUDED.value_integer,
                        value_decimal = EXCLUDED.value_decimal,
                        value_date = EXCLUDED.value_date,
                        value_currency = EXCLUDED.value_currency,
                        provided_by = EXCLUDED.provided_by,
                        updated_at = NOW()
                    RETURNING *
                """, (
                    contract_id, param.parameter_id,
                    value_text, value_integer, value_decimal, value_date,
                    json.dumps(value_currency) if value_currency else None,
                    provided_by
                ))
                
                saved_params.append(cur.fetchone())
            
            conn.commit()
            return saved_params
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving parameters: {str(e)}")
    finally:
        conn.close()


@router.delete("/{contract_id}/parameters/{parameter_id}")
async def delete_parameter_value(contract_id: str, parameter_id: str):
    """Delete a parameter value (for optional parameters)"""
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                DELETE FROM contract_parameters
                WHERE contract_id = %s AND parameter_id = %s
                RETURNING parameter_id
            """, (contract_id, parameter_id))
            
            result = cur.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Parameter not found")
            
            conn.commit()
            return {"message": f"Parameter {parameter_id} deleted successfully"}
    finally:
        conn.close()


@router.get("/{contract_id}/parameters/validation")
async def validate_parameters(contract_id: str):
    """
    Step 4.5: Validate all required parameters are filled
    
    Returns:
    - is_complete: Can user proceed to Step 5?
    - missing_required: List of required parameters not yet filled
    """
    parameters = fetch_parameters_for_active_clauses(contract_id)
    required_params = [p for p in parameters if p["is_required"]]
    
    if not required_params:
        return {
            "is_complete": True,
            "total_required": 0,
            "filled_required": 0,
            "missing_required": [],
            "message": "No required parameters"
        }
    
    # Get filled parameters
    conn = get_db()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT parameter_id 
                FROM contract_parameters
                WHERE contract_id = %s
            """, (contract_id,))
            
            filled_param_ids = {row["parameter_id"] for row in cur.fetchall()}
    finally:
        conn.close()
    
    # Find missing required parameters
    missing_required = []
    for param in required_params:
        if param["id"] not in filled_param_ids:
            missing_required.append({
                "parameter_id": param["id"],
                "parameter_name": param["name"],
                "data_type": param["data_type"]
            })
    
    return {
        "is_complete": len(missing_required) == 0,
        "total_required": len(required_params),
        "filled_required": len(required_params) - len(missing_required),
        "missing_required": missing_required,
        "completion_percentage": ((len(required_params) - len(missing_required)) / len(required_params) * 100) if required_params else 100
    }
