"""
Phase 7: UK Jurisdiction Clauses
Creates 66 UK clause variants (22 clause types × 3 variants) with
UK-specific legal language, statute references (UCTA, CDPA, UK GDPR, etc.).
"""

from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

UK_CLAUSES = [
    # ===== CONFIDENTIALITY =====
    {"id": "CONF_STD_UK001", "clause_type": "confidentiality", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "CONFIDENTIALITY\n\n1. DEFINITION\n\"Confidential Information\" means any information disclosed by either Party which is identified as confidential or which ought reasonably to be considered confidential given the nature of the information and the circumstances of disclosure.\n\n2. OBLIGATIONS\nThe Receiving Party shall: (a) keep the Confidential Information confidential; (b) not disclose it to any person save as permitted; (c) use it only for the purposes of this Agreement.\n\n3. EXCLUSIONS\nThis clause does not apply to information which: (a) is or becomes publicly known otherwise than through breach; (b) was already in the Receiving Party's possession; (c) is independently developed; (d) is received from a third party entitled to disclose it.\n\n4. DURATION\nObligations continue for {{CONFIDENTIALITY_PERIOD}} years following termination.\n\n5. EQUITABLE RELIEF\nThe Disclosing Party shall be entitled to seek injunctive relief in the courts of England and Wales."},

    {"id": "CONF_MOD_UK001", "clause_type": "confidentiality", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "CONFIDENTIALITY\n\n1. DEFINED CATEGORIES\n\"Confidential Information\" means: (a) trade secrets (within the meaning of the Trade Secrets (Enforcement, etc.) Regulations 2018); (b) financial, commercial, and technical information; (c) customer and supplier data; (d) any information marked \"Confidential\" or disclosed in circumstances importing an obligation of confidence.\n\n2. OBLIGATIONS\nEach Party shall: (a) apply no lesser standard of care than it applies to its own confidential information (and in any event reasonable care); (b) limit disclosure to employees and professional advisers with a need to know who are bound by equivalent obligations; (c) promptly notify the Disclosing Party of any suspected unauthorised disclosure.\n\n3. PERMITTED DISCLOSURES\nDisclosure is permitted: (a) with prior written consent; (b) to professional advisers (subject to professional duty of confidence); (c) as required by law, regulation, or court order (with prompt notice and cooperation to seek protective orders).\n\n4. RETURN AND DESTRUCTION\nUpon termination or request, the Receiving Party shall return or destroy all Confidential Information and certify destruction in writing within {{RETURN_PERIOD_DAYS}} days.\n\n5. SURVIVAL\nObligations survive for {{CONFIDENTIALITY_PERIOD}} years. Trade secrets are protected indefinitely under common law and the 2018 Regulations."},

    {"id": "CONF_STR_UK001", "clause_type": "confidentiality", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "CONFIDENTIALITY\n\n1. COMPREHENSIVE SCOPE\n\"Confidential Information\" means all information (howsoever recorded or preserved) disclosed to or obtained by either Party, including trade secrets (Trade Secrets Regulations 2018), know-how, business methods, financial data, and all copies and extracts thereof.\n\n2. ENHANCED PROTECTIONS\nThe Receiving Party shall: (a) implement technical and organisational security measures proportionate to the sensitivity of the information; (b) restrict access to named individuals who have signed individual confidentiality undertakings; (c) maintain an access register; (d) not reverse-engineer or decompile any materials.\n\n3. INJUNCTIVE RELIEF\nThe Parties acknowledge that damages may not be an adequate remedy and that the Disclosing Party shall be entitled to seek injunctive and specific performance from the courts of England and Wales without the need to prove special damage.\n\n4. PUBLIC INTEREST DISCLOSURE\nNothing in this Agreement shall prevent either Party from making a protected disclosure within the meaning of the Employment Rights Act 1996, Part IVA.\n\n5. SURVIVAL\nConfidentiality obligations are perpetual for trade secrets and survive for {{CONFIDENTIALITY_PERIOD}} years for all other Confidential Information."},

    # ===== DEFINITIONS =====
    {"id": "DEFN_STD_UK001", "clause_type": "definitions", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "DEFINITIONS AND INTERPRETATION\n\nIn this Agreement, unless the context otherwise requires:\n\n\"Affiliate\" means any entity Controlling, Controlled by, or under common Control with a Party. \"Control\" has the meaning given by section 1124 of the Corporation Tax Act 2010.\n\"Agreement\" means this agreement including all schedules and annexes.\n\"Business Day\" means any day other than a Saturday, Sunday, or bank holiday in England and Wales.\n\"Effective Date\" means the date set out at the head of this Agreement.\n\"Party\" and \"Parties\" means {{PARTY_A_NAME}} and {{PARTY_B_NAME}}.\n\"Services\" means the services described in {{SERVICES_DESCRIPTION}}.\n\"VAT\" means value added tax under the Value Added Tax Act 1994."},

    {"id": "DEFN_MOD_UK001", "clause_type": "definitions", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "DEFINITIONS AND INTERPRETATION\n\n1. DEFINITIONS\n\"Affiliate\" means any entity Controlling, Controlled by, or under common Control with a Party (Control per CTA 2010 s.1124).\n\"Applicable Law\" means all applicable laws, statutes, regulations, and codes of practice of England and Wales.\n\"Business Day\" means Monday to Friday, excluding bank holidays in England and Wales.\n\"Change of Control\" means any change in Control of a Party.\n\"Confidential Information\" has the meaning in the Confidentiality clause.\n\"Deliverables\" means the deliverables specified in each SOW.\n\"Force Majeure Event\" has the meaning in clause [X].\n\"Good Industry Practice\" means the degree of skill, care, and diligence expected of a competent provider of services similar to the Services.\n\"Intellectual Property Rights\" means patents, trade marks, design rights, copyright, database rights, and rights in know-how.\n\"Losses\" means all losses, liabilities, damages, costs, and expenses (including reasonable legal fees).\n\"SOW\" means a Statement of Work agreed under this Agreement.\n\"VAT\" means value added tax under VATA 1994 and any similar replacement or additional tax.\n\n2. INTERPRETATION\n(a) References to statutes include amendments and re-enactments;\n(b) \"Including\" means \"including without limitation\";\n(c) Schedules form part of this Agreement."},

    {"id": "DEFN_STR_UK001", "clause_type": "definitions", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "DEFINITIONS AND INTERPRETATION\n\n1. DEFINITIONS\n\"Affiliate\" — CTA 2010 s.1124.\n\"Applicable Law\" — all statutes, statutory instruments, regulations, EU retained law (per the European Union (Withdrawal) Act 2018), and binding regulatory guidance.\n\"Bribery Laws\" — Bribery Act 2010 and associated guidance.\n\"Business Day\" — Monday-Friday excluding England and Wales bank holidays.\n\"Change of Control\" — any change in Control of a Party or a change in Ultimate Beneficial Ownership.\n\"Consequential Loss\" — loss of profits, revenue, goodwill, anticipated savings, and indirect or consequential loss (whether or not foreseeable).\n\"Data Protection Legislation\" — UK GDPR, Data Protection Act 2018, and PECR 2003.\n\"Good Industry Practice\" — practices, methods, and standards of skill, care, and diligence conforming to applicable BSI/ISO standards.\n\"Intellectual Property Rights\" — all IP rights including patents, trade marks, registered and unregistered design rights, copyright, database rights (Copyright, Designs and Patents Act 1988), semiconductor topography rights, and rights in know-how and trade secrets.\n\"Material Adverse Change\" — any event materially impairing a Party's ability to perform its obligations.\n\n2. INTERPRETATION\n(a) References to statutes include amendments, re-enactments, and subordinate legislation;\n(b) \"Including\" is not limiting;\n(c) Obligations of \"a Party\" bind that Party and its successors;\n(d) Order of precedence: amendments > main body > schedules > SOWs."},

    # ===== GOVERNING LAW =====
    {"id": "GOV_STD_UK001", "clause_type": "governing-law-and-jurisdiction", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "GOVERNING LAW AND JURISDICTION\n\nThis Agreement and any dispute or claim arising out of or in connection with it or its subject matter or formation (including non-contractual disputes or claims) shall be governed by and construed in accordance with the law of England and Wales. Each Party irrevocably agrees that the courts of England and Wales shall have exclusive jurisdiction."},

    {"id": "GOV_MOD_UK001", "clause_type": "governing-law-and-jurisdiction", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "GOVERNING LAW AND JURISDICTION\n\n1. GOVERNING LAW\nThis Agreement is governed by and construed in accordance with English law. The Parties exclude the application of the Contracts (Rights of Third Parties) Act 1999.\n\n2. ARBITRATION\nAny dispute shall be referred to and finally resolved by arbitration under the Rules of the London Court of International Arbitration (LCIA). The seat of arbitration shall be London. The tribunal shall consist of a sole arbitrator.\n\n3. LANGUAGE\nThe arbitration shall be conducted in English.\n\n4. INTERIM RELIEF\nNotwithstanding the arbitration clause, either Party may apply to the courts of England and Wales for interim injunctive relief under section 44 of the Arbitration Act 1996."},

    {"id": "GOV_STR_UK001", "clause_type": "governing-law-and-jurisdiction", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "GOVERNING LAW AND JURISDICTION\n\n1. GOVERNING LAW\nThis Agreement is governed by English law. The Contracts (Rights of Third Parties) Act 1999 is excluded. Rome I Regulation choice-of-law provisions are excluded to the extent permitted.\n\n2. ARBITRATION\nAll disputes shall be referred to arbitration under the LCIA Rules or ICC Rules (at Claimant's election). Seat: London. Tribunal: three arbitrators selected per LCIA/ICC appointment procedures.\n\n3. PROCEDURAL MATTERS\n(a) Limited disclosure per the Arbitration Act 1996 s.34;\n(b) The tribunal shall issue a reasoned final award;\n(c) The award is final and binding (s.58 Arbitration Act 1996);\n(d) Each Party bears its own costs; costs follow the event.\n\n4. EMERGENCY ARBITRATOR\nEmergency arbitrator relief available under LCIA Article 9B.\n\n5. COURT SUPPORT\nThe courts of England and Wales shall have non-exclusive jurisdiction for: (a) enforcement of arbitral awards; (b) interim measures under s.44 Arbitration Act 1996; (c) challenges under s.67-69."},

    # ===== DISPUTE RESOLUTION =====
    {"id": "DISP_STD_UK001", "clause_type": "dispute-resolution", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "DISPUTE RESOLUTION\n\nAny dispute arising out of or in connection with this Agreement shall be submitted to the exclusive jurisdiction of the courts of England and Wales. The Parties agree to submit to the jurisdiction of such courts."},

    {"id": "DISP_MOD_UK001", "clause_type": "dispute-resolution", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "DISPUTE RESOLUTION\n\n1. NEGOTIATION\nThe Parties shall first attempt to resolve any dispute by good-faith negotiation between senior representatives for {{NEGOTIATION_PERIOD_DAYS}} Business Days.\n\n2. MEDIATION\nIf not resolved, the dispute shall be referred to mediation under the CEDR Model Mediation Procedure for a period of {{MEDIATION_PERIOD_DAYS}} days.\n\n3. LITIGATION OR ARBITRATION\nIf mediation fails, disputes shall be determined by the courts of England and Wales (or by LCIA arbitration if specified in the Governing Law clause).\n\n4. CONTINUED PERFORMANCE\nThe Parties shall continue to perform their obligations during the dispute, excluding the obligation which is the subject of the dispute."},

    {"id": "DISP_STR_UK001", "clause_type": "dispute-resolution", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "DISPUTE RESOLUTION\n\n1. NOTICE OF DISPUTE\nA Party wishing to raise a dispute shall serve a written Dispute Notice setting out in reasonable detail the nature of the dispute.\n\n2. ESCALATION\n(a) Project managers: {{NEGOTIATION_PERIOD_DAYS}} Business Days;\n(b) Senior executives: {{EXECUTIVE_ESCALATION_DAYS}} Business Days;\n(c) CEO/Board level: {{CEO_ESCALATION_DAYS}} Business Days.\n\n3. MEDIATION\nCEDR Model Mediation Procedure, London. Maximum {{MEDIATION_PERIOD_DAYS}} days.\n\n4. ARBITRATION\nLCIA Rules, London, three arbitrators. Seat: London. English language. Reasoned award.\n\n5. URGENT RELIEF\nNothing prevents applications to the courts of England and Wales under s.44 Arbitration Act 1996 for injunctive or interim relief.\n\n6. CONFIDENTIALITY\nAll dispute resolution proceedings and outcomes are confidential.\n\n7. COSTS\nCosts follow the event absent exceptional circumstances."},

    # ===== PAYMENT TERMS =====
    {"id": "PAY_STD_UK001", "clause_type": "payment-terms", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "PAYMENT TERMS\n\n1. FEES\n{{PARTY_B_NAME}} shall pay {{PARTY_A_NAME}} the fees specified in the applicable SOW.\n\n2. INVOICING\nInvoices are issued {{INVOICE_FREQUENCY}} and payable within {{PAYMENT_DAYS}} days of receipt. All sums are in pounds sterling (GBP).\n\n3. VAT\nAll fees are exclusive of VAT. Where VAT is chargeable, {{PARTY_A_NAME}} shall issue a valid VAT invoice and {{PARTY_B_NAME}} shall pay the VAT amount.\n\n4. LATE PAYMENT\nInterest on overdue amounts accrues at the rate specified under the Late Payment of Commercial Debts (Interest) Act 1998 (currently Bank of England base rate + 8%)."},

    {"id": "PAY_MOD_UK001", "clause_type": "payment-terms", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "PAYMENT TERMS\n\n1. FEES AND INVOICING\nFees per SOW. Invoices payable Net {{PAYMENT_DAYS}} from invoice date. Payment by BACS, CHAPS, or Faster Payment to the designated bank account.\n\n2. EXPENSES\nReasonable pre-approved expenses reimbursable within {{EXPENSE_SUBMISSION_DAYS}} days, supported by receipts.\n\n3. VAT\nAll amounts exclusive of VAT. VAT invoices to be issued per HMRC requirements. Where reverse charge applies, {{PARTY_B_NAME}} shall account for VAT.\n\n4. CIS DEDUCTIONS\nWhere applicable, deductions under the Construction Industry Scheme (CIS) shall be made at the applicable rate.\n\n5. LATE PAYMENT\n(a) Statutory interest under the Late Payment of Commercial Debts Act 1998;\n(b) Compensation for recovery costs (£40/£70/£100 per invoice depending on debt size);\n(c) Suspension of Services after {{PAYMENT_DEFAULT_DAYS}} days' default.\n\n6. DISPUTES\nDisputes must be raised within {{INVOICE_DISPUTE_DAYS}} days. Undisputed amounts remain payable."},

    {"id": "PAY_STR_UK001", "clause_type": "payment-terms", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "PAYMENT TERMS\n\n1. MILESTONE PAYMENTS\nPayment structure per SOW milestones. Invoices due Net {{PAYMENT_DAYS}}.\n\n2. ESCROW\nFor contracts exceeding £{{ESCROW_THRESHOLD}}, {{ESCROW_PERCENTAGE}}% held in escrow with a regulated UK escrow agent.\n\n3. TAX COMPLIANCE\nVAT per VATA 1994. IR35 assessment required under the off-payroll working rules (Chapter 10, ITEPA 2003): {{PARTY_B_NAME}} shall determine employment status. If inside IR35, PAYE and NICs deductions apply.\n\n4. LATE PAYMENT\n(a) Late Payment Act statutory interest;\n(b) Administrative charge per statutory scale;\n(c) Automatic suspension after {{PAYMENT_DEFAULT_DAYS}} days;\n(d) Acceleration: all future milestones due upon second default within 12 months.\n\n5. AUDIT\nAnnual fee audit with {{AUDIT_NOTICE_DAYS}} days' notice. Underpayment >5% triggers {{PARTY_B_NAME}} bearing audit costs.\n\n6. NO SET-OFF\nNeither Party may set off amounts without written agreement."},

    # ===== SCOPE, TERM, IP, INDEMNIFICATION, LIABILITY, WARRANTIES, FM, TERMINATION, SURVIVAL, NON-COMPETE, NON-SOLICITATION, NDA, PARTIES, ENTIRE AGREEMENT, PROFIT SHARING, DPA =====
    # (Remaining 13 clause types × 3 variants = 39 clauses)

    {"id": "SCOP_STD_UK001", "clause_type": "scope-of-agreement", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "SCOPE OF AGREEMENT\n\n1. SERVICES\n{{PARTY_A_NAME}} shall provide the Services described in {{SERVICES_DESCRIPTION}} to {{PARTY_B_NAME}} with reasonable skill and care.\n\n2. STANDARD OF CARE\nServices shall be performed in accordance with Good Industry Practice and with the skill and care expected of a competent provider of such services.\n\n3. STATUS\n{{PARTY_A_NAME}} is an independent contractor and nothing in this Agreement creates a relationship of employment, agency, or partnership."},

    {"id": "SCOP_MOD_UK001", "clause_type": "scope-of-agreement", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "SCOPE OF AGREEMENT\n\n1. SOW FRAMEWORK\nServices are defined in individual Statements of Work. Each SOW specifies scope, deliverables, milestones, fees, and acceptance criteria.\n\n2. CHANGE CONTROL\nChanges require a written Change Request approved by both Parties, specifying impact on timelines, deliverables, and fees.\n\n3. ACCEPTANCE\nDeliverables subject to acceptance testing per SOW criteria. {{PARTY_B_NAME}} provides acceptance or rejection with reasons within {{ACCEPTANCE_PERIOD_DAYS}} Business Days. No response constitutes acceptance.\n\n4. STANDARD OF CARE\nServices shall conform to Good Industry Practice.\n\n5. NON-EXCLUSIVITY\nThis Agreement is non-exclusive. Both Parties may engage third parties for similar services."},

    {"id": "SCOP_STR_UK001", "clause_type": "scope-of-agreement", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "SCOPE OF AGREEMENT\n\n1. DETAILED SOW\nAll Services governed by signed SOWs specifying: (a) scope and exclusions; (b) deliverables with specifications; (c) milestones and critical path; (d) key personnel; (e) service levels; (f) fees.\n\n2. SERVICE LEVELS\nSLAs per SOW including: {{UPTIME_SLA}}% availability, {{RESPONSE_TIME}} response, and severity-based resolution targets. Service credits for SLA breaches.\n\n3. CHANGE CONTROL\nFormal change requests only. Unauthorised work at {{PARTY_A_NAME}}'s cost.\n\n4. ACCEPTANCE\n(a) Deliver with completion certificate;\n(b) Testing within {{ACCEPTANCE_PERIOD_DAYS}} Business Days;\n(c) Rejection with deficiency list;\n(d) Remediation within {{REMEDY_PERIOD_DAYS}} days;\n(e) Second rejection permits SOW termination.\n\n5. KEY PERSONNEL\nNamed personnel in SOW may not be removed without consent. Replacements of equivalent competence required."},

    {"id": "TERM_STD_UK001", "clause_type": "term-and-renewal", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "TERM AND RENEWAL\n\n1. INITIAL TERM\nThis Agreement commences on {{START_DATE}} and shall continue for {{TERM_DURATION}} (the \"Initial Term\").\n\n2. RENEWAL\nThe Agreement renews automatically for successive {{RENEWAL_TERM_DURATION}} periods unless either Party gives not less than {{NOTICE_PERIOD}} days' written notice before the end of the then-current term."},

    {"id": "TERM_MOD_UK001", "clause_type": "term-and-renewal", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "TERM AND RENEWAL\n\n1. INITIAL TERM\nFrom {{START_DATE}} to {{END_DATE}}.\n\n2. RENEWAL\nAuto-renewal for {{RENEWAL_TERM_DURATION}} periods unless {{RENEWAL_NOTICE_PERIOD}} days' notice of non-renewal.\n\n3. FEE ADJUSTMENT\nUpon renewal, fees may increase by up to {{PRICE_ADJUSTMENT_PERCENTAGE}}% or CPI (as published by ONS), whichever is lower.\n\n4. TRANSITION\nReasonable transition assistance for {{TRANSITION_DAYS}} days at prevailing rates."},

    {"id": "TERM_STR_UK001", "clause_type": "term-and-renewal", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "TERM AND RENEWAL\n\n1. FIXED TERM\nFrom {{START_DATE}} to {{END_DATE}} with minimum commitment of {{MINIMUM_COMMITMENT}}.\n\n2. RENEWAL\n(a) Auto-renewal for {{RENEWAL_TERM_DURATION}};\n(b) Non-renewal notice: {{RENEWAL_NOTICE_PERIOD}} days;\n(c) Acceptance window: {{RENEWAL_ACCEPTANCE_WINDOW_DAYS}} days.\n\n3. PRICE ESCALATION\nAnnual increase capped at {{PRICE_ADJUSTMENT_PERCENTAGE}}% or RPI, whichever is lower.\n\n4. HOLDOVER\nContinued performance after expiry: month-to-month at {{HOLDOVER_RATE_MULTIPLIER}}x rates, terminable on {{HOLDOVER_TERMINATION_NOTICE}} days' notice.\n\n5. BREAK CLAUSE\nEarly termination triggers early termination charge per Termination for Convenience clause."},

    {"id": "IP_STD_UK001", "clause_type": "intellectual-property-ownership", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "INTELLECTUAL PROPERTY\n\n1. WORK PRODUCT\nAll Intellectual Property Rights in materials created by {{PARTY_A_NAME}} in performance of this Agreement shall vest in {{PARTY_B_NAME}}.\n\n2. ASSIGNMENT\n{{PARTY_A_NAME}} assigns (by way of present assignment of future rights) all IP Rights in the Work Product to {{PARTY_B_NAME}} with full title guarantee.\n\n3. FURTHER ASSURANCE\n{{PARTY_A_NAME}} shall execute all documents and do all things necessary to give effect to this assignment pursuant to section 234 of the CDPA 1988."},

    {"id": "IP_MOD_UK001", "clause_type": "intellectual-property-ownership", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "INTELLECTUAL PROPERTY\n\n1. BACKGROUND IP\nEach Party retains its Background IP. Background IP is listed in Schedule {{IP_SCHEDULE}}.\n\n2. FOREGROUND IP\nAll IP Rights in Foreground IP vest in {{PARTY_B_NAME}} by assignment under CDPA 1988 (present assignment of future rights).\n\n3. LICENCE TO BACKGROUND IP\n{{PARTY_A_NAME}} grants a non-exclusive, perpetual, royalty-free licence to use Background IP embedded in Foreground IP.\n\n4. JOINT IP\nJointly created IP owned jointly, neither Party to exploit without the other's consent unless agreed in the SOW.\n\n5. MORAL RIGHTS\n{{PARTY_A_NAME}} irrevocably waives all moral rights under CDPA 1988, Chapter IV to the fullest extent permitted by law."},

    {"id": "IP_STR_UK001", "clause_type": "intellectual-property-ownership", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "INTELLECTUAL PROPERTY\n\n1. COMPREHENSIVE ASSIGNMENT\n(a) All IP Rights in Work Product vest in {{PARTY_B_NAME}} (present assignment of future rights, CDPA 1988 s.91);\n(b) Assignment includes the right to sue for past infringement;\n(c) {{PARTY_A_NAME}} shall procure equivalent assignments from all personnel.\n\n2. BACKGROUND IP\nListed in Schedule {{IP_SCHEDULE}}. Unlisted IP created during the term is presumed Foreground IP.\n\n3. MORAL RIGHTS WAIVER\nIrrevocable waiver under CDPA 1988 ss.77-85 to the fullest extent permitted. {{PARTY_A_NAME}} shall procure equivalent waivers from all contributors.\n\n4. REGISTERED RIGHTS\n{{PARTY_A_NAME}} shall assist with patent, trade mark, and design registration at {{PARTY_B_NAME}}'s expense.\n\n5. POWER OF ATTORNEY\n{{PARTY_A_NAME}} appoints {{PARTY_B_NAME}} as attorney to execute IP assignments if {{PARTY_A_NAME}} is unavailable. This power is irrevocable under the Powers of Attorney Act 1971 s.4."},

    {"id": "INDEM_STD_UK001", "clause_type": "indemnification", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "INDEMNIFICATION\n\n{{PARTY_A_NAME}} shall indemnify and hold harmless {{PARTY_B_NAME}} against all Losses arising from: (a) breach of this Agreement; (b) negligent or wrongful acts; (c) breach of applicable law."},

    {"id": "INDEM_MOD_UK001", "clause_type": "indemnification", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "INDEMNIFICATION\n\n1. MUTUAL INDEMNITY\nEach Party indemnifies the other against third-party Claims arising from: (a) material breach; (b) negligence; (c) breach of law.\n\n2. IP INDEMNITY\n{{PARTY_A_NAME}} indemnifies {{PARTY_B_NAME}} against Claims that Deliverables infringe UK IP Rights.\n\n3. PROCEDURE\n(a) Prompt written notice;\n(b) Sole conduct of defence (subject to UCTA 1977 reasonableness);\n(c) Reasonable cooperation.\n\n4. IP REMEDIES\nIf enjoined: (a) obtain licence; (b) modify to non-infringing; (c) refund fees for infringing element.\n\n5. EXCLUSIONS\nNo indemnity for Claims arising from {{PARTY_B_NAME}}'s modifications or combination with third-party materials."},

    {"id": "INDEM_STR_UK001", "clause_type": "indemnification", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "INDEMNIFICATION\n\n1. COMPREHENSIVE INDEMNITY\nEach Party indemnifies the other against all Claims and Losses (including Consequential Loss where applicable) arising from: (a) any breach; (b) negligence, gross negligence, or wilful default; (c) breach of Data Protection Legislation; (d) death or personal injury.\n\n2. IP INDEMNITY\n{{PARTY_A_NAME}} indemnifies against worldwide IP infringement Claims. First-party coverage with no threshold.\n\n3. DATA BREACH INDEMNITY\n{{PARTY_A_NAME}} indemnifies against ICO enforcement action, fines, compensation claims, and notification costs arising from {{PARTY_A_NAME}}'s processing breach.\n\n4. MITIGATION\nThe indemnified Party shall take reasonable steps to mitigate Losses (per the common law duty of mitigation).\n\n5. SURVIVAL\nIndemnity obligations survive for the applicable limitation period (Limitation Act 1980) plus {{INDEMNITY_SURVIVAL_YEARS}} years."},

    {"id": "LIAB_STD_UK001", "clause_type": "limitation-of-liability", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "LIMITATION OF LIABILITY\n\n1. EXCLUSION OF INDIRECT LOSS\nNeither Party shall be liable for any indirect, special, or consequential loss or damage.\n\n2. CAP\nEach Party's total aggregate liability shall not exceed the fees paid or payable in the {{LIABILITY_CAP_PERIOD}} months preceding the Claim.\n\n3. STATUTORY EXCLUSIONS\nNothing in this Agreement excludes or limits liability for: (a) death or personal injury caused by negligence; (b) fraud or fraudulent misrepresentation; (c) any other liability which cannot be excluded by law (UCTA 1977, s.2)."},

    {"id": "LIAB_MOD_UK001", "clause_type": "limitation-of-liability", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "LIMITATION OF LIABILITY\n\n1. EXCLUSION\nSubject to clause 3, neither Party is liable for loss of profits, revenue, goodwill, anticipated savings, or indirect/consequential loss.\n\n2. CAP\nTotal aggregate liability: {{LIABILITY_CAP_MULTIPLIER}}x fees paid in the {{LIABILITY_CAP_PERIOD}} months preceding the Claim.\n\n3. UNCAPPED LIABILITY\nNo limit applies to: (a) death or personal injury from negligence (UCTA 1977 s.2(1)); (b) fraud; (c) breach of confidence involving trade secrets; (d) IP indemnification; (e) data protection breaches.\n\n4. REASONABLENESS\nThe aggregate cap represents a genuine pre-estimate of the maximum likely loss and satisfies the requirement of reasonableness under UCTA 1977 s.11(1).\n\n5. INSURANCE\nEach Party shall maintain adequate professional indemnity and public liability insurance."},

    {"id": "LIAB_STR_UK001", "clause_type": "limitation-of-liability", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "LIMITATION OF LIABILITY\n\n1. EXCLUSION\nSubject to clause 3, neither Party is liable for Consequential Loss (as defined).\n\n2. TIERED CAPS\n(a) Per-incident: greater of £{{PER_INCIDENT_CAP}} or 3 months' fees;\n(b) Annual aggregate: {{LIABILITY_CAP_MULTIPLIER}}x annual fees;\n(c) Lifetime: {{LIFETIME_CAP_MULTIPLIER}}x total contract value.\n\n3. UNCAPPED\nNo limitation on: (a) death/personal injury (UCTA s.2(1)); (b) fraud; (c) wilful default; (d) breach of confidence/trade secrets; (e) data protection breach (ICO fines and enforcement); (f) IP indemnity.\n\n4. UCTA COMPLIANCE\nCaps satisfy UCTA 1977 s.11 reasonableness having regard to: (a) parties' relative bargaining positions; (b) insurance availability; (c) whether term was negotiated.\n\n5. INSURANCE\n(a) Professional Indemnity: £{{PI_COVERAGE}};\n(b) Public Liability: £{{PL_COVERAGE}};\n(c) Cyber Liability: £{{CYBER_COVERAGE}};\n(d) Employer's Liability: per statutory minimum. Certificates on request."},

    {"id": "WARR_STD_UK001", "clause_type": "representations-and-warranties", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "REPRESENTATIONS AND WARRANTIES\n\nEach Party warrants that: (a) it has full capacity and authority to enter into and perform this Agreement; (b) this Agreement constitutes a legal, valid, and binding obligation; (c) it shall comply with all Applicable Law; (d) performance does not breach any other agreement."},

    {"id": "WARR_MOD_UK001", "clause_type": "representations-and-warranties", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "REPRESENTATIONS AND WARRANTIES\n\n1. MUTUAL WARRANTIES\n(a) Duly incorporated and validly existing under the Companies Act 2006;\n(b) Authority of signatories (per articles of association);\n(c) No conflict with existing obligations;\n(d) Compliance with Applicable Law, including Bribery Act 2010 and Modern Slavery Act 2015.\n\n2. SERVICE WARRANTIES\n{{PARTY_A_NAME}} warrants: (a) Services performed with reasonable skill and care (Supply of Goods and Services Act 1982 s.13); (b) Deliverables conform to specifications for {{WARRANTY_PERIOD}} days; (c) no infringement of third-party IP Rights.\n\n3. EXCLUSIONS\nSave as expressly set out, all conditions, warranties, and terms implied by statute (Sale of Goods Act 1979, Supply of Goods and Services Act 1982) or common law are excluded to the maximum extent permitted.\n\n4. REMEDY\nBreach entitles {{PARTY_B_NAME}} to require re-performance or refund."},

    {"id": "WARR_STR_UK001", "clause_type": "representations-and-warranties", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "REPRESENTATIONS AND WARRANTIES\n\n1. CORPORATE\n(a) Duly incorporated under Companies Act 2006 and in good standing;\n(b) Board authority and all necessary resolutions obtained;\n(c) No winding-up proceedings, administration, or Company Voluntary Arrangement.\n\n2. COMPLIANCE\n(a) Bribery Act 2010 — adequate procedures in place;\n(b) Modern Slavery Act 2015 — slavery and human trafficking statement published;\n(c) Criminal Finances Act 2017 — prevention of tax evasion;\n(d) Sanctions compliance (OFSI).\n\n3. FINANCIAL SOLVENCY\nNot insolvent within the meaning of the Insolvency Act 1986. Able to pay debts as they fall due.\n\n4. SERVICE WARRANTIES\n(a) Conformity to specification for {{WARRANTY_PERIOD}} days;\n(b) Good Industry Practice per applicable BSI/ISO standards;\n(c) No open-source with copyleft obligations without disclosure;\n(d) Free from malicious code.\n\n5. EXCLUSIONS\nImplied terms excluded to the maximum extent under UCTA 1977.\n\n6. DISCLOSURE\nPrompt notification of any event making any warranty materially inaccurate."},

    {"id": "FM_STD_UK001", "clause_type": "force-majeure", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "FORCE MAJEURE\n\nNeither Party shall be liable for delay or failure to perform caused by circumstances beyond its reasonable control, including acts of God, war, terrorism, fire, flood, epidemic, governmental action, or industrial disputes (not involving the affected Party's workforce). The affected Party shall give prompt notice and use reasonable endeavours to mitigate. If the event continues for {{FM_THRESHOLD_DAYS}} days, either Party may terminate on written notice."},

    {"id": "FM_MOD_UK001", "clause_type": "force-majeure", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "FORCE MAJEURE\n\n1. DEFINED EVENTS\nForce Majeure means: (a) natural disaster; (b) pandemic (WHO-declared); (c) war, terrorism, civil unrest; (d) governmental restrictions, sanctions (OFSI); (e) cyberattack on critical national infrastructure; (f) failure of utility services beyond the Party's control; (g) Brexit-related regulatory disruption (if applicable).\n\n2. NOTIFICATION\nWritten notice within {{FM_NOTICE_DAYS}} Business Days with mitigation plan.\n\n3. MITIGATION\nReasonable endeavours to overcome or work around the event, including engaging alternative suppliers.\n\n4. PAYMENT\nPayment obligations suspended proportionally during the FM period.\n\n5. TERMINATION\nIf FM continues for {{FM_THRESHOLD_DAYS}} days, either Party may terminate on {{FM_TERMINATION_NOTICE}} days' notice without further liability."},

    {"id": "FM_STR_UK001", "clause_type": "force-majeure", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "FORCE MAJEURE\n\n1. ENUMERATED EVENTS\nForce Majeure: (a) acts of God; (b) WHO or UK Government-declared pandemic; (c) war, military action; (d) cyberattack, ransomware; (e) OFSI sanctions, export controls; (f) critical infrastructure failure; (g) supply chain collapse. Excluded: financial difficulty, Brexit consequences (unless involving new legal impossibility), staffing issues.\n\n2. NOTICE AND BCP\n(a) Written notice within {{FM_NOTICE_DAYS}} Business Days;\n(b) Activate Business Continuity Plan within 48 hours;\n(c) Weekly status reports.\n\n3. TIERED RESPONSE\n(a) Days 1-{{FM_PHASE1_DAYS}}: suspension with mitigation;\n(b) Days {{FM_PHASE1_DAYS}}-{{FM_THRESHOLD_DAYS}}: mandatory renegotiation under the common law doctrine of frustration (Law Reform (Frustrated Contracts) Act 1943);\n(c) Beyond {{FM_THRESHOLD_DAYS}} days: termination right.\n\n4. INSURANCE\nAfected Party shall pursue all applicable insurance claims. Recovery shared equitably."},

    {"id": "TERMB_STD_UK001", "clause_type": "termination-for-cause", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "TERMINATION FOR CAUSE\n\nEither Party may terminate this Agreement by written notice if the other Party: (a) commits a material breach and fails to remedy within {{CURE_PERIOD}} days of written notice; (b) enters administration, has a winding-up order made, or passes a resolution for voluntary winding-up (Insolvency Act 1986)."},

    {"id": "TERMB_MOD_UK001", "clause_type": "termination-for-cause", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "TERMINATION FOR CAUSE\n\n1. MATERIAL BREACH\nTermination on {{CURE_PERIOD_STANDARD}} days' notice if breach uncured. Payment default: {{CURE_PERIOD_SHORT}} days.\n\n2. INSOLVENCY EVENTS\nImmediate termination if the other Party: (a) enters administration (IA 1986 Sch.B1); (b) has a winding-up petition presented; (c) makes a company voluntary arrangement; (d) has a receiver appointed.\n\n3. SLA FAILURES\nTermination after {{CONSECUTIVE_FAILURES}} consecutive or {{CUMULATIVE_FAILURES}} cumulative SLA failures in 12 months.\n\n4. REGULATORY CHANGE\nTermination on {{REGULATORY_NOTICE_DAYS}} days' notice if regulatory changes make performance unlawful."},

    {"id": "TERMB_STR_UK001", "clause_type": "termination-for-cause", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "TERMINATION FOR CAUSE\n\n1. BREACH\n{{CURE_PERIOD_STANDARD}} days to cure. Repeated breach of same obligation within 12 months is incurable.\n\n2. AUTOMATIC TERMINATION\nImmediate (no cure) upon: (a) insolvency event (IA 1986); (b) dissolution or striking off (CA 2006); (c) fraud or criminal conviction of directors; (d) breach of data protection or confidentiality.\n\n3. SLA TERMINATION\n(a) {{CONSECUTIVE_SLA_FAILURES}} consecutive SLA failures;\n(b) Availability below {{OUTAGE_TERMINATION_THRESHOLD}}%;\n(c) Failure to deliver remediation plan within {{REMEDIATION_PLAN_PERIOD}} days.\n\n4. IPSO FACTO PROTECTION\nFor the avoidance of doubt, the insolvency termination rights are subject to any applicable restrictions on ipso facto clauses under the Corporate Insolvency and Governance Act 2020.\n\n5. CROSS-DEFAULT\nMaterial breach of any agreement between the Parties entitles termination of this Agreement."},

    {"id": "TERMC_STD_UK001", "clause_type": "termination-for-convenience", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "TERMINATION FOR CONVENIENCE\n\nEither Party may terminate this Agreement at any time by giving not less than {{NOTICE_PERIOD}} days' written notice. Upon termination, {{PARTY_B_NAME}} shall pay for all Services performed up to the effective date."},

    {"id": "TERMC_MOD_UK001", "clause_type": "termination-for-convenience", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "TERMINATION FOR CONVENIENCE\n\n1. NOTICE\nEither Party may terminate on {{NOTICE_PERIOD_LONG}} days' written notice.\n\n2. WIND-DOWN\n{{PARTY_A_NAME}} shall: (a) complete WIP to a reasonable stopping point; (b) deliver all completed Deliverables; (c) return {{PARTY_B_NAME}} materials within {{RETURN_MATERIALS_DAYS}} days.\n\n3. PAYMENT\n{{PARTY_B_NAME}} shall pay: (a) Services rendered; (b) WIP on a quantum meruit basis; (c) irrecoverable third-party costs.\n\n4. TRANSITION\nTransition assistance for {{TRANSITION_ASSISTANCE_DAYS}} days at prevailing rates."},

    {"id": "TERMC_STR_UK001", "clause_type": "termination-for-convenience", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "TERMINATION FOR CONVENIENCE\n\n1. DIFFERENTIATED NOTICE\n(a) Client: {{CLIENT_NOTICE_PERIOD}} days;\n(b) Provider: {{VENDOR_NOTICE_PERIOD}} days.\n\n2. EARLY TERMINATION CHARGE\nIf before minimum commitment: {{EARLY_TERMINATION_FEE_PERCENTAGE}}% of remaining contract value.\n\n3. WIP SETTLEMENT\n(a) Completed milestones: 100%; (b) WIP: {{WIP_PERCENTAGE}}% of milestone; (c) Valuation: {{WIP_VALUATION_METHOD}}.\n\n4. MANDATORY TRANSITION\n{{MINIMAL_TRANSITION_DAYS}} days' transition at {{TRANSITION_RATE}}.\n\n5. MATERIALS\nAll materials and data returned within {{RETURN_PERIOD}} days with certification."},

    {"id": "SURV_STD_UK001", "clause_type": "effect-of-termination-and-survival", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "EFFECT OF TERMINATION AND SURVIVAL\n\n1. EFFECT\nUpon termination: (a) rights and licences cease; (b) Confidential Information returned; (c) outstanding payments become due.\n\n2. SURVIVAL\nConfidentiality, IP, Indemnification, Limitation of Liability, Governing Law, and Dispute Resolution survive termination."},

    {"id": "SURV_MOD_UK001", "clause_type": "effect-of-termination-and-survival", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "EFFECT OF TERMINATION AND SURVIVAL\n\n1. IMMEDIATE EFFECTS\n(a) Licences terminate within {{ACCESS_TERMINATION_DAYS}} days; (b) invoices for Services rendered become immediately due; (c) each Party returns the other's property.\n\n2. TRANSITION\nTransition assistance for {{TRANSITION_DAYS}} days.\n\n3. ACCRUED RIGHTS\nTermination does not affect accrued rights, including warranty claims and indemnification obligations (per common law).\n\n4. SURVIVAL\nClauses surviving by nature: Confidentiality, IP, Indemnity, Liability, Governing Law, Dispute Resolution."},

    {"id": "SURV_STR_UK001", "clause_type": "effect-of-termination-and-survival", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "EFFECT OF TERMINATION AND SURVIVAL\n\n1. WIND-DOWN\nWithin {{WIND_DOWN_DAYS}} days: (a) cease new work; (b) complete critical WIP; (c) deliver work product; (d) revoke access; (e) return materials.\n\n2. DATA\n(a) Export in open format within {{DATA_EXPORT_DAYS}} days;\n(b) Deletion within {{DATA_DELETION_DAYS}} days;\n(c) Officer certification of deletion.\n\n3. KNOWLEDGE TRANSFER\nMandatory KT: documentation, training, vendor transition support.\n\n4. FINANCIAL\n(a) Final invoice within {{FINAL_INVOICE_DAYS}} days;\n(b) Prepaid fee reconciliation;\n(c) Refund within {{REFUND_DAYS}} days.\n\n5. SURVIVAL\nConfidentiality (perpetual for trade secrets, {{CONFIDENTIALITY_PERIOD}} years otherwise), IP, Indemnity (per Limitation Act 1980), Liability, Governing Law, Dispute Resolution. General obligations: {{GENERAL_SURVIVAL_YEARS}} years."},

    {"id": "NONCOMP_STD_UK001", "clause_type": "non-compete", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "NON-COMPETE\n\nDuring the term and for {{NON_COMPETE_PERIOD}} months thereafter, {{PARTY_A_NAME}} shall not engage in any business that directly competes with {{PARTY_B_NAME}}'s core business within {{GEOGRAPHIC_SCOPE}}.\n\nThis restriction is considered reasonable and necessary for the protection of {{PARTY_B_NAME}}'s legitimate business interests."},

    {"id": "NONCOMP_MOD_UK001", "clause_type": "non-compete", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "NON-COMPETE\n\n1. RESTRICTION\nDuring the term and {{NON_COMPETE_PERIOD}} months post-termination: (a) not to carry on or engage in a Competing Business; (b) not to be employed by or act as consultant to a Competing Business.\n\n2. COMPETING BUSINESS\nA business providing {{COMPETING_SERVICES_DESCRIPTION}} within {{GEOGRAPHIC_SCOPE}}.\n\n3. REASONABLENESS\nThe Parties acknowledge these restrictions are reasonable and necessary to protect {{PARTY_B_NAME}}'s legitimate interests (trade secrets, confidential information, and customer connections) per common law restraint of trade doctrine.\n\n4. GARDEN LEAVE\n{{PARTY_B_NAME}} may place {{PARTY_A_NAME}} on garden leave during any notice period, during which the non-compete period runs concurrently.\n\n5. SEVERANCE\nIf any restriction is held unreasonable, the court is requested to sever the offending words and give effect to the remainder."},

    {"id": "NONCOMP_STR_UK001", "clause_type": "non-compete", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "NON-COMPETE\n\n1. COMPREHENSIVE RESTRICTION\nDuring the term and {{NON_COMPETE_PERIOD}} months post-termination: not directly or indirectly carry on, be engaged in, or interested in any Competing Business anywhere within {{GEOGRAPHIC_SCOPE}}.\n\n2. BROAD DEFINITION\n\"Competing Business\" includes any business dealing in products or services substantially similar to those of {{PARTY_B_NAME}} or its group companies.\n\n3. LEGITIMATE INTERESTS\nRestrictions protect: (a) trade secrets and confidential information; (b) customer connections and goodwill; (c) workforce stability.\n\n4. GARDEN LEAVE\nDuring notice period, {{PARTY_B_NAME}} may invoke garden leave. Non-compete period offset by garden leave served.\n\n5. LIQUIDATED DAMAGES\nBreach entitles {{PARTY_B_NAME}} to liquidated damages of £{{LIQUIDATED_DAMAGES_AMOUNT}} per breach.\n\n6. INJUNCTIVE RELIEF\nConsent to injunctive relief without proof of actual damage.\n\n7. BLUE PENCIL\nCourt invited to sever or modify restrictions to render enforceable per the blue-pencil test (Attwood v Lamont)."},

    {"id": "NONSOL_STD_UK001", "clause_type": "non-solicitation", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "NON-SOLICITATION\n\nDuring the term and {{NON_SOLICITATION_PERIOD}} months thereafter, neither Party shall solicit or entice away any employee of the other Party who was materially involved in this Agreement. General recruitment advertising is not solicitation."},

    {"id": "NONSOL_MOD_UK001", "clause_type": "non-solicitation", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "NON-SOLICITATION\n\n1. EMPLOYEES\nDuring the term and {{NON_SOLICITATION_PERIOD}} months post-termination, neither Party shall solicit, recruit, or entice away employees who were involved in this Agreement.\n\n2. CLIENTS\n{{PARTY_A_NAME}} shall not solicit {{PARTY_B_NAME}}'s customers or prospective customers with whom {{PARTY_A_NAME}} had dealings during the engagement for {{CLIENT_NON_SOLICIT_PERIOD}} months.\n\n3. EXCEPTIONS\nGeneral advertising and unsolicited approaches are permitted.\n\n4. REASONABLENESS\nRestrictions protect legitimate business interests and customer connections."},

    {"id": "NONSOL_STR_UK001", "clause_type": "non-solicitation", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "NON-SOLICITATION\n\n1. COMPREHENSIVE RESTRICTION\nDuring term and {{NON_SOLICITATION_PERIOD}} months post-termination: not solicit, recruit, entice, or hire any employee, officer, or contractor; not encourage termination of association.\n\n2. CLIENT PROTECTION\nNot solicit, interfere with, or divert any client or prospect within the {{LOOKBACK_MONTHS}}-month lookback.\n\n3. LIQUIDATED DAMAGES\nBreach: liquidated damages equal to the person's annual compensation or £{{LIQUIDATED_DAMAGES_AMOUNT}}, whichever is greater.\n\n4. INJUNCTION\nConsent to injunctive relief. Court to apply per Lansing Linde Ltd v Kerr proportionality test."},

    {"id": "NDISC_STD_UK001", "clause_type": "non-disclosure-employment", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "NON-DISCLOSURE (EMPLOYMENT)\n\nEmployee acknowledges access to Confidential Information and agrees: (a) to maintain strict confidentiality; (b) not to use for personal or third-party benefit; (c) to return all materials on termination. Obligations survive for {{NDA_SURVIVAL_YEARS}} years. Trade secrets protected indefinitely at common law and under the Trade Secrets Regulations 2018."},

    {"id": "NDISC_MOD_UK001", "clause_type": "non-disclosure-employment", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "NON-DISCLOSURE (EMPLOYMENT)\n\n1. SCOPE\nEmployee shall not disclose trade secrets, customer data, financial information, source code, or business strategy, whether during or after employment.\n\n2. PERMITTED DISCLOSURES\n(a) In performance of duties; (b) with written authorisation; (c) as required by law; (d) protected disclosures under the Employment Rights Act 1996, Part IVA (whistleblowing).\n\n3. RETURN\nReturn all materials within {{RETURN_PERIOD_DAYS}} days of termination with deletion certification.\n\n4. SURVIVAL\nTrade secrets: perpetual. Other Confidential Information: {{NDA_SURVIVAL_YEARS}} years."},

    {"id": "NDISC_STR_UK001", "clause_type": "non-disclosure-employment", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "NON-DISCLOSURE (EMPLOYMENT)\n\n1. COMPREHENSIVE OBLIGATION\nAbsolute confidentiality of all non-public information learned during employment.\n\n2. SECURITY CONTROLS\n(a) Company-approved devices only; (b) no personal device transfers; (c) VPN and encryption for remote access; (d) immediate incident reporting.\n\n3. EXIT\n(a) Exit interview confirming obligations;\n(b) Return all materials within {{RETURN_PERIOD_DAYS}} days;\n(c) Deletion certification (forensic verification on request).\n\n4. WHISTLEBLOWING\nNothing prevents a protected disclosure under ERA 1996 Part IVA.\n\n5. INJUNCTION\nConsent to injunctive and specific performance.\n\n6. SURVIVAL\nPerpetual for trade secrets; {{NDA_SURVIVAL_YEARS}} years otherwise."},

    {"id": "PART_STD_UK001", "clause_type": "parties-and-recitals", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "PARTIES\n\nThis Agreement is dated {{EFFECTIVE_DATE}} and made between:\n\n(1) {{PARTY_A_NAME}}, a company incorporated in England and Wales with company number {{PARTY_A_COMPANY_NUMBER}}, whose registered office is at {{PARTY_A_ADDRESS}} (\"{{PARTY_A_SHORT_NAME}}\"); and\n\n(2) {{PARTY_B_NAME}}, a company incorporated in England and Wales with company number {{PARTY_B_COMPANY_NUMBER}}, whose registered office is at {{PARTY_B_ADDRESS}} (\"{{PARTY_B_SHORT_NAME}}\").\n\nBACKGROUND\n\n(A) {{PARTY_A_SHORT_NAME}} provides {{SERVICES_DESCRIPTION}}.\n(B) {{PARTY_B_SHORT_NAME}} wishes to engage {{PARTY_A_SHORT_NAME}} on the terms of this Agreement.\n\nIT IS AGREED as follows:"},

    {"id": "PART_MOD_UK001", "clause_type": "parties-and-recitals", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "PARTIES\n\nThis Agreement is dated {{EFFECTIVE_DATE}} and made between:\n\n(1) {{PARTY_A_NAME}} (company no. {{PARTY_A_COMPANY_NUMBER}}), registered in England and Wales, registered office: {{PARTY_A_ADDRESS}}, VAT no. {{PARTY_A_VAT_NUMBER}} (\"{{PARTY_A_SHORT_NAME}}\"); and\n\n(2) {{PARTY_B_NAME}} (company no. {{PARTY_B_COMPANY_NUMBER}}), registered in England and Wales, registered office: {{PARTY_B_ADDRESS}}, VAT no. {{PARTY_B_VAT_NUMBER}} (\"{{PARTY_B_SHORT_NAME}}\").\n\nBACKGROUND\n\n(A) {{PARTY_A_SHORT_NAME}} is engaged in {{PARTY_A_BUSINESS}}.\n(B) {{PARTY_B_SHORT_NAME}} wishes to engage {{PARTY_A_SHORT_NAME}} to provide certain services.\n(C) The Parties have agreed the terms upon which such services will be provided.\n\nIT IS AGREED as follows:"},

    {"id": "PART_STR_UK001", "clause_type": "parties-and-recitals", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "PARTIES\n\nThis Agreement is dated the date of last execution below and made between:\n\n(1) {{PARTY_A_NAME}} (company no. {{PARTY_A_COMPANY_NUMBER}}), incorporated under the Companies Act 2006, registered office: {{PARTY_A_ADDRESS}}, VAT: {{PARTY_A_VAT_NUMBER}}, acting by {{PARTY_A_SIGNATORY}}, {{PARTY_A_SIGNATORY_TITLE}}, duly authorised (\"{{PARTY_A_SHORT_NAME}}\"); and\n\n(2) {{PARTY_B_NAME}} (company no. {{PARTY_B_COMPANY_NUMBER}}), incorporated under the Companies Act 2006, registered office: {{PARTY_B_ADDRESS}}, VAT: {{PARTY_B_VAT_NUMBER}}, acting by {{PARTY_B_SIGNATORY}}, {{PARTY_B_SIGNATORY_TITLE}}, duly authorised (\"{{PARTY_B_SHORT_NAME}}\").\n\nBACKGROUND\n\n(A) Each signatory warrants authority to bind their respective Party.\n(B) The Parties have conducted appropriate due diligence.\n(C) All necessary board approvals have been obtained per each Party's articles of association.\n\nIT IS AGREED as follows:"},

    {"id": "ENTIRE_STD_UK001", "clause_type": "entire-agreement-amendments-severability", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "ENTIRE AGREEMENT; AMENDMENTS; SEVERABILITY\n\n1. ENTIRE AGREEMENT\nThis Agreement constitutes the entire agreement between the Parties and supersedes all prior discussions, understandings, and agreements.\n\n2. AMENDMENTS\nNo variation shall be effective unless in writing and signed by both Parties.\n\n3. SEVERABILITY\nIf any provision is held invalid by a court of competent jurisdiction, such provision shall be severed and the remaining provisions shall continue in full force."},

    {"id": "ENTIRE_MOD_UK001", "clause_type": "entire-agreement-amendments-severability", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "ENTIRE AGREEMENT; AMENDMENTS; SEVERABILITY\n\n1. ENTIRE AGREEMENT\nThis Agreement (together with Schedules and SOWs) constitutes the entire agreement. Each Party acknowledges it has not relied on any statement, representation, or warranty not set out herein (but nothing excludes liability for fraudulent misrepresentation).\n\n2. VARIATION\nNo variation effective unless in writing signed by authorised representatives.\n\n3. WAIVER\nNo waiver unless in writing. Failure to exercise a right is not a waiver.\n\n4. SEVERABILITY\nInvalid provisions reformed to the minimum extent necessary; remainder unaffected.\n\n5. THIRD PARTY RIGHTS\nThe Contracts (Rights of Third Parties) Act 1999 is excluded."},

    {"id": "ENTIRE_STR_UK001", "clause_type": "entire-agreement-amendments-severability", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "ENTIRE AGREEMENT; AMENDMENTS; SEVERABILITY\n\n1. ENTIRE AGREEMENT\nThis Agreement supersedes all prior negotiations, representations, and agreements. Each Party acknowledges that it has not been induced to enter by any representation not set out herein. Nothing excludes liability for fraud.\n\n2. VARIATION\n(a) Written and signed by authorised officers;\n(b) Material variations (scope, price, term >10%) require board approval;\n(c) Variation register to be maintained.\n\n3. WAIVER\nWritten waivers only. No course of dealing constitutes waiver.\n\n4. SEVERABILITY\n(a) Reform to maximum enforceable extent;\n(b) If reformation impossible, sever;\n(c) Remainder continues.\n\n5. THIRD PARTY RIGHTS\nContracts (Rights of Third Parties) Act 1999 excluded.\n\n6. PRECEDENCE\nAmendments > main body > Schedules > SOWs."},

    {"id": "PROFIT_STD_UK001", "clause_type": "profit-sharing-terms", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "PROFIT SHARING AND DISTRIBUTION\n\n1. ALLOCATION\nNet profits and losses shared in the ratio of {{PROFIT_SHARE_RATIO}} in accordance with the Partnership Act 1890.\n\n2. DISTRIBUTIONS\n{{DISTRIBUTION_FREQUENCY}} distributions within {{DISTRIBUTION_DAYS}} days, subject to adequate working capital.\n\n3. CAPITAL CONTRIBUTIONS\nInitial contributions per Schedule A. Additional contributions by unanimous agreement.\n\n4. DRAWINGS\nDrawings up to £{{MAX_DRAW_AMOUNT}} per {{DRAW_PERIOD}} with managing partner approval.\n\n5. ACCOUNTS\nAccounts prepared in accordance with UK GAAP (FRS 102). Annual audit by a registered auditor."},

    {"id": "PROFIT_MOD_UK001", "clause_type": "profit-sharing-terms", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "PROFIT SHARING AND DISTRIBUTION\n\n1. ALLOCATION\nPer {{PROFIT_SHARE_RATIO}}, subject to Partnership Act 1890 default rules where not expressly varied.\n\n2. DISTRIBUTIONS\n(a) {{DISTRIBUTION_FREQUENCY}} within {{DISTRIBUTION_DAYS}} days;\n(b) Minimum reserve of £{{MIN_RESERVE_AMOUNT}};\n(c) Tax distributions for estimated Income Tax and NIC liabilities.\n\n3. CAPITAL\n(a) Separate capital accounts;\n(b) Additional calls: {{CAPITAL_CALL_NOTICE_DAYS}} days' notice, {{CAPITAL_CALL_APPROVAL_THRESHOLD}}% approval;\n(c) Interest at {{CAPITAL_INTEREST_RATE}}% (commercial rate).\n\n4. TAX\nPartnership Tax Return (SA800) filed by the nominated partner. Each partner responsible for own Self-Assessment.\n\n5. REPORTING\nMonthly management accounts within {{MONTHLY_REPORT_DAYS}} days. Annual audit per Companies Act 2006 (if applicable) or Partnership Act 1890."},

    {"id": "PROFIT_STR_UK001", "clause_type": "profit-sharing-terms", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "PROFIT SHARING AND DISTRIBUTION\n\n1. WATERFALL\n(a) Return of capital; (b) Preferred return at {{PREFERRED_RETURN_RATE}}%; (c) Carried interest {{CARRY_PERCENTAGE}}% to Managing Partner; (d) Balance per {{PROFIT_SHARE_RATIO}}.\n\n2. DISTRIBUTION CONTROLS\n(a) {{DISTRIBUTION_FREQUENCY}}, subject to £{{MIN_RESERVE_AMOUNT}} or {{RESERVE_PERCENTAGE}}% reserve;\n(b) No distributions during breach;\n(c) Escrow for disputed amounts.\n\n3. CAPITAL DEFAULT\nFailure within {{CAPITAL_CURE_PERIOD_DAYS}} days: (a) dilution; (b) default interest at {{DEFAULT_INTEREST_RATE}}% (8% above BoE base rate).\n\n4. CLAWBACK\nExcess distributions returned within {{CLAWBACK_PERIOD_DAYS}} days with interest.\n\n5. TAX MATTERS\nSenior Partner files SA800. HMRC enquiry management by nominated tax advisor. Salaried member rules (ITTOIA 2005 s.863A-863G) assessed annually."},

    {"id": "DPA_STD_UK001", "clause_type": "data-processing-obligations", "variant": "Standard", "jurisdiction": "UK", "risk_level": "Low",
     "raw_text": "DATA PROCESSING OBLIGATIONS\n\n1. SCOPE\nProcessor processes Personal Data only on documented instructions from Controller, for the purposes of this Agreement.\n\n2. COMPLIANCE\nProcessor shall comply with: UK GDPR (as retained under EU (Withdrawal) Act 2018) and Data Protection Act 2018.\n\n3. SECURITY\nAppropriate technical and organisational measures per UK GDPR Article 32.\n\n4. BREACH NOTIFICATION\nNotify Controller without undue delay and within {{BREACH_NOTIFICATION_HOURS}} hours of becoming aware.\n\n5. DATA RETURN\nReturn or delete all Personal Data within {{DATA_DELETION_DAYS}} days of termination."},

    {"id": "DPA_MOD_UK001", "clause_type": "data-processing-obligations", "variant": "Moderate", "jurisdiction": "UK", "risk_level": "Medium",
     "raw_text": "DATA PROCESSING OBLIGATIONS\n\n1. PROCESSING\nProcessor acts as \"Processor\" under UK GDPR Article 28. Documented instructions only.\n\n2. COMPLIANCE\nUK GDPR, DPA 2018, and PECR 2003.\n\n3. DPIA\nCooperate with DPIAs per UK GDPR Article 35.\n\n4. SECURITY (ARTICLE 32)\n(a) Cyber Essentials Plus or ISO 27001;\n(b) Encryption (AES-256/TLS 1.2+);\n(c) Annual penetration testing;\n(d) Staff DBS checks and training.\n\n5. BREACH\n(a) Notify within {{BREACH_NOTIFICATION_HOURS}} hours;\n(b) Cooperate with ICO notification (Article 33) within 72 hours.\n\n6. SUB-PROCESSORS\nPrior specific or general authorisation per Article 28(2). {{SUB_PROCESSOR_OBJECTION_DAYS}} days' objection period.\n\n7. INTERNATIONAL TRANSFERS\nNo transfer outside UK without adequate safeguards: UK adequacy regulations, UK International Data Transfer Agreement, or UK Addendum to EU SCCs.\n\n8. AUDIT\n{{AUDIT_NOTICE_DAYS}} days' notice, {{MAX_AUDITS_PER_YEAR}} per year.\n\n9. DELETION\nReturn or delete within {{DATA_DELETION_DAYS}} days with certification."},

    {"id": "DPA_STR_UK001", "clause_type": "data-processing-obligations", "variant": "Strict", "jurisdiction": "UK", "risk_level": "High",
     "raw_text": "DATA PROCESSING OBLIGATIONS\n\n1. CONTROLLER/PROCESSOR\nProcessor under UK GDPR Article 28. No processing outside documented instructions. DPO appointed and notified to Controller.\n\n2. PRIVACY BY DESIGN\nArticle 25 obligations. Processing records per Article 30.\n\n3. SECURITY (ENHANCED)\n(a) ISO 27001 + Cyber Essentials Plus;\n(b) AES-256/TLS 1.3;\n(c) Quarterly penetration testing;\n(d) 24/7 SOC;\n(e) Annual third-party ITHC.\n\n4. BREACH\n(a) {{BREACH_NOTIFICATION_HOURS}} hours notification;\n(b) Full report within {{INCIDENT_REPORT_DAYS}} days;\n(c) Processor bears all ICO notification, compensation, and remediation costs;\n(d) Liquidated damages: £{{BREACH_LIABILITY_AMOUNT}} per incident.\n\n5. SUB-PROCESSORS\n(a) Prior written approval (not general authorisation);\n(b) Full liability for sub-processor acts;\n(c) Mirror obligations verbatim;\n(d) Removal within {{SUB_PROCESSOR_REMOVAL_DAYS}} days.\n\n6. INTERNATIONAL TRANSFERS\nUK IDTA or UK Addendum required. Transfer Impact Assessment per Schrems II/UK equivalent.\n\n7. AUDIT\n(a) {{AUDIT_NOTICE_DAYS}} days' notice;\n(b) Emergency audit post-breach;\n(c) Evidence within {{AUDIT_RESPONSE_DAYS}} days.\n\n8. DELETION\n(a) NCSC-compliant media sanitisation;\n(b) Within {{DATA_DELETION_DAYS}} days;\n(c) Backups purged within {{BACKUP_PURGE_DAYS}} days;\n(d) Third-party certification."},
]


def phase7(session):
    print("\n=== PHASE 7: UK Jurisdiction Clauses ===\n")

    created = 0
    skipped = 0
    for clause in UK_CLAUSES:
        r = session.run("MATCH (c:Clause {id: $id}) RETURN count(*) AS cnt", {"id": clause["id"]})
        if r.single()["cnt"] > 0:
            skipped += 1
            continue

        session.run("""
            CREATE (c:Clause {
                id: $id, clause_type: $clause_type, name: $name,
                variant: $variant, jurisdiction: $jurisdiction,
                risk_level: $risk_level, raw_text: $raw_text
            })
        """, {**clause, "name": f"{clause['clause_type']} — {clause['variant']} (UK)"})

        session.run("""
            MATCH (ct:ClauseType {id: $ct_id}), (c:Clause {id: $c_id})
            CREATE (ct)-[:HAS_VARIANT]->(c)
        """, {"ct_id": clause["clause_type"], "c_id": clause["id"]})

        session.run("""
            MATCH (c:Clause {id: $c_id}), (j:Jurisdiction {id: 'uk'})
            CREATE (c)-[:GOVERNED_BY]->(j)
        """, {"c_id": clause["id"]})

        created += 1

    print(f"  Created {created} clause nodes, skipped {skipped}")

    # CONFLICTS_WITH
    print("\n  Creating UK CONFLICTS_WITH edges...")
    for v1, v2, sev in [("Standard", "Moderate", "medium"), ("Standard", "Strict", "high"), ("Moderate", "Strict", "high")]:
        for a_var, b_var in [(v1, v2), (v2, v1)]:
            result = session.run("""
                MATCH (a:Clause), (b:Clause)
                WHERE a.clause_type = b.clause_type
                  AND a.variant = $a_var AND b.variant = $b_var
                  AND a.jurisdiction = 'UK' AND b.jurisdiction = 'UK'
                  AND NOT (a)-[:CONFLICTS_WITH]->(b)
                CREATE (a)-[:CONFLICTS_WITH {
                    severity: $sev, conflict_type: 'duplication',
                    reason: 'Cannot use both ' + a.variant + ' and ' + b.variant + ' variants of ' + a.clause_type,
                    resolution_advice: 'Choose one variant'
                }]->(b)
                RETURN count(*) AS cnt
            """, {"a_var": a_var, "b_var": b_var, "sev": sev})
            cnt = result.single()["cnt"]
            if cnt > 0:
                print(f"    ✓ {a_var}→{b_var} ({sev}): {cnt}")

    # ALTERNATIVE_TO
    print("\n  Creating UK ALTERNATIVE_TO edges...")
    for v1, v2, alt, strength in [
        ("Standard", "Moderate", "enhanced_protection", "medium"),
        ("Standard", "Strict", "maximum_protection", "low"),
        ("Moderate", "Standard", "simplified", "medium"),
        ("Moderate", "Strict", "enhanced_enforcement", "low"),
        ("Strict", "Moderate", "balanced_approach", "high"),
        ("Strict", "Standard", "simplified", "high"),
    ]:
        result = session.run("""
            MATCH (a:Clause), (b:Clause)
            WHERE a.clause_type = b.clause_type
              AND a.variant = $v1 AND b.variant = $v2
              AND a.jurisdiction = 'UK' AND b.jurisdiction = 'UK'
              AND NOT (a)-[:ALTERNATIVE_TO]->(b)
            CREATE (a)-[:ALTERNATIVE_TO {
                alternative_type: $alt,
                recommendation_strength: $strength,
                reason: $v2 + ' variant offers an alternative under English law',
                benefit: 'Alternative ' + $v2 + ' protection level'
            }]->(b)
            RETURN count(*) AS cnt
        """, {"v1": v1, "v2": v2, "alt": alt, "strength": strength})
        cnt = result.single()["cnt"]
        if cnt > 0:
            print(f"    ✓ {v1}→{v2}: {cnt}")

    # CONTAINS_PARAM (reuse India params)
    print("\n  Wiring UK CONTAINS_PARAM edges...")
    r = session.run("""
        MATCH (c:Clause)-[:CONTAINS_PARAM]->(p:Parameter)
        WHERE c.jurisdiction = 'India'
        RETURN c.clause_type AS ct, c.variant AS v, collect(p.id) AS pids
    """)
    india_params = {}
    for rec in r:
        india_params[(rec["ct"], rec["v"])] = rec["pids"]

    param_ct = 0
    for clause in UK_CLAUSES:
        key = (clause["clause_type"], clause["variant"])
        if key in india_params:
            for pid in india_params[key]:
                session.run("""
                    MATCH (c:Clause {id: $cid}), (p:Parameter {id: $pid})
                    WHERE NOT (c)-[:CONTAINS_PARAM]->(p)
                    CREATE (c)-[:CONTAINS_PARAM]->(p)
                """, {"cid": clause["id"], "pid": pid})
                param_ct += 1
    print(f"    ✓ {param_ct} CONTAINS_PARAM edges")

    print("\n✅ Phase 7 complete!")


if __name__ == "__main__":
    with driver.session() as session:
        phase7(session)
    driver.close()
