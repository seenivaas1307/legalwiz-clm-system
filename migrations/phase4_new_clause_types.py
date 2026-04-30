"""
Phase 4: New Clause Types + Variants
- Create `profit-sharing-terms` ClauseType with 3 clause variants
- Create `data-processing-obligations` ClauseType with 3 clause variants
- Wire them into appropriate contract types
- Add parameters and relationship edges
"""

from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)


# ==========================================
# PROFIT-SHARING TERMS
# ==========================================

PROFIT_SHARING_CLAUSE_TYPE = {
    "id": "profit-sharing-terms",
    "name": "Profit Sharing and Distribution",
    "category": "Financial",
    "importance_level": "Critical",
}

PROFIT_SHARING_CLAUSES = [
    {
        "id": "PROFIT_STD_001",
        "clause_type": "profit-sharing-terms",
        "name": "Profit Sharing and Distribution — Standard",
        "variant": "Standard",
        "jurisdiction": "India",
        "risk_level": "Low",
        "raw_text": (
            "PROFIT SHARING AND DISTRIBUTION\n\n"
            "1. PROFIT/LOSS ALLOCATION\n"
            "All net profits and losses of the Partnership shall be shared between the Partners in the ratio of "
            "{{PROFIT_SHARE_RATIO}}, unless otherwise agreed in writing by all Partners.\n\n"
            "2. DISTRIBUTION SCHEDULE\n"
            "Profits shall be distributed {{DISTRIBUTION_FREQUENCY}} within {{DISTRIBUTION_DAYS}} days after the close "
            "of each {{DISTRIBUTION_FREQUENCY}} period, subject to the retention of adequate working capital reserves.\n\n"
            "3. CAPITAL CONTRIBUTIONS\n"
            "Each Partner's initial capital contribution shall be as set forth in Schedule A. Additional capital contributions "
            "may be required by mutual written agreement of all Partners.\n\n"
            "4. DRAWING RIGHTS\n"
            "Partners may draw against anticipated profits up to {{MAX_DRAW_AMOUNT}} per {{DRAW_PERIOD}}, "
            "subject to availability of funds and approval by {{DRAW_APPROVAL_AUTHORITY}}.\n\n"
            "5. ACCOUNTING\n"
            "The Partnership shall maintain proper books of account in accordance with Indian Accounting Standards. "
            "Annual accounts shall be prepared and audited by a Chartered Accountant within {{AUDIT_DEADLINE_DAYS}} days "
            "of the financial year end."
        ),
    },
    {
        "id": "PROFIT_MOD_001",
        "clause_type": "profit-sharing-terms",
        "name": "Profit Sharing and Distribution — Moderate",
        "variant": "Moderate",
        "jurisdiction": "India",
        "risk_level": "Medium",
        "raw_text": (
            "PROFIT SHARING AND DISTRIBUTION\n\n"
            "1. PROFIT/LOSS ALLOCATION\n"
            "1.1. Net profits and losses shall be allocated among Partners in the ratio of {{PROFIT_SHARE_RATIO}}.\n"
            "1.2. 'Net Profit' means gross revenue less all operating expenses, taxes, depreciation, and agreed reserves.\n"
            "1.3. Losses exceeding a Partner's capital account shall be allocated proportionally; no Partner shall be "
            "required to contribute additional capital to cover losses without written consent.\n\n"
            "2. DISTRIBUTION MECHANISM\n"
            "2.1. Distributions shall occur {{DISTRIBUTION_FREQUENCY}} within {{DISTRIBUTION_DAYS}} days.\n"
            "2.2. A minimum working capital reserve of {{MIN_RESERVE_AMOUNT}} shall be maintained before distributions.\n"
            "2.3. Tax withholding (TDS under Section 194J / 194C of the Income Tax Act, 1961) shall be deducted at source "
            "where applicable before distribution.\n\n"
            "3. CAPITAL ACCOUNTS AND CONTRIBUTIONS\n"
            "3.1. Each Partner's capital account shall be maintained separately, recording contributions, drawings, and profit/loss allocations.\n"
            "3.2. Additional capital calls require {{CAPITAL_CALL_NOTICE_DAYS}} days' prior written notice and approval by "
            "Partners holding at least {{CAPITAL_CALL_APPROVAL_THRESHOLD}}% of total capital.\n"
            "3.3. Interest at {{CAPITAL_INTEREST_RATE}}% per annum shall accrue on capital contributions exceeding the "
            "agreed initial amount.\n\n"
            "4. DRAWING RIGHTS AND PARTNER REMUNERATION\n"
            "4.1. Working Partners shall be entitled to remuneration as permitted under Section 40(b) of the Income Tax Act, 1961.\n"
            "4.2. Drawings shall not exceed {{MAX_DRAW_AMOUNT}} per {{DRAW_PERIOD}} without unanimous partner consent.\n"
            "4.3. Excess drawings shall attract interest at {{EXCESS_DRAW_INTEREST_RATE}}% per annum.\n\n"
            "5. FINANCIAL REPORTING AND AUDIT\n"
            "5.1. Monthly management accounts shall be circulated to all Partners within {{MONTHLY_REPORT_DAYS}} days.\n"
            "5.2. Annual accounts shall be audited by an independent Chartered Accountant.\n"
            "5.3. Any Partner may request a special audit at the Partnership's expense upon {{SPECIAL_AUDIT_NOTICE_DAYS}} days' notice."
        ),
    },
    {
        "id": "PROFIT_STR_001",
        "clause_type": "profit-sharing-terms",
        "name": "Profit Sharing and Distribution — Strict",
        "variant": "Strict",
        "jurisdiction": "India",
        "risk_level": "High",
        "raw_text": (
            "PROFIT SHARING AND DISTRIBUTION\n\n"
            "1. PROFIT/LOSS ALLOCATION AND WATERFALL\n"
            "1.1. Net profits shall be distributed in the following waterfall:\n"
            "  (a) First, repayment of any outstanding capital call obligations;\n"
            "  (b) Second, preferred return of {{PREFERRED_RETURN_RATE}}% per annum on unreturned capital contributions;\n"
            "  (c) Third, to the Managing Partner as carried interest of {{CARRY_PERCENTAGE}}% of remaining profits;\n"
            "  (d) Fourth, balance distributed in the ratio of {{PROFIT_SHARE_RATIO}}.\n"
            "1.2. Losses shall be allocated proportionally to capital accounts; no Partner's capital account shall be "
            "reduced below zero without that Partner's express written consent.\n"
            "1.3. 'Net Profit' shall be computed in accordance with Indian Accounting Standards (Ind AS) and shall "
            "account for depreciation, amortization, provisions, and statutory reserves.\n\n"
            "2. DISTRIBUTION MECHANISM AND CONTROLS\n"
            "2.1. Distributions shall occur {{DISTRIBUTION_FREQUENCY}}, subject to:\n"
            "  (a) Maintenance of minimum cash reserves of {{MIN_RESERVE_AMOUNT}} or {{RESERVE_PERCENTAGE}}% of annual "
            "revenue, whichever is higher;\n"
            "  (b) No outstanding defaults or material breaches by any Partner;\n"
            "  (c) Compliance with all tax withholding obligations.\n"
            "2.2. Distributions shall be accompanied by a detailed computation certified by the Partnership's auditor.\n"
            "2.3. Disputed distributions shall be held in escrow pending resolution under the dispute resolution clause.\n\n"
            "3. CAPITAL ACCOUNTS, CONTRIBUTIONS, AND DILUTION\n"
            "3.1. Mandatory additional capital contributions require {{CAPITAL_CALL_NOTICE_DAYS}} days' notice and "
            "approval by Partners holding {{CAPITAL_CALL_APPROVAL_THRESHOLD}}% of capital.\n"
            "3.2. A Partner failing to meet a capital call within {{CAPITAL_CURE_PERIOD_DAYS}} days shall face:\n"
            "  (a) Proportional dilution of their profit share; and\n"
            "  (b) Default interest at {{DEFAULT_INTEREST_RATE}}% per annum.\n"
            "3.3. Capital contributions shall earn interest at {{CAPITAL_INTEREST_RATE}}% per annum, payable quarterly.\n\n"
            "4. PARTNER REMUNERATION, DRAWINGS, AND CLAWBACK\n"
            "4.1. Working Partner remuneration shall comply with Section 40(b) limits.\n"
            "4.2. No drawings shall be permitted if the Partnership's cash position falls below {{MIN_CASH_THRESHOLD}}.\n"
            "4.3. Distributions received in excess of a Partner's entitlement shall be subject to clawback within "
            "{{CLAWBACK_PERIOD_DAYS}} days of discovery, with interest at {{DEFAULT_INTEREST_RATE}}% per annum.\n\n"
            "5. FINANCIAL GOVERNANCE\n"
            "5.1. The Partnership shall appoint an independent auditor approved by all Partners.\n"
            "5.2. Monthly P&L, balance sheet, and cash flow statements shall be circulated within {{MONTHLY_REPORT_DAYS}} days.\n"
            "5.3. Quarterly partner meetings shall review financial performance and approve distribution recommendations.\n"
            "5.4. Forensic audit rights: any Partner may commission a forensic audit at the Partnership's expense upon "
            "demonstrating reasonable grounds for concern."
        ),
    },
]

PROFIT_SHARING_PARAMS = [
    {"id": "P_300", "name": "{{PROFIT_SHARE_RATIO}}", "data_type": "text", "is_required": True,
     "description": "Profit/loss sharing ratio (e.g., '50:50', '60:40')"},
    {"id": "P_301", "name": "{{DISTRIBUTION_FREQUENCY}}", "data_type": "text", "is_required": True,
     "description": "Frequency of profit distributions (e.g., 'quarterly', 'annually')"},
    {"id": "P_302", "name": "{{DISTRIBUTION_DAYS}}", "data_type": "number", "is_required": True,
     "description": "Days after period close for distribution"},
    {"id": "P_303", "name": "{{MAX_DRAW_AMOUNT}}", "data_type": "currency", "is_required": True,
     "description": "Maximum drawing amount per period"},
    {"id": "P_304", "name": "{{DRAW_PERIOD}}", "data_type": "text", "is_required": True,
     "description": "Drawing period (e.g., 'month', 'quarter')"},
    {"id": "P_305", "name": "{{DRAW_APPROVAL_AUTHORITY}}", "data_type": "text", "is_required": False,
     "description": "Authority required for drawing approval"},
    {"id": "P_306", "name": "{{AUDIT_DEADLINE_DAYS}}", "data_type": "number", "is_required": False,
     "description": "Days after FY end for audit completion"},
    {"id": "P_307", "name": "{{MIN_RESERVE_AMOUNT}}", "data_type": "currency", "is_required": False,
     "description": "Minimum working capital reserve"},
    {"id": "P_308", "name": "{{CAPITAL_CALL_NOTICE_DAYS}}", "data_type": "number", "is_required": False,
     "description": "Notice days for additional capital calls"},
    {"id": "P_309", "name": "{{CAPITAL_CALL_APPROVAL_THRESHOLD}}", "data_type": "number", "is_required": False,
     "description": "Percentage of capital required to approve capital calls"},
    {"id": "P_310", "name": "{{CAPITAL_INTEREST_RATE}}", "data_type": "number", "is_required": False,
     "description": "Interest rate on excess capital contributions (%)"},
    {"id": "P_311", "name": "{{EXCESS_DRAW_INTEREST_RATE}}", "data_type": "number", "is_required": False,
     "description": "Interest rate on excess drawings (%)"},
    {"id": "P_312", "name": "{{MONTHLY_REPORT_DAYS}}", "data_type": "number", "is_required": False,
     "description": "Days after month-end for management accounts"},
    {"id": "P_313", "name": "{{SPECIAL_AUDIT_NOTICE_DAYS}}", "data_type": "number", "is_required": False,
     "description": "Notice period for requesting special audit"},
    {"id": "P_314", "name": "{{PREFERRED_RETURN_RATE}}", "data_type": "number", "is_required": False,
     "description": "Preferred return rate on capital (%)"},
    {"id": "P_315", "name": "{{CARRY_PERCENTAGE}}", "data_type": "number", "is_required": False,
     "description": "Carried interest for managing partner (%)"},
    {"id": "P_316", "name": "{{RESERVE_PERCENTAGE}}", "data_type": "number", "is_required": False,
     "description": "Minimum reserve as percentage of annual revenue"},
    {"id": "P_317", "name": "{{CAPITAL_CURE_PERIOD_DAYS}}", "data_type": "number", "is_required": False,
     "description": "Cure period for failed capital calls (days)"},
    {"id": "P_318", "name": "{{DEFAULT_INTEREST_RATE}}", "data_type": "number", "is_required": False,
     "description": "Interest rate for defaults and clawbacks (%)"},
    {"id": "P_319", "name": "{{MIN_CASH_THRESHOLD}}", "data_type": "currency", "is_required": False,
     "description": "Minimum cash position below which drawings are prohibited"},
    {"id": "P_320", "name": "{{CLAWBACK_PERIOD_DAYS}}", "data_type": "number", "is_required": False,
     "description": "Days within which excess distributions must be returned"},
]

# Which params belong to which variant
PROFIT_PARAM_MAP = {
    "PROFIT_STD_001": ["P_300", "P_301", "P_302", "P_303", "P_304", "P_305", "P_306"],
    "PROFIT_MOD_001": ["P_300", "P_301", "P_302", "P_303", "P_304", "P_307", "P_308", "P_309",
                        "P_310", "P_311", "P_312", "P_313"],
    "PROFIT_STR_001": ["P_300", "P_301", "P_302", "P_303", "P_304", "P_307", "P_308", "P_309",
                        "P_310", "P_312", "P_314", "P_315", "P_316", "P_317", "P_318", "P_319", "P_320"],
}

# ==========================================
# DATA PROCESSING OBLIGATIONS
# ==========================================

DPA_CLAUSE_TYPE = {
    "id": "data-processing-obligations",
    "name": "Data Processing Obligations",
    "category": "Data & Privacy",
    "importance_level": "Critical",
}

DPA_CLAUSES = [
    {
        "id": "DPA_STD_001",
        "clause_type": "data-processing-obligations",
        "name": "Data Processing Obligations — Standard",
        "variant": "Standard",
        "jurisdiction": "India",
        "risk_level": "Low",
        "raw_text": (
            "DATA PROCESSING OBLIGATIONS\n\n"
            "1. SCOPE OF PROCESSING\n"
            "The Processor shall process Personal Data only on documented instructions from the Controller, "
            "solely for the purpose of performing its obligations under this Agreement.\n\n"
            "2. CATEGORIES OF DATA\n"
            "The categories of data subjects and types of personal data processed under this Agreement are "
            "as set forth in {{DATA_SCHEDULE_REFERENCE}}.\n\n"
            "3. SECURITY MEASURES\n"
            "The Processor shall implement and maintain appropriate technical and organisational measures to protect "
            "Personal Data against unauthorised or unlawful processing, accidental loss, destruction, or damage, "
            "including at minimum:\n"
            "  (a) Encryption of Personal Data in transit and at rest;\n"
            "  (b) Access controls limiting processing to authorised personnel;\n"
            "  (c) Regular testing and evaluation of security measures.\n\n"
            "4. DATA BREACH NOTIFICATION\n"
            "The Processor shall notify the Controller of any Personal Data breach without undue delay and in any "
            "event within {{BREACH_NOTIFICATION_HOURS}} hours of becoming aware of the breach.\n\n"
            "5. SUB-PROCESSORS\n"
            "The Processor shall not engage any sub-processor without prior written consent of the Controller. "
            "The Processor shall ensure that sub-processors are bound by equivalent data protection obligations.\n\n"
            "6. DATA SUBJECT RIGHTS\n"
            "The Processor shall assist the Controller in responding to data subject rights requests under applicable "
            "data protection law.\n\n"
            "7. DATA RETURN AND DELETION\n"
            "Upon termination of this Agreement, the Processor shall, at the Controller's election, return or securely "
            "delete all Personal Data within {{DATA_DELETION_DAYS}} days."
        ),
    },
    {
        "id": "DPA_MOD_001",
        "clause_type": "data-processing-obligations",
        "name": "Data Processing Obligations — Moderate",
        "variant": "Moderate",
        "jurisdiction": "India",
        "risk_level": "Medium",
        "raw_text": (
            "DATA PROCESSING OBLIGATIONS\n\n"
            "1. PROCESSING SCOPE AND LAWFUL BASIS\n"
            "1.1. The Processor shall process Personal Data only on documented instructions from the Controller.\n"
            "1.2. Processing shall be limited to the purposes specified in {{DATA_SCHEDULE_REFERENCE}} and shall comply "
            "with the Digital Personal Data Protection Act, 2023 (DPDPA) and, where applicable, GDPR (Regulation (EU) 2016/679).\n"
            "1.3. The Processor shall immediately inform the Controller if, in its opinion, an instruction infringes applicable law.\n\n"
            "2. DATA PROTECTION IMPACT ASSESSMENT\n"
            "The Processor shall cooperate with and provide information necessary for the Controller to conduct Data Protection "
            "Impact Assessments (DPIAs) where required under DPDPA Section 10 or GDPR Article 35.\n\n"
            "3. SECURITY MEASURES (ARTICLE 32 EQUIVALENT)\n"
            "The Processor shall implement measures including:\n"
            "  (a) ISO 27001 certification or equivalent security framework;\n"
            "  (b) Encryption (AES-256 at rest, TLS 1.2+ in transit);\n"
            "  (c) Multi-factor authentication for systems processing Personal Data;\n"
            "  (d) Regular penetration testing (at least {{PENTEST_FREQUENCY}});\n"
            "  (e) Security incident response plan reviewed {{INCIDENT_REVIEW_FREQUENCY}}.\n\n"
            "4. DATA BREACH NOTIFICATION AND RESPONSE\n"
            "4.1. The Processor shall notify the Controller within {{BREACH_NOTIFICATION_HOURS}} hours of becoming aware.\n"
            "4.2. Notification shall include: nature of breach, categories and approximate number of affected data subjects, "
            "likely consequences, and measures taken.\n"
            "4.3. Processor shall cooperate with Controller for regulatory notifications under DPDPA Section 8.\n\n"
            "5. SUB-PROCESSOR MANAGEMENT\n"
            "5.1. Current sub-processors are listed in {{SUB_PROCESSOR_SCHEDULE}}.\n"
            "5.2. Controller may object to new sub-processors within {{SUB_PROCESSOR_OBJECTION_DAYS}} days.\n"
            "5.3. Sub-processors must be bound by equivalent data protection obligations via written agreement.\n\n"
            "6. CROSS-BORDER TRANSFERS\n"
            "Transfer of Personal Data outside India requires Controller's prior written consent and appropriate safeguards "
            "(Standard Contractual Clauses, adequacy decisions, or binding corporate rules).\n\n"
            "7. AUDIT RIGHTS\n"
            "The Controller may audit the Processor's compliance with these obligations upon {{AUDIT_NOTICE_DAYS}} days' notice, "
            "not more than {{MAX_AUDITS_PER_YEAR}} times per year.\n\n"
            "8. DATA RETURN, DELETION, AND CERTIFICATION\n"
            "8.1. Upon termination, all Personal Data shall be returned or deleted within {{DATA_DELETION_DAYS}} days.\n"
            "8.2. Processor shall provide written certification of deletion signed by an authorized officer."
        ),
    },
    {
        "id": "DPA_STR_001",
        "clause_type": "data-processing-obligations",
        "name": "Data Processing Obligations — Strict",
        "variant": "Strict",
        "jurisdiction": "India",
        "risk_level": "High",
        "raw_text": (
            "DATA PROCESSING OBLIGATIONS\n\n"
            "1. PROCESSING SCOPE, LAWFUL BASIS, AND DATA MINIMISATION\n"
            "1.1. The Processor shall process Personal Data only on documented instructions from the Controller, "
            "strictly limited to the purposes in {{DATA_SCHEDULE_REFERENCE}}.\n"
            "1.2. The Processor shall implement data minimisation principles: no Personal Data shall be collected, "
            "stored, or processed beyond what is strictly necessary.\n"
            "1.3. Compliance with DPDPA 2023, GDPR, and any other applicable data protection regime is mandatory.\n"
            "1.4. The Processor shall appoint a Data Protection Officer and notify the Controller of their identity.\n\n"
            "2. PRIVACY BY DESIGN AND DEFAULT\n"
            "2.1. The Processor shall implement privacy by design and by default in all processing systems.\n"
            "2.2. Records of processing activities shall be maintained per GDPR Article 30 / DPDPA requirements.\n"
            "2.3. Annual privacy impact assessments shall be conducted and shared with the Controller.\n\n"
            "3. SECURITY MEASURES (ENHANCED)\n"
            "The Processor shall implement:\n"
            "  (a) ISO 27001 and SOC 2 Type II certifications;\n"
            "  (b) AES-256 encryption at rest, TLS 1.3 in transit;\n"
            "  (c) Hardware Security Modules (HSMs) for cryptographic key management;\n"
            "  (d) Zero-trust network architecture;\n"
            "  (e) Quarterly penetration testing by independent third party;\n"
            "  (f) 24/7 Security Operations Centre (SOC) monitoring;\n"
            "  (g) Annual third-party security audit with results shared with Controller.\n\n"
            "4. DATA BREACH: NOTIFICATION, RESPONSE, AND REMEDIATION\n"
            "4.1. Processor shall notify Controller within {{BREACH_NOTIFICATION_HOURS}} hours.\n"
            "4.2. Full incident report within {{INCIDENT_REPORT_DAYS}} days including root cause analysis.\n"
            "4.3. Processor shall bear all costs of breach notification, credit monitoring, and remediation "
            "where the breach results from Processor's failure to comply with this clause.\n"
            "4.4. Liquidated damages of {{BREACH_LIABILITY_AMOUNT}} per breach event attributable to Processor negligence.\n\n"
            "5. SUB-PROCESSOR GOVERNANCE\n"
            "5.1. New sub-processors require Controller's prior written approval (not mere notification).\n"
            "5.2. Processor remains fully liable for all sub-processor acts and omissions.\n"
            "5.3. Sub-processor agreements must mirror these data protection obligations verbatim.\n"
            "5.4. Controller may require removal of any sub-processor within {{SUB_PROCESSOR_REMOVAL_DAYS}} days.\n\n"
            "6. CROSS-BORDER TRANSFERS\n"
            "6.1. No cross-border transfer without Controller's prior written approval and adequate safeguards.\n"
            "6.2. Processor shall conduct Transfer Impact Assessments for each destination jurisdiction.\n"
            "6.3. Government access requests for Personal Data shall be notified to Controller immediately "
            "(unless prohibited by law).\n\n"
            "7. AUDIT AND INSPECTION RIGHTS\n"
            "7.1. Controller or its appointed auditor may inspect Processor's premises, systems, and records "
            "with {{AUDIT_NOTICE_DAYS}} days' notice.\n"
            "7.2. Emergency audits may be conducted without notice following a data breach or credible security concern.\n"
            "7.3. Processor shall provide all requested evidence within {{AUDIT_RESPONSE_DAYS}} days.\n\n"
            "8. DATA LIFECYCLE MANAGEMENT\n"
            "8.1. Processor shall implement automated data retention policies.\n"
            "8.2. Upon termination: all Personal Data returned or deleted within {{DATA_DELETION_DAYS}} days.\n"
            "8.3. Deletion shall be certified by an independent third party using NIST 800-88 guidelines.\n"
            "8.4. Backup copies shall be purged within {{BACKUP_PURGE_DAYS}} days of termination.\n\n"
            "9. LIABILITY AND INDEMNIFICATION\n"
            "The Processor shall indemnify the Controller for all losses, damages, regulatory fines, and enforcement "
            "costs arising from the Processor's breach of these data processing obligations."
        ),
    },
]

DPA_PARAMS = [
    {"id": "P_400", "name": "{{DATA_SCHEDULE_REFERENCE}}", "data_type": "text", "is_required": True,
     "description": "Reference to schedule listing data categories and processing purposes"},
    {"id": "P_401", "name": "{{BREACH_NOTIFICATION_HOURS}}", "data_type": "number", "is_required": True,
     "description": "Hours within which data breach must be notified (DPDPA: 72h, GDPR: 72h)"},
    {"id": "P_402", "name": "{{DATA_DELETION_DAYS}}", "data_type": "number", "is_required": True,
     "description": "Days to delete/return personal data after termination"},
    {"id": "P_403", "name": "{{PENTEST_FREQUENCY}}", "data_type": "text", "is_required": False,
     "description": "Frequency of penetration testing (e.g., 'annually', 'quarterly')"},
    {"id": "P_404", "name": "{{INCIDENT_REVIEW_FREQUENCY}}", "data_type": "text", "is_required": False,
     "description": "Frequency of security incident response plan review"},
    {"id": "P_405", "name": "{{SUB_PROCESSOR_SCHEDULE}}", "data_type": "text", "is_required": False,
     "description": "Reference to schedule listing approved sub-processors"},
    {"id": "P_406", "name": "{{SUB_PROCESSOR_OBJECTION_DAYS}}", "data_type": "number", "is_required": False,
     "description": "Days for controller to object to new sub-processor"},
    {"id": "P_407", "name": "{{AUDIT_NOTICE_DAYS}}", "data_type": "number", "is_required": False,
     "description": "Notice days required for audit/inspection"},
    {"id": "P_408", "name": "{{MAX_AUDITS_PER_YEAR}}", "data_type": "number", "is_required": False,
     "description": "Maximum number of audits per year"},
    {"id": "P_409", "name": "{{INCIDENT_REPORT_DAYS}}", "data_type": "number", "is_required": False,
     "description": "Days for full incident report after breach"},
    {"id": "P_410", "name": "{{BREACH_LIABILITY_AMOUNT}}", "data_type": "currency", "is_required": False,
     "description": "Liquidated damages per data breach event"},
    {"id": "P_411", "name": "{{SUB_PROCESSOR_REMOVAL_DAYS}}", "data_type": "number", "is_required": False,
     "description": "Days to remove sub-processor at controller's request"},
    {"id": "P_412", "name": "{{AUDIT_RESPONSE_DAYS}}", "data_type": "number", "is_required": False,
     "description": "Days for processor to provide requested audit evidence"},
    {"id": "P_413", "name": "{{BACKUP_PURGE_DAYS}}", "data_type": "number", "is_required": False,
     "description": "Days to purge backup copies after termination"},
]

DPA_PARAM_MAP = {
    "DPA_STD_001": ["P_400", "P_401", "P_402"],
    "DPA_MOD_001": ["P_400", "P_401", "P_402", "P_403", "P_404", "P_405", "P_406", "P_407", "P_408"],
    "DPA_STR_001": ["P_400", "P_401", "P_402", "P_403", "P_407", "P_409", "P_410", "P_411", "P_412", "P_413"],
}


def create_clause_type_and_variants(session, clause_type_def, clauses, params, param_map, label=""):
    """Idempotent creation of a ClauseType, its Clause variants, Parameters, and edges."""
    ct_id = clause_type_def["id"]

    # Check and create ClauseType
    r = session.run("MATCH (ct:ClauseType {id: $id}) RETURN count(*) AS cnt", {"id": ct_id})
    if r.single()["cnt"] == 0:
        session.run("""
            CREATE (ct:ClauseType {
                id: $id, name: $name, category: $category, importance_level: $importance
            })
        """, {
            "id": ct_id, "name": clause_type_def["name"],
            "category": clause_type_def["category"],
            "importance": clause_type_def["importance_level"],
        })
        print(f"  ✓ Created ClauseType: {ct_id}")
    else:
        print(f"  ⏭ ClauseType {ct_id} already exists")

    # Create Clause variants
    for clause in clauses:
        r = session.run("MATCH (c:Clause {id: $id}) RETURN count(*) AS cnt", {"id": clause["id"]})
        if r.single()["cnt"] == 0:
            session.run("""
                CREATE (c:Clause {
                    id: $id, clause_type: $clause_type, name: $name,
                    variant: $variant, jurisdiction: $jurisdiction,
                    risk_level: $risk_level, raw_text: $raw_text
                })
            """, clause)

            # HAS_VARIANT edge
            session.run("""
                MATCH (ct:ClauseType {id: $ct_id}), (c:Clause {id: $c_id})
                CREATE (ct)-[:HAS_VARIANT]->(c)
            """, {"ct_id": ct_id, "c_id": clause["id"]})

            # GOVERNED_BY edge (India jurisdiction)
            session.run("""
                MATCH (c:Clause {id: $c_id}), (j:Jurisdiction {id: 'india'})
                CREATE (c)-[:GOVERNED_BY]->(j)
            """, {"c_id": clause["id"]})

            print(f"  ✓ Created Clause: {clause['id']} ({clause['variant']})")
        else:
            print(f"  ⏭ Clause {clause['id']} already exists")

    # Create Parameters
    for param in params:
        r = session.run("MATCH (p:Parameter {id: $id}) RETURN count(*) AS cnt", {"id": param["id"]})
        if r.single()["cnt"] == 0:
            session.run("""
                CREATE (p:Parameter {
                    id: $id, name: $name, data_type: $data_type,
                    is_required: $is_required, description: $description
                })
            """, param)
            print(f"  ✓ Created Parameter: {param['id']} ({param['name']})")

    # Create CONTAINS_PARAM edges
    for clause_id, param_ids in param_map.items():
        for pid in param_ids:
            r = session.run("""
                MATCH (c:Clause {id: $cid})-[:CONTAINS_PARAM]->(p:Parameter {id: $pid})
                RETURN count(*) AS cnt
            """, {"cid": clause_id, "pid": pid})
            if r.single()["cnt"] == 0:
                session.run("""
                    MATCH (c:Clause {id: $cid}), (p:Parameter {id: $pid})
                    CREATE (c)-[:CONTAINS_PARAM]->(p)
                """, {"cid": clause_id, "pid": pid})

    # Add CONFLICTS_WITH edges between variants (bidirectional for all 3 pairs)
    variant_pairs = [
        ("Standard", "Moderate", "medium"),
        ("Standard", "Strict", "high"),
        ("Moderate", "Strict", "high"),
    ]
    for v1, v2, severity in variant_pairs:
        c1 = [c for c in clauses if c["variant"] == v1][0]
        c2 = [c for c in clauses if c["variant"] == v2][0]
        for a_id, b_id in [(c1["id"], c2["id"]), (c2["id"], c1["id"])]:
            r = session.run("""
                MATCH (a:Clause {id: $aid})-[:CONFLICTS_WITH]->(b:Clause {id: $bid})
                RETURN count(*) AS cnt
            """, {"aid": a_id, "bid": b_id})
            if r.single()["cnt"] == 0:
                session.run("""
                    MATCH (a:Clause {id: $aid}), (b:Clause {id: $bid})
                    CREATE (a)-[:CONFLICTS_WITH {
                        severity: $severity, conflict_type: 'duplication',
                        reason: 'Cannot have both ' + a.variant + ' and ' + b.variant + ' variants of ' + $ct_name + ' in one contract',
                        resolution_advice: 'Choose one variant of ' + $ct_name
                    }]->(b)
                """, {"aid": a_id, "bid": b_id, "severity": severity, "ct_name": clause_type_def["name"]})

    # Add ALTERNATIVE_TO edges (all 6 direction pairs)
    alt_config = {
        ("Standard", "Moderate"): ("enhanced_protection", "medium"),
        ("Standard", "Strict"): ("maximum_protection", "low"),
        ("Moderate", "Standard"): ("simplified", "medium"),
        ("Moderate", "Strict"): ("enhanced_enforcement", "low"),
        ("Strict", "Moderate"): ("balanced_approach", "high"),
        ("Strict", "Standard"): ("simplified", "high"),
    }
    for (v1, v2), (alt_type, strength) in alt_config.items():
        c1 = [c for c in clauses if c["variant"] == v1][0]
        c2 = [c for c in clauses if c["variant"] == v2][0]
        r = session.run("""
            MATCH (a:Clause {id: $aid})-[:ALTERNATIVE_TO]->(b:Clause {id: $bid})
            RETURN count(*) AS cnt
        """, {"aid": c1["id"], "bid": c2["id"]})
        if r.single()["cnt"] == 0:
            session.run("""
                MATCH (a:Clause {id: $aid}), (b:Clause {id: $bid})
                CREATE (a)-[:ALTERNATIVE_TO {
                    alternative_type: $alt_type,
                    recommendation_strength: $strength,
                    reason: $reason,
                    benefit: $benefit
                }]->(b)
            """, {
                "aid": c1["id"], "bid": c2["id"],
                "alt_type": alt_type, "strength": strength,
                "reason": f"{v2} variant of {clause_type_def['name']} provides an alternative approach",
                "benefit": f"Alternative {v2.lower()} level of {clause_type_def['name'].lower()} protection",
            })


def phase4(session):
    print("\n=== PHASE 4: New Clause Types ===\n")

    # --- 4a: Profit Sharing Terms ---
    print("[4a] Creating profit-sharing-terms...\n")
    create_clause_type_and_variants(
        session, PROFIT_SHARING_CLAUSE_TYPE, PROFIT_SHARING_CLAUSES,
        PROFIT_SHARING_PARAMS, PROFIT_PARAM_MAP
    )

    # Wire profit-sharing-terms into partnership-agreement
    # First check and remove payment-terms from partnership-agreement (it's being replaced)
    r = session.run("""
        MATCH (ct:ContractType {id: 'partnership-agreement'})-[:CONTAINS_CLAUSE]->(ctype:ClauseType {id: 'profit-sharing-terms'})
        RETURN count(*) AS cnt
    """)
    if r.single()["cnt"] == 0:
        # Find where payment-terms is in partnership-agreement to put profit-sharing in same position
        r = session.run("""
            MATCH (ct:ContractType {id: 'partnership-agreement'})-[r:CONTAINS_CLAUSE]->(ctype:ClauseType {id: 'payment-terms'})
            RETURN r.sequence AS seq
        """)
        rec = r.single()
        if rec:
            pay_seq = rec["seq"]
            # Add profit-sharing at same sequence
            session.run("""
                MATCH (ct:ContractType {id: 'partnership-agreement'}),
                      (ctype:ClauseType {id: 'profit-sharing-terms'})
                CREATE (ct)-[:CONTAINS_CLAUSE {
                    sequence: $seq, mandatory: true,
                    description: 'Profit/loss allocation, distribution schedule, capital contributions, drawing rights'
                }]->(ctype)
            """, {"seq": pay_seq + 1})
            # Shift sequences after the new position
            session.run("""
                MATCH (ct:ContractType {id: 'partnership-agreement'})-[r:CONTAINS_CLAUSE]->(ctype:ClauseType)
                WHERE r.sequence > $seq AND ctype.id <> 'profit-sharing-terms'
                SET r.sequence = r.sequence + 1
            """, {"seq": pay_seq + 1})
            print(f"  ✓ Wired profit-sharing-terms into partnership-agreement at seq={pay_seq + 1}")
        else:
            # Payment-terms not found, just append
            session.run("""
                MATCH (ct:ContractType {id: 'partnership-agreement'}),
                      (ctype:ClauseType {id: 'profit-sharing-terms'})
                CREATE (ct)-[:CONTAINS_CLAUSE {
                    sequence: 17, mandatory: true,
                    description: 'Profit/loss allocation, distribution schedule, capital contributions, drawing rights'
                }]->(ctype)
            """)
            print("  ✓ Wired profit-sharing-terms into partnership-agreement at seq=17")
    else:
        print("  ⏭ profit-sharing-terms already in partnership-agreement")

    # Add REQUIRES: profit-sharing-terms → definitions
    r = session.run("""
        MATCH (a:ClauseType {id: 'profit-sharing-terms'})-[:REQUIRES]->(b:ClauseType {id: 'definitions'})
        RETURN count(*) AS cnt
    """)
    if r.single()["cnt"] == 0:
        session.run("""
            MATCH (a:ClauseType {id: 'profit-sharing-terms'}), (b:ClauseType {id: 'definitions'})
            CREATE (a)-[:REQUIRES {
                dependency_type: 'definitional', is_critical: true,
                reason: 'Profit sharing requires clear definitions of Net Profit, Capital Contributions, Working Capital Reserve, and Distribution'
            }]->(b)
        """)
        print("  ✓ Added REQUIRES: profit-sharing-terms → definitions")

    # --- 4b: Data Processing Obligations ---
    print("\n[4b] Creating data-processing-obligations...\n")
    create_clause_type_and_variants(
        session, DPA_CLAUSE_TYPE, DPA_CLAUSES,
        DPA_PARAMS, DPA_PARAM_MAP
    )

    # Wire data-processing-obligations into data-processing-agreement
    r = session.run("""
        MATCH (ct:ContractType {id: 'data-processing-agreement'})-[:CONTAINS_CLAUSE]->(ctype:ClauseType {id: 'data-processing-obligations'})
        RETURN count(*) AS cnt
    """)
    if r.single()["cnt"] == 0:
        # Insert right after scope-of-agreement (seq=3)
        session.run("""
            MATCH (ct:ContractType {id: 'data-processing-agreement'})-[r:CONTAINS_CLAUSE]->(ctype:ClauseType)
            WHERE r.sequence >= 4
            SET r.sequence = r.sequence + 1
        """)
        session.run("""
            MATCH (ct:ContractType {id: 'data-processing-agreement'}),
                  (ctype:ClauseType {id: 'data-processing-obligations'})
            CREATE (ct)-[:CONTAINS_CLAUSE {
                sequence: 4, mandatory: true,
                description: 'GDPR/DPDPA compliant data processing obligations, security measures, breach notification, sub-processor management'
            }]->(ctype)
        """)
        print("  ✓ Wired data-processing-obligations into data-processing-agreement at seq=4")
    else:
        print("  ⏭ data-processing-obligations already in data-processing-agreement")

    # Add REQUIRES: data-processing-obligations → confidentiality
    r = session.run("""
        MATCH (a:ClauseType {id: 'data-processing-obligations'})-[:REQUIRES]->(b:ClauseType {id: 'confidentiality'})
        RETURN count(*) AS cnt
    """)
    if r.single()["cnt"] == 0:
        session.run("""
            MATCH (a:ClauseType {id: 'data-processing-obligations'}), (b:ClauseType {id: 'confidentiality'})
            CREATE (a)-[:REQUIRES {
                dependency_type: 'procedural', is_critical: true,
                reason: 'Data processing obligations require a confidentiality clause to protect personal data handled under the agreement'
            }]->(b)
        """)
        print("  ✓ Added REQUIRES: data-processing-obligations → confidentiality")

    # Add REQUIRES: data-processing-obligations → definitions
    r = session.run("""
        MATCH (a:ClauseType {id: 'data-processing-obligations'})-[:REQUIRES]->(b:ClauseType {id: 'definitions'})
        RETURN count(*) AS cnt
    """)
    if r.single()["cnt"] == 0:
        session.run("""
            MATCH (a:ClauseType {id: 'data-processing-obligations'}), (b:ClauseType {id: 'definitions'})
            CREATE (a)-[:REQUIRES {
                dependency_type: 'definitional', is_critical: true,
                reason: 'Data processing obligations require definitions of Personal Data, Processing, Controller, Processor, Data Subject, and Personal Data Breach'
            }]->(b)
        """)
        print("  ✓ Added REQUIRES: data-processing-obligations → definitions")

    # Add REQUIRES: data-processing-obligations → effect-of-termination-and-survival
    r = session.run("""
        MATCH (a:ClauseType {id: 'data-processing-obligations'})-[:REQUIRES]->(b:ClauseType {id: 'effect-of-termination-and-survival'})
        RETURN count(*) AS cnt
    """)
    if r.single()["cnt"] == 0:
        session.run("""
            MATCH (a:ClauseType {id: 'data-processing-obligations'}), (b:ClauseType {id: 'effect-of-termination-and-survival'})
            CREATE (a)-[:REQUIRES {
                dependency_type: 'procedural', is_critical: true,
                reason: 'Data processing obligations must specify post-termination data return/deletion requirements and survival of confidentiality'
            }]->(b)
        """)
        print("  ✓ Added REQUIRES: data-processing-obligations → effect-of-termination-and-survival")

    print("\n✅ Phase 4 complete!")


if __name__ == "__main__":
    with driver.session() as session:
        phase4(session)
    driver.close()
