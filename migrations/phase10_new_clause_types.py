"""
Phase 10: New Clause Types
Creates 5 new ClauseTypes with 3 variants each across 3 jurisdictions = 45 clause nodes.
- insurance-requirements
- assignment-and-subcontracting
- notices-and-communications
- audit-and-inspection-rights
- anti-bribery-compliance
"""

from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

NEW_CLAUSE_TYPES = [
    {"id": "insurance-requirements", "name": "Insurance Requirements", "category": "Risk", "importance_level": "high",
     "description": "Specifies minimum insurance coverage requirements including general liability, professional indemnity, cyber liability, and workers' compensation."},
    {"id": "assignment-and-subcontracting", "name": "Assignment and Subcontracting", "category": "Control", "importance_level": "medium",
     "description": "Governs whether rights or obligations under the agreement can be assigned or subcontracted to third parties."},
    {"id": "notices-and-communications", "name": "Notices and Communications", "category": "Procedural", "importance_level": "low",
     "description": "Formal notice mechanics including delivery methods, deemed receipt, and address for service."},
    {"id": "audit-and-inspection-rights", "name": "Audit and Inspection Rights", "category": "Governance", "importance_level": "high",
     "description": "Financial and compliance audit rights, inspection access, and record-keeping obligations."},
    {"id": "anti-bribery-compliance", "name": "Anti-Bribery and Compliance", "category": "Compliance", "importance_level": "high",
     "description": "Anti-corruption covenants referencing applicable legislation (PCA, FCPA, UK Bribery Act) with compliance program requirements."},
]

CLAUSES = [
    # ===== INSURANCE REQUIREMENTS =====
    # India
    {"id": "INS_STD_001", "clause_type": "insurance-requirements", "variant": "Standard", "jurisdiction": "India", "risk_level": "Low",
     "raw_text": "INSURANCE\n\n{{PARTY_A_NAME}} shall maintain adequate insurance coverage including: (a) Commercial General Liability; (b) Professional Indemnity. Certificates of insurance shall be provided upon request."},
    {"id": "INS_MOD_001", "clause_type": "insurance-requirements", "variant": "Moderate", "jurisdiction": "India", "risk_level": "Medium",
     "raw_text": "INSURANCE\n\n1. REQUIRED COVERAGE\n{{PARTY_A_NAME}} shall maintain: (a) Commercial General Liability: INR {{CGL_COVERAGE}} per occurrence; (b) Professional Indemnity/E&O: INR {{PI_COVERAGE}}; (c) Workers' Compensation: per Employees' Compensation Act, 1923; (d) Cyber Liability: INR {{CYBER_COVERAGE}} (if processing personal data).\n\n2. POLICY REQUIREMENTS\n(a) {{PARTY_B_NAME}} named as additional insured on CGL; (b) {{NOTICE_OF_CANCELLATION_DAYS}} days' notice of cancellation; (c) Policies from IRDAI-registered insurers.\n\n3. CERTIFICATES\nProvide certificates within {{INSURANCE_CERT_DAYS}} days of request and annually thereafter."},
    {"id": "INS_STR_001", "clause_type": "insurance-requirements", "variant": "Strict", "jurisdiction": "India", "risk_level": "High",
     "raw_text": "INSURANCE\n\n1. MANDATORY COVERAGE\n(a) CGL: INR {{CGL_COVERAGE}} per occurrence / INR {{CGL_AGGREGATE}} aggregate;\n(b) PI/E&O: INR {{PI_COVERAGE}};\n(c) Cyber/Data Breach: INR {{CYBER_COVERAGE}};\n(d) Workers' Compensation: Employees' Compensation Act 1923;\n(e) Product Liability: INR {{PRODUCT_LIABILITY_COVERAGE}} (if applicable);\n(f) Directors & Officers: INR {{DO_COVERAGE}} (if applicable).\n\n2. POLICY TERMS\n(a) Additional insured endorsement; (b) Primary and non-contributory; (c) Waiver of subrogation; (d) {{NOTICE_OF_CANCELLATION_DAYS}} days' cancellation notice; (e) IRDAI-registered insurers with claim-paying ability rating of at least AA.\n\n3. FAILURE TO MAINTAIN\nFailure to maintain insurance is a material breach permitting immediate termination.\n\n4. AUDIT\n{{PARTY_B_NAME}} may audit insurance compliance annually."},

    # US
    {"id": "INS_STD_US001", "clause_type": "insurance-requirements", "variant": "Standard", "jurisdiction": "US", "risk_level": "Low",
     "raw_text": "INSURANCE\n\n{{PARTY_A_NAME}} shall maintain adequate insurance coverage including Commercial General Liability and Professional Liability (E&O). Certificates of insurance provided upon request."},
    {"id": "INS_MOD_US001", "clause_type": "insurance-requirements", "variant": "Moderate", "jurisdiction": "US", "risk_level": "Medium",
     "raw_text": "INSURANCE\n\n1. REQUIRED COVERAGE\n(a) CGL: ${{CGL_COVERAGE}} per occurrence / ${{CGL_AGGREGATE}} aggregate; (b) Professional Liability/E&O: ${{PI_COVERAGE}}; (c) Workers' Compensation: per applicable state law; (d) Cyber Liability: ${{CYBER_COVERAGE}}; (e) Commercial Auto: ${{AUTO_COVERAGE}} (if applicable).\n\n2. ENDORSEMENTS\n(a) {{PARTY_B_NAME}} as additional insured; (b) {{NOTICE_OF_CANCELLATION_DAYS}} days' notice of cancellation; (c) Carriers rated A- VII or better by A.M. Best.\n\n3. CERTIFICATES\nACORD certificates within {{INSURANCE_CERT_DAYS}} days and annually."},
    {"id": "INS_STR_US001", "clause_type": "insurance-requirements", "variant": "Strict", "jurisdiction": "US", "risk_level": "High",
     "raw_text": "INSURANCE\n\n1. MANDATORY COVERAGE\n(a) CGL: ${{CGL_COVERAGE}} occ / ${{CGL_AGGREGATE}} agg; (b) Umbrella: ${{UMBRELLA_COVERAGE}}; (c) E&O: ${{PI_COVERAGE}}; (d) Cyber: ${{CYBER_COVERAGE}}; (e) Workers' Comp: statutory; (f) Employer's Liability: ${{EL_COVERAGE}}; (g) D&O: ${{DO_COVERAGE}}.\n\n2. ENDORSEMENTS\n(a) Additional insured (CGL + Umbrella); (b) Primary and non-contributory; (c) Waiver of subrogation; (d) Per-project aggregate; (e) A.M. Best A- VII+ carriers; (f) {{NOTICE_OF_CANCELLATION_DAYS}} days' notice.\n\n3. ANNUAL COMPLIANCE\nACORD 25/28 certificates annually. Failure = material breach.\n\n4. INSURANCE AUDIT\nAnnual review of coverage adequacy."},

    # UK
    {"id": "INS_STD_UK001", "clause_type": "insurance-requirements", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "INSURANCE\n\n{{PARTY_A_NAME}} shall maintain adequate insurance including public liability and professional indemnity with FCA/PRA-authorised insurers."},
    {"id": "INS_MOD_UK001", "clause_type": "insurance-requirements", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "INSURANCE\n\n1. REQUIRED COVERAGE\n(a) Public Liability: £{{PL_COVERAGE}}; (b) Professional Indemnity: £{{PI_COVERAGE}}; (c) Employer's Liability: £5,000,000 minimum (per Employers' Liability (Compulsory Insurance) Act 1969); (d) Cyber: £{{CYBER_COVERAGE}}.\n\n2. POLICY REQUIREMENTS\n(a) FCA/PRA-authorised insurers; (b) {{PARTY_B_NAME}} noted as interested party; (c) {{NOTICE_OF_CANCELLATION_DAYS}} days' cancellation notice.\n\n3. CERTIFICATES\nProvide certificates annually and on request."},
    {"id": "INS_STR_UK001", "clause_type": "insurance-requirements", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "INSURANCE\n\n1. MANDATORY\n(a) Public Liability: £{{PL_COVERAGE}}; (b) PI: £{{PI_COVERAGE}}; (c) Employer's Liability: per EL(CI)A 1969 minimum; (d) Cyber: £{{CYBER_COVERAGE}}; (e) Product Liability: £{{PRODUCT_LIABILITY_COVERAGE}}; (f) D&O: £{{DO_COVERAGE}}.\n\n2. TERMS\n(a) FCA/PRA-authorised; (b) Noted interest; (c) Non-vitiation; (d) {{NOTICE_OF_CANCELLATION_DAYS}} days' notice.\n\n3. FAILURE\nMaterial breach; immediate termination right.\n\n4. AUDIT\nAnnual insurance compliance verification."},

    # ===== ASSIGNMENT AND SUBCONTRACTING =====
    {"id": "ASSIGN_STD_001", "clause_type": "assignment-and-subcontracting", "variant": "Standard", "jurisdiction": "India", "risk_level": "Low",
     "raw_text": "ASSIGNMENT\n\nNeither Party may assign this Agreement without the prior written consent of the other Party, such consent not to be unreasonably withheld. Any purported assignment without consent is void."},
    {"id": "ASSIGN_MOD_001", "clause_type": "assignment-and-subcontracting", "variant": "Moderate", "jurisdiction": "India", "risk_level": "Medium",
     "raw_text": "ASSIGNMENT AND SUBCONTRACTING\n\n1. ASSIGNMENT\nNeither Party may assign without prior written consent, except: (a) to an Affiliate; (b) in connection with a merger, acquisition, or sale of all or substantially all assets (Indian Contract Act, 1872 Section 37).\n\n2. SUBCONTRACTING\n{{PARTY_A_NAME}} may subcontract portions of the Services with prior written notice, provided: (a) {{PARTY_A_NAME}} remains fully liable; (b) subcontractors comply with confidentiality, data protection, and applicable law.\n\n3. CHANGE OF CONTROL\nA Change of Control entitles the other Party to terminate upon {{CHANGE_OF_CONTROL_NOTICE_DAYS}} days' notice."},
    {"id": "ASSIGN_STR_001", "clause_type": "assignment-and-subcontracting", "variant": "Strict", "jurisdiction": "India", "risk_level": "High",
     "raw_text": "ASSIGNMENT AND SUBCONTRACTING\n\n1. NO ASSIGNMENT\nNeither Party may assign, novate, or transfer without prior written consent. Assignment to Affiliates requires {{AFFILIATE_ASSIGNMENT_NOTICE}} days' notice.\n\n2. NO SUBCONTRACTING\n{{PARTY_A_NAME}} shall not subcontract without {{PARTY_B_NAME}}'s prior written approval. Approved subcontractors must execute mirror obligations.\n\n3. CHANGE OF CONTROL\nChange of Control: (a) {{CHANGE_OF_CONTROL_NOTICE_DAYS}} days' notice; (b) other Party may terminate within {{CHANGE_OF_CONTROL_EXIT_DAYS}} days; (c) no additional payment obligation.\n\n4. BINDING ON SUCCESSORS\nThis Agreement binds and inures to the benefit of permitted successors and assigns."},

    {"id": "ASSIGN_STD_US001", "clause_type": "assignment-and-subcontracting", "variant": "Standard", "jurisdiction": "US", "risk_level": "Low",
     "raw_text": "ASSIGNMENT\n\nNeither Party may assign this Agreement without prior written consent, not to be unreasonably withheld. Any assignment without consent is void and of no effect."},
    {"id": "ASSIGN_MOD_US001", "clause_type": "assignment-and-subcontracting", "variant": "Moderate", "jurisdiction": "US", "risk_level": "Medium",
     "raw_text": "ASSIGNMENT AND SUBCONTRACTING\n\n1. ASSIGNMENT\nNo assignment without consent, except: (a) to an Affiliate; (b) in connection with a merger, acquisition, or sale of substantially all assets.\n\n2. SUBCONTRACTING\nSubcontracting permitted with notice. {{PARTY_A_NAME}} remains liable. Subcontractors bound by equivalent obligations.\n\n3. CHANGE OF CONTROL\nChange of Control triggers {{CHANGE_OF_CONTROL_NOTICE_DAYS}} days' notice and termination right."},
    {"id": "ASSIGN_STR_US001", "clause_type": "assignment-and-subcontracting", "variant": "Strict", "jurisdiction": "US", "risk_level": "High",
     "raw_text": "ASSIGNMENT AND SUBCONTRACTING\n\n1. PROHIBITION\nNo assignment, delegation, or subcontracting without prior written consent.\n\n2. AFFILIATE EXCEPTION\nAffiliate assignment on {{AFFILIATE_ASSIGNMENT_NOTICE}} days' notice, provided assignee assumes all obligations.\n\n3. CHANGE OF CONTROL\n(a) Notice within {{CHANGE_OF_CONTROL_NOTICE_DAYS}} days;\n(b) Exit right within {{CHANGE_OF_CONTROL_EXIT_DAYS}} days;\n(c) Anti-assignment-in-bankruptcy: to maximum extent permitted under 11 U.S.C. §365.\n\n4. SUCCESSORS\nBinding on permitted successors and assigns."},

    {"id": "ASSIGN_STD_UK001", "clause_type": "assignment-and-subcontracting", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "ASSIGNMENT\n\nNeither Party shall assign this Agreement without the prior written consent of the other, which shall not be unreasonably withheld or delayed."},
    {"id": "ASSIGN_MOD_UK001", "clause_type": "assignment-and-subcontracting", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "ASSIGNMENT AND SUBCONTRACTING\n\n1. ASSIGNMENT\nNo assignment without consent, except to Affiliate or on change of control (by operation of law).\n\n2. SUBCONTRACTING\nPermitted with notice. {{PARTY_A_NAME}} liable for subcontractor performance.\n\n3. CHANGE OF CONTROL\n{{CHANGE_OF_CONTROL_NOTICE_DAYS}} days' notice. Other Party may terminate if the change materially prejudices its interests."},
    {"id": "ASSIGN_STR_UK001", "clause_type": "assignment-and-subcontracting", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "ASSIGNMENT AND SUBCONTRACTING\n\n1. PROHIBITION\nNo assignment or novation without consent.\n\n2. SUBCONTRACTING\nPrior written approval. Mirror obligations. Full liability.\n\n3. CHANGE OF CONTROL\n(a) {{CHANGE_OF_CONTROL_NOTICE_DAYS}} days' notice;\n(b) Termination right within {{CHANGE_OF_CONTROL_EXIT_DAYS}} days;\n(c) Subject to CIGA 2020 restrictions on termination for insolvency-related events.\n\n4. BINDING\nBinds and enures to permitted successors and assigns."},

    # ===== NOTICES AND COMMUNICATIONS =====
    {"id": "NOTICE_STD_001", "clause_type": "notices-and-communications", "variant": "Standard", "jurisdiction": "India", "risk_level": "Low",
     "raw_text": "NOTICES\n\nAll notices under this Agreement shall be in writing and delivered to the addresses specified in this Agreement. Notices may be delivered by hand, registered post/speed post, or email. Notices are deemed received: (a) on delivery if by hand; (b) 3 business days after posting if by registered post; (c) on the next business day if by email with delivery confirmation."},
    {"id": "NOTICE_MOD_001", "clause_type": "notices-and-communications", "variant": "Moderate", "jurisdiction": "India", "risk_level": "Medium",
     "raw_text": "NOTICES\n\n1. METHOD\nNotices must be in writing and may be delivered by: (a) registered post or speed post; (b) reputed courier service; (c) email to designated addresses with read receipt.\n\n2. DEEMED RECEIPT\n(a) Hand delivery: on delivery; (b) Registered post: {{POST_DEEMED_DAYS}} days after posting; (c) Courier: {{COURIER_DEEMED_DAYS}} days; (d) Email: next business day if sent before 5:00 PM IST.\n\n3. ADDRESSES\nAs set out in Schedule {{NOTICE_SCHEDULE}} or as updated by {{ADDRESS_CHANGE_NOTICE_DAYS}} days' written notice.\n\n4. LEGAL NOTICES\nTermination and dispute notices must be sent by registered post in addition to email."},
    {"id": "NOTICE_STR_001", "clause_type": "notices-and-communications", "variant": "Strict", "jurisdiction": "India", "risk_level": "High",
     "raw_text": "NOTICES\n\n1. MANDATORY METHODS\nAll formal notices (termination, dispute, breach, indemnification) must be delivered by: (a) registered post with AD; (b) reputed courier; AND (c) email to all designated recipients.\n\n2. DEEMED RECEIPT\n(a) Hand: on signature; (b) Registered post: {{POST_DEEMED_DAYS}} days; (c) Courier: {{COURIER_DEEMED_DAYS}} days; (d) Email: next business day with delivery confirmation.\n\n3. DESIGNATED CONTACTS\nEach Party appoints: (a) Primary contact; (b) Legal/compliance contact; (c) Escalation contact. As set forth in Annexure {{NOTICE_SCHEDULE}}.\n\n4. UPDATES\n{{ADDRESS_CHANGE_NOTICE_DAYS}} days' advance notice for address changes.\n\n5. LANGUAGE\nAll formal notices in English."},

    {"id": "NOTICE_STD_US001", "clause_type": "notices-and-communications", "variant": "Standard", "jurisdiction": "US", "risk_level": "Low",
     "raw_text": "NOTICES\n\nAll notices shall be in writing and deemed given when: (a) delivered by hand; (b) one business day after deposit with a nationally recognized overnight courier; (c) three business days after deposit in U.S. mail, certified, return receipt requested; (d) on the date sent by email with confirmation of receipt."},
    {"id": "NOTICE_MOD_US001", "clause_type": "notices-and-communications", "variant": "Moderate", "jurisdiction": "US", "risk_level": "Medium",
     "raw_text": "NOTICES\n\n1. DELIVERY\nNotices effective when delivered by: (a) certified mail, return receipt requested; (b) FedEx/UPS overnight; (c) email with read confirmation. Formal legal notices require physical copy in addition to email.\n\n2. DEEMED RECEIPT\n(a) Hand: on delivery; (b) Overnight: next business day; (c) Certified mail: {{POST_DEEMED_DAYS}} days; (d) Email: verified receipt date.\n\n3. ADDRESSES\nPer signature block, updated with {{ADDRESS_CHANGE_NOTICE_DAYS}} days' notice."},
    {"id": "NOTICE_STR_US001", "clause_type": "notices-and-communications", "variant": "Strict", "jurisdiction": "US", "risk_level": "High",
     "raw_text": "NOTICES\n\n1. FORMAL NOTICES\nTermination, breach, and dispute notices require: (a) certified mail, return receipt requested; AND (b) nationally recognized overnight courier; AND (c) email confirmation.\n\n2. DEEMED RECEIPT\n(a) Personal: on delivery; (b) Overnight: next business day; (c) Certified mail: {{POST_DEEMED_DAYS}} days; (d) Email: business day of confirmed receipt.\n\n3. DESIGNATED RECIPIENTS\nPrimary contact, legal contact, and escalation contact per Exhibit {{NOTICE_SCHEDULE}}. Updated with {{ADDRESS_CHANGE_NOTICE_DAYS}} days' notice.\n\n4. ELECTRONIC SIGNATURES\nNotices may be signed electronically per the E-SIGN Act and UETA."},

    {"id": "NOTICE_STD_UK001", "clause_type": "notices-and-communications", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "NOTICES\n\nNotices must be in writing and delivered by: (a) hand; (b) first class post; or (c) email. Deemed received: (a) on delivery if by hand; (b) 2 business days after posting; (c) next business day if by email before 5:00 PM GMT."},
    {"id": "NOTICE_MOD_UK001", "clause_type": "notices-and-communications", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "NOTICES\n\n1. METHOD\n(a) First class post or recorded delivery; (b) DX or reputable courier; (c) Email to designated addresses.\n\n2. DEEMED RECEIPT\n(a) Hand: on delivery; (b) Post: {{POST_DEEMED_DAYS}} days; (c) DX: next business day; (d) Email: next business day if before 5:00 PM.\n\n3. ADDRESSES\nPer Schedule {{NOTICE_SCHEDULE}}. Updated with {{ADDRESS_CHANGE_NOTICE_DAYS}} days' notice.\n\n4. FORMAL NOTICES\nTermination and dispute notices must use post or DX in addition to email."},
    {"id": "NOTICE_STR_UK001", "clause_type": "notices-and-communications", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "NOTICES\n\n1. FORMAL NOTICES\nTermination, breach, and dispute: (a) recorded delivery Royal Mail; AND (b) reputable courier/DX; AND (c) email.\n\n2. DEEMED RECEIPT\n(a) Hand: date of delivery; (b) Recorded delivery: {{POST_DEEMED_DAYS}} days; (c) DX: next business day; (d) Email: next business day.\n\n3. DESIGNATED CONTACTS\nPrimary, legal, and escalation contacts per Schedule {{NOTICE_SCHEDULE}}.\n\n4. LANGUAGE\nEnglish."},

    # ===== AUDIT AND INSPECTION RIGHTS =====
    {"id": "AUDIT_STD_001", "clause_type": "audit-and-inspection-rights", "variant": "Standard", "jurisdiction": "India", "risk_level": "Low",
     "raw_text": "AUDIT RIGHTS\n\n{{PARTY_B_NAME}} may audit {{PARTY_A_NAME}}'s compliance with this Agreement upon {{AUDIT_NOTICE_DAYS}} days' prior written notice, during business hours, no more than {{MAX_AUDITS_PER_YEAR}} time(s) per year."},
    {"id": "AUDIT_MOD_001", "clause_type": "audit-and-inspection-rights", "variant": "Moderate", "jurisdiction": "India", "risk_level": "Medium",
     "raw_text": "AUDIT AND INSPECTION RIGHTS\n\n1. SCOPE\n{{PARTY_B_NAME}} may audit: (a) financial records related to invoicing; (b) compliance with SLAs; (c) security controls; (d) data protection compliance.\n\n2. PROCEDURE\n(a) {{AUDIT_NOTICE_DAYS}} days' written notice;\n(b) During business hours;\n(c) Maximum {{MAX_AUDITS_PER_YEAR}} audits per year;\n(d) {{PARTY_A_NAME}} shall provide reasonable cooperation.\n\n3. COSTS\nEach Party bears its own audit costs, unless the audit reveals material non-compliance (>5% discrepancy), in which case {{PARTY_A_NAME}} bears all costs.\n\n4. RECORDS\n{{PARTY_A_NAME}} shall maintain accurate records for {{RECORD_RETENTION_YEARS}} years."},
    {"id": "AUDIT_STR_001", "clause_type": "audit-and-inspection-rights", "variant": "Strict", "jurisdiction": "India", "risk_level": "High",
     "raw_text": "AUDIT AND INSPECTION RIGHTS\n\n1. COMPREHENSIVE AUDIT\n{{PARTY_B_NAME}} may audit: (a) financial records, invoices, and time records; (b) process compliance; (c) security measures; (d) data protection (DPDPA 2023 compliance); (e) subcontractor compliance; (f) insurance certificates.\n\n2. ACCESS\n(a) {{AUDIT_NOTICE_DAYS}} days' notice for scheduled audits;\n(b) Emergency/incident-triggered audits with no notice required;\n(c) Third-party auditors permitted (subject to confidentiality);\n(d) {{MAX_AUDITS_PER_YEAR}} scheduled + unlimited emergency audits.\n\n3. REMEDIATION\nNon-compliance findings remediated within {{REMEDIATION_DAYS}} days. Repeat findings constitute material breach.\n\n4. RECORDS\n{{RECORD_RETENTION_YEARS}} years retention. Statutory records as per GST and Companies Act requirements."},

    {"id": "AUDIT_STD_US001", "clause_type": "audit-and-inspection-rights", "variant": "Standard", "jurisdiction": "US", "risk_level": "Low",
     "raw_text": "AUDIT RIGHTS\n\n{{PARTY_B_NAME}} may audit compliance upon {{AUDIT_NOTICE_DAYS}} days' notice, during business hours, {{MAX_AUDITS_PER_YEAR}} time(s) annually."},
    {"id": "AUDIT_MOD_US001", "clause_type": "audit-and-inspection-rights", "variant": "Moderate", "jurisdiction": "US", "risk_level": "Medium",
     "raw_text": "AUDIT AND INSPECTION\n\n1. SCOPE\nFinancial, compliance, security, and data protection audits.\n\n2. PROCEDURE\n(a) {{AUDIT_NOTICE_DAYS}} days' notice; (b) business hours; (c) {{MAX_AUDITS_PER_YEAR}} per year; (d) reasonable cooperation.\n\n3. COSTS\nAudit costs borne by {{PARTY_B_NAME}} unless >5% discrepancy discovered.\n\n4. RECORDS\n{{RECORD_RETENTION_YEARS}} years per applicable tax and regulatory requirements."},
    {"id": "AUDIT_STR_US001", "clause_type": "audit-and-inspection-rights", "variant": "Strict", "jurisdiction": "US", "risk_level": "High",
     "raw_text": "AUDIT AND INSPECTION\n\n1. COMPREHENSIVE\nAudit scope: financials, compliance (SOX if applicable), security (SOC 2), data handling (CCPA/HIPAA), and subcontractors.\n\n2. ACCESS\n(a) {{AUDIT_NOTICE_DAYS}} days' scheduled; (b) no-notice for emergency/breach; (c) third-party auditors permitted; (d) {{MAX_AUDITS_PER_YEAR}} scheduled + unlimited emergency.\n\n3. REMEDIATION\nFindings cured within {{REMEDIATION_DAYS}} days. Repeated findings = material breach.\n\n4. RECORDS\n{{RECORD_RETENTION_YEARS}} years (IRS, SEC, state requirements)."},

    {"id": "AUDIT_STD_UK001", "clause_type": "audit-and-inspection-rights", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "AUDIT RIGHTS\n\n{{PARTY_B_NAME}} may audit compliance upon {{AUDIT_NOTICE_DAYS}} days' notice, during business hours, {{MAX_AUDITS_PER_YEAR}} per year."},
    {"id": "AUDIT_MOD_UK001", "clause_type": "audit-and-inspection-rights", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "AUDIT AND INSPECTION\n\n1. SCOPE\nFinancial, compliance, security, and UK GDPR data protection audits.\n\n2. PROCEDURE\n(a) {{AUDIT_NOTICE_DAYS}} Business Days' notice; (b) business hours; (c) {{MAX_AUDITS_PER_YEAR}} annually.\n\n3. COSTS\n{{PARTY_B_NAME}} bears costs unless >5% discrepancy. Audit cooperations costs at {{PARTY_A_NAME}}'s expense.\n\n4. RECORDS\n{{RECORD_RETENTION_YEARS}} years per HMRC and Companies Act 2006 requirements."},
    {"id": "AUDIT_STR_UK001", "clause_type": "audit-and-inspection-rights", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "AUDIT AND INSPECTION\n\n1. SCOPE\nFinancials, compliance (Bribery Act 2010, Modern Slavery Act 2015), security (Cyber Essentials), data protection (UK GDPR Article 28(3)(h)), subcontractors.\n\n2. ACCESS\n(a) {{AUDIT_NOTICE_DAYS}} days' scheduled; (b) no-notice post-breach; (c) third-party auditors; (d) {{MAX_AUDITS_PER_YEAR}} scheduled + emergency.\n\n3. REMEDIATION\n{{REMEDIATION_DAYS}} days to cure. Repeat findings = material breach.\n\n4. RECORDS\n{{RECORD_RETENTION_YEARS}} years per HMRC, CA 2006, and data retention policies."},

    # ===== ANTI-BRIBERY AND COMPLIANCE =====
    {"id": "ANTIBRIBE_STD_001", "clause_type": "anti-bribery-compliance", "variant": "Standard", "jurisdiction": "India", "risk_level": "Low",
     "raw_text": "ANTI-BRIBERY\n\nEach Party shall comply with the Prevention of Corruption Act, 1988 and all applicable anti-bribery and anti-corruption laws. Neither Party shall offer, promise, give, or accept any bribe, kickback, or improper payment in connection with this Agreement."},
    {"id": "ANTIBRIBE_MOD_001", "clause_type": "anti-bribery-compliance", "variant": "Moderate", "jurisdiction": "India", "risk_level": "Medium",
     "raw_text": "ANTI-BRIBERY AND COMPLIANCE\n\n1. COMPLIANCE\nEach Party shall comply with: (a) Prevention of Corruption Act, 1988 (as amended 2018); (b) Prevention of Money Laundering Act, 2002; (c) all applicable anti-corruption laws.\n\n2. PROHIBITED CONDUCT\nNeither Party shall: (a) offer bribes or facilitation payments; (b) provide gifts exceeding INR {{GIFT_THRESHOLD}} without disclosure; (c) make political contributions in connection with this Agreement.\n\n3. COMPLIANCE PROGRAM\nEach Party shall maintain an anti-corruption compliance program including employee training, reporting channels, and due diligence on third parties.\n\n4. DISCLOSURE\nPrompt notification of any investigation, charge, or conviction related to corruption."},
    {"id": "ANTIBRIBE_STR_001", "clause_type": "anti-bribery-compliance", "variant": "Strict", "jurisdiction": "India", "risk_level": "High",
     "raw_text": "ANTI-BRIBERY AND COMPLIANCE\n\n1. COMPREHENSIVE COMPLIANCE\nCompliance with: (a) PCA 1988 (as amended); (b) PMLA 2002; (c) Companies Act 2013 (CSR and Related Party provisions); (d) FEMA, 1999; (e) any applicable foreign anti-corruption law.\n\n2. PROHIBITED ACTS\n(a) No bribes, kickbacks, or facilitation payments; (b) Gifts limited to INR {{GIFT_THRESHOLD}}; (c) No improper entertainment; (d) No political contributions; (e) No hiring of government officials' relatives without disclosure.\n\n3. DUE DILIGENCE\n(a) Third-party due diligence before engagement; (b) Annual compliance certifications; (c) Whistleblower channel per SEBI (Protection of Interests of Investors) mechanism.\n\n4. BOOKS AND RECORDS\nAccurate books per Companies Act 2013 and applicable accounting standards. No off-book payments.\n\n5. BREACH\nBreach is incurable material breach permitting immediate termination.\n\n6. INDEMNIFICATION\nThe breaching Party indemnifies the other against all penalties, fines, and enforcement costs."},

    {"id": "ANTIBRIBE_STD_US001", "clause_type": "anti-bribery-compliance", "variant": "Standard", "jurisdiction": "US", "risk_level": "Low",
     "raw_text": "ANTI-BRIBERY\n\nEach Party shall comply with the Foreign Corrupt Practices Act (FCPA), 15 U.S.C. §78dd, and all applicable anti-corruption laws. No Party shall make any improper payment to any government official or person."},
    {"id": "ANTIBRIBE_MOD_US001", "clause_type": "anti-bribery-compliance", "variant": "Moderate", "jurisdiction": "US", "risk_level": "Medium",
     "raw_text": "ANTI-BRIBERY AND COMPLIANCE\n\n1. FCPA COMPLIANCE\nCompliance with the FCPA (15 U.S.C. §78dd-1 et seq.), including anti-bribery and books-and-records provisions.\n\n2. PROHIBITED ACTS\n(a) No corrupt payments to foreign officials; (b) No facilitation payments; (c) Gifts/entertainment within policy limits (${{GIFT_THRESHOLD}}).\n\n3. COMPLIANCE PROGRAM\nAnti-corruption training, third-party due diligence, and internal reporting (hotline).\n\n4. SANCTIONS COMPLIANCE\nOFAC sanctions compliance. No transactions with Specially Designated Nationals (SDN) or sanctioned countries."},
    {"id": "ANTIBRIBE_STR_US001", "clause_type": "anti-bribery-compliance", "variant": "Strict", "jurisdiction": "US", "risk_level": "High",
     "raw_text": "ANTI-BRIBERY AND COMPLIANCE\n\n1. COMPREHENSIVE\nFCPA, Travel Act (18 U.S.C. §1952), state anti-corruption laws, OFAC, BIS/EAR export controls.\n\n2. ZERO TOLERANCE\n(a) No bribes (direct or indirect); (b) No facilitation payments; (c) Gifts capped at ${{GIFT_THRESHOLD}}; (d) No hiring of government-related persons without compliance review.\n\n3. DUE DILIGENCE\n(a) Background checks on agents and intermediaries; (b) OFAC/SDN screening; (c) Enhanced due diligence for high-risk jurisdictions.\n\n4. RECORDS AND INTERNAL CONTROLS\n(a) FCPA books-and-records compliance; (b) SOX-compliant internal controls; (c) Annual compliance certifications.\n\n5. WHISTLEBLOWER\nProtection per Dodd-Frank §922 and SOX §806.\n\n6. BREACH\nIncurable material breach. Immediate termination. Full indemnification."},

    {"id": "ANTIBRIBE_STD_UK001", "clause_type": "anti-bribery-compliance", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "ANTI-BRIBERY\n\nEach Party shall comply with the Bribery Act 2010 and shall not engage in any activity that would constitute an offence under sections 1, 2, 6, or 7 of that Act."},
    {"id": "ANTIBRIBE_MOD_UK001", "clause_type": "anti-bribery-compliance", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "ANTI-BRIBERY AND COMPLIANCE\n\n1. BRIBERY ACT 2010\nCompliance with all sections, including s.7 (failure to prevent bribery by associated persons).\n\n2. ADEQUATE PROCEDURES\nEach Party maintains \"adequate procedures\" (per Ministry of Justice Guidance) to prevent bribery.\n\n3. MODERN SLAVERY\nCompliance with Modern Slavery Act 2015. Annual slavery and human trafficking statement published.\n\n4. CRIMINAL FINANCES\nCompliance with Criminal Finances Act 2017 (prevention of tax evasion facilitation).\n\n5. GIFTS\nHospitality and gifts within policy (£{{GIFT_THRESHOLD}} threshold). Register maintained.\n\n6. DISCLOSURE\nPrompt notification of any SFO or NCA investigation."},
    {"id": "ANTIBRIBE_STR_UK001", "clause_type": "anti-bribery-compliance", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "ANTI-BRIBERY AND COMPLIANCE\n\n1. COMPREHENSIVE\nBribery Act 2010, Proceeds of Crime Act 2002, Modern Slavery Act 2015, Criminal Finances Act 2017, OFSI sanctions regime.\n\n2. ADEQUATE PROCEDURES\nMOJ six-principles compliance: (a) proportionate procedures; (b) top-level commitment; (c) risk assessment; (d) due diligence; (e) communication/training; (f) monitoring/review.\n\n3. NO TOLERANCE\n(a) No facilitation payments; (b) Gifts capped at £{{GIFT_THRESHOLD}}; (c) Hospitality pre-approved; (d) Political contributions prohibited.\n\n4. SUPPLY CHAIN\nDue diligence on all agents, intermediaries, and subcontractors. Modern Slavery Act compliance cascade.\n\n5. WHISTLEBLOWING\nPublic Interest Disclosure Act 1998 protections honoured.\n\n6. BREACH\nIncurable material breach. Immediate termination. Full indemnification for SFO/NCA fines and enforcement costs."},
]

# Contract type wiring for new clause types
CLAUSE_WIRING = {
    "insurance-requirements": [
        ("consulting-agreement", False, "Optional insurance requirements for consulting engagements"),
        ("vendor-agreement", True, "Vendor insurance requirements for procurement risk management"),
        ("master-service-agreement", True, "MSA insurance requirements for B2B engagements"),
        ("freelancer-agreement", False, "Optional insurance for freelance engagements"),
    ],
    "assignment-and-subcontracting": [
        ("consulting-agreement", True, "Assignment and subcontracting controls for consulting"),
        ("vendor-agreement", True, "Vendor subcontracting governance"),
        ("master-service-agreement", True, "MSA assignment and subcontracting provisions"),
        ("saas-agreement", True, "SaaS assignment provisions"),
        ("software-license", True, "License assignment restrictions"),
        ("freelancer-agreement", True, "Freelancer assignment restrictions"),
    ],
    "notices-and-communications": [
        ("consulting-agreement", True, "Notice provisions for consulting agreements"),
        ("vendor-agreement", True, "Vendor communication protocols"),
        ("master-service-agreement", True, "MSA notice mechanisms"),
        ("saas-agreement", True, "SaaS agreement notice provisions"),
        ("software-license", True, "License agreement notice provisions"),
        ("partnership-agreement", True, "Partnership notice provisions"),
        ("data-processing-agreement", True, "DPA notice provisions"),
        ("freelancer-agreement", True, "Freelancer agreement notice provisions"),
        ("joint-venture-agreement", True, "JV notice provisions"),
    ],
    "audit-and-inspection-rights": [
        ("vendor-agreement", True, "Vendor audit rights for compliance and financial verification"),
        ("master-service-agreement", True, "MSA audit provisions"),
        ("saas-agreement", False, "Optional SaaS audit rights"),
        ("data-processing-agreement", True, "DPA audit rights per GDPR/DPDPA requirements"),
        ("joint-venture-agreement", True, "JV financial audit rights"),
    ],
    "anti-bribery-compliance": [
        ("consulting-agreement", False, "Optional anti-bribery for consulting"),
        ("vendor-agreement", True, "Mandatory anti-bribery for vendor agreements"),
        ("master-service-agreement", True, "MSA anti-corruption covenants"),
        ("partnership-agreement", True, "Partnership anti-bribery requirements"),
        ("joint-venture-agreement", True, "JV anti-corruption compliance"),
    ],
}


def phase10(session):
    print("\n=== PHASE 10: New Clause Types ===\n")

    # 1. Create ClauseType nodes
    for ct in NEW_CLAUSE_TYPES:
        r = session.run("MATCH (c:ClauseType {id: $id}) RETURN count(*) AS cnt", {"id": ct["id"]})
        if r.single()["cnt"] == 0:
            session.run("""
                CREATE (ct:ClauseType {
                    id: $id, name: $name, category: $category,
                    importance_level: $importance_level, description: $description
                })
            """, ct)
            print(f"  ✓ Created ClauseType: {ct['id']}")
        else:
            print(f"  ⏭ ClauseType {ct['id']} exists")

    # 2. Create Clause nodes
    print()
    created = 0
    for clause in CLAUSES:
        r = session.run("MATCH (c:Clause {id: $id}) RETURN count(*) AS cnt", {"id": clause["id"]})
        if r.single()["cnt"] > 0:
            continue

        session.run("""
            CREATE (c:Clause {
                id: $id, clause_type: $clause_type, name: $name,
                variant: $variant, jurisdiction: $jurisdiction,
                risk_level: $risk_level, raw_text: $raw_text
            })
        """, {**clause, "name": f"{clause['clause_type']} — {clause['variant']} ({clause['jurisdiction']})"})

        # HAS_VARIANT
        session.run("""
            MATCH (ct:ClauseType {id: $ct_id}), (c:Clause {id: $c_id})
            CREATE (ct)-[:HAS_VARIANT]->(c)
        """, {"ct_id": clause["clause_type"], "c_id": clause["id"]})

        # GOVERNED_BY
        jmap = {"India": "India", "US": "us", "UK": "uk"}
        session.run("""
            MATCH (c:Clause {id: $c_id}), (j:Jurisdiction {id: $j_id})
            CREATE (c)-[:GOVERNED_BY]->(j)
        """, {"c_id": clause["id"], "j_id": jmap[clause["jurisdiction"]]})

        created += 1

    print(f"  Created {created} clause nodes")

    # 3. CONFLICTS_WITH and ALTERNATIVE_TO for new clauses (per jurisdiction)
    print("\n  Creating relationship edges for new clause types...")
    for juris in ["India", "US", "UK"]:
        for v1, v2, sev in [("Standard", "Moderate", "medium"), ("Standard", "Strict", "high"), ("Moderate", "Strict", "high")]:
            for a_var, b_var in [(v1, v2), (v2, v1)]:
                for ct in NEW_CLAUSE_TYPES:
                    session.run("""
                        MATCH (a:Clause {clause_type: $ct_id, variant: $a_var, jurisdiction: $juris}),
                              (b:Clause {clause_type: $ct_id, variant: $b_var, jurisdiction: $juris})
                        WHERE NOT (a)-[:CONFLICTS_WITH]->(b)
                        CREATE (a)-[:CONFLICTS_WITH {severity: $sev, conflict_type: 'duplication', reason: 'Variant conflict'}]->(b)
                    """, {"ct_id": ct["id"], "a_var": a_var, "b_var": b_var, "juris": juris, "sev": sev})

        for v1, v2, alt, strength in [
            ("Standard", "Moderate", "enhanced_protection", "medium"),
            ("Standard", "Strict", "maximum_protection", "low"),
            ("Moderate", "Standard", "simplified", "medium"),
            ("Moderate", "Strict", "enhanced_enforcement", "low"),
            ("Strict", "Moderate", "balanced_approach", "high"),
            ("Strict", "Standard", "simplified", "high"),
        ]:
            for ct in NEW_CLAUSE_TYPES:
                session.run("""
                    MATCH (a:Clause {clause_type: $ct_id, variant: $v1, jurisdiction: $juris}),
                          (b:Clause {clause_type: $ct_id, variant: $v2, jurisdiction: $juris})
                    WHERE NOT (a)-[:ALTERNATIVE_TO]->(b)
                    CREATE (a)-[:ALTERNATIVE_TO {
                        alternative_type: $alt, recommendation_strength: $strength,
                        reason: $v2 + ' variant offers alternative protection level',
                        benefit: 'Alternative ' + $v2 + ' level'
                    }]->(b)
                """, {"ct_id": ct["id"], "v1": v1, "v2": v2, "juris": juris, "alt": alt, "strength": strength})

    print("  ✓ CONFLICTS_WITH and ALTERNATIVE_TO edges created")

    # 4. Wire to contract types
    print("\n  Wiring new clause types to contract types...")
    for ct_id, wirings in CLAUSE_WIRING.items():
        for contract_type_id, mandatory, desc in wirings:
            r = session.run("""
                MATCH (ct:ContractType {id: $ct_id})-[:CONTAINS_CLAUSE]->(ctype:ClauseType {id: $clause_id})
                RETURN count(*) AS cnt
            """, {"ct_id": contract_type_id, "clause_id": ct_id})
            if r.single()["cnt"] > 0:
                continue

            r = session.run("""
                MATCH (ct:ContractType {id: $ct_id})-[r:CONTAINS_CLAUSE]->(ctype:ClauseType)
                RETURN max(r.sequence) AS max_seq
            """, {"ct_id": contract_type_id})
            max_seq = r.single()["max_seq"] or 20

            session.run("""
                MATCH (ct:ContractType {id: $ct_id}), (ctype:ClauseType {id: $clause_id})
                CREATE (ct)-[:CONTAINS_CLAUSE {
                    sequence: $seq, mandatory: $mandatory, description: $desc
                }]->(ctype)
            """, {"ct_id": contract_type_id, "clause_id": ct_id, "seq": max_seq + 1, "mandatory": mandatory, "desc": desc})
            print(f"    ✓ {ct_id} → {contract_type_id} ({'mandatory' if mandatory else 'optional'})")

    print("\n✅ Phase 10 complete!")


if __name__ == "__main__":
    with driver.session() as session:
        phase10(session)
    driver.close()
