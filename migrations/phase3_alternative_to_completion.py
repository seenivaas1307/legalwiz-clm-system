"""
Phase 3: Complete ALTERNATIVE_TO Graph
- Add missing upgrade paths: Standard→Strict and Moderate→Strict (40 new edges)
- Replace all templated reasons on existing 80 + new 40 edges with clause-specific legal reasoning
"""

from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)


def phase3(session):
    print("\n=== PHASE 3: ALTERNATIVE_TO Completion + Clause-Specific Reasoning ===\n")

    # -----------------------------------------------------------------------
    # 3a. Add missing upgrade paths: Standard → Strict, Moderate → Strict
    # -----------------------------------------------------------------------
    print("[3a] Adding Standard→Strict and Moderate→Strict upgrade paths...\n")

    # Check what already exists
    r = session.run("""
        MATCH (a:Clause)-[:ALTERNATIVE_TO]->(b:Clause)
        WHERE a.variant = 'Standard' AND b.variant = 'Strict'
        RETURN count(*) AS cnt
    """)
    std_strict_count = r.single()["cnt"]

    r = session.run("""
        MATCH (a:Clause)-[:ALTERNATIVE_TO]->(b:Clause)
        WHERE a.variant = 'Moderate' AND b.variant = 'Strict'
        RETURN count(*) AS cnt
    """)
    mod_strict_count = r.single()["cnt"]

    if std_strict_count == 0:
        session.run("""
            MATCH (std:Clause), (strict:Clause)
            WHERE std.clause_type = strict.clause_type
              AND std.variant = 'Standard' AND strict.variant = 'Strict'
              AND std.jurisdiction = strict.jurisdiction
            CREATE (std)-[:ALTERNATIVE_TO {
                alternative_type: 'maximum_protection',
                recommendation_strength: 'low',
                reason: 'Strict variant provides maximum contractual protection for high-value engagements',
                benefit: 'Maximum legal protection with detailed enforcement mechanisms'
            }]->(strict)
        """)
        print("  ✓ Added Standard→Strict paths (20 edges)")
    else:
        print(f"  ⏭ Standard→Strict already exists ({std_strict_count} edges)")

    if mod_strict_count == 0:
        session.run("""
            MATCH (mod:Clause), (strict:Clause)
            WHERE mod.clause_type = strict.clause_type
              AND mod.variant = 'Moderate' AND strict.variant = 'Strict'
              AND mod.jurisdiction = strict.jurisdiction
            CREATE (mod)-[:ALTERNATIVE_TO {
                alternative_type: 'enhanced_enforcement',
                recommendation_strength: 'low',
                reason: 'Strict variant adds detailed enforcement mechanisms and expanded protective scope',
                benefit: 'Stronger legal position in disputes with comprehensive remedy provisions'
            }]->(strict)
        """)
        print("  ✓ Added Moderate→Strict paths (20 edges)")
    else:
        print(f"  ⏭ Moderate→Strict already exists ({mod_strict_count} edges)")

    # -----------------------------------------------------------------------
    # 3b. Replace templated reasons with clause-specific legal reasoning
    # -----------------------------------------------------------------------
    print("\n[3b] Updating ALTERNATIVE_TO edges with clause-specific reasoning...\n")

    # Each entry: (from_id, to_id, reason, benefit)
    # Covering all 6 direction pairs × 20 clause types where meaningful
    clause_specific_reasons = [
        # ===== CONFIDENTIALITY =====
        ("CONF_STD_001", "CONF_MOD_001",
         "Moderate Confidentiality adds defined information categories, bilateral obligations, and multi-year survival period — essential when sharing proprietary data with vendors or partners.",
         "Broader protection scope with explicit carve-outs for permitted disclosures."),
        ("CONF_STD_001", "CONF_STR_001",
         "Strict Confidentiality imposes lifetime obligations, broad injunctive relief, and return/destruction certification — appropriate only for trade-secret-heavy engagements where the cost of disclosure is catastrophic.",
         "Maximum information protection with court-enforceable injunctive remedies."),
        ("CONF_MOD_001", "CONF_STD_001",
         "Standard Confidentiality is lighter-weight, suitable for low-risk engagements where minimal proprietary information is exchanged.",
         "Simpler compliance burden for routine commercial relationships."),
        ("CONF_MOD_001", "CONF_STR_001",
         "Strict Confidentiality adds permanent obligations and injunctive relief provisions — warranted when trade secrets or highly sensitive data is involved.",
         "Irrevocable protection for critical trade secrets with court-enforceable remedies."),
        ("CONF_STR_001", "CONF_MOD_001",
         "Strict Confidentiality with lifetime obligations and broad injunctive relief may be disproportionate and harder to enforce in Indian courts; Moderate offers better enforceability.",
         "Better enforceability with reasonable time-bound obligations that courts are more likely to uphold."),
        ("CONF_STR_001", "CONF_STD_001",
         "Standard Confidentiality removes enforcement complexity suitable for low-risk or short-term engagements where lifetime obligations are commercially unnecessary.",
         "Minimal administrative overhead with adequate protection for non-sensitive information."),

        # ===== PAYMENT TERMS =====
        ("PAY_STD_001", "PAY_MOD_001",
         "Moderate Payment Terms adds late payment interest, TDS compliance provisions, and expense reimbursement mechanisms required for Indian B2B contracts.",
         "Tax-compliant payment structure with incentive mechanisms for timely payment."),
        ("PAY_STD_001", "PAY_STR_001",
         "Strict Payment Terms introduces milestone-based billing, escrow provisions, and graduated late-payment penalties — essential for high-value project-based contracts.",
         "Complete payment governance with escrow-backed milestone verification."),
        ("PAY_MOD_001", "PAY_STD_001",
         "Standard Payment Terms is lighter and suitable for routine procurement where detailed tax and reimbursement mechanisms add unnecessary complexity.",
         "Simplified invoicing with basic payment timelines."),
        ("PAY_MOD_001", "PAY_STR_001",
         "Strict Payment Terms adds escrow, milestone-based release, and performance-linked payments — justified for engagements exceeding ₹50 lakhs.",
         "Full financial control with escrow and milestone-linked disbursements."),
        ("PAY_STR_001", "PAY_MOD_001",
         "Strict Payment Terms with escrow and milestone gates may be operationally heavy for mid-range contracts; Moderate provides adequate payment governance.",
         "Pragmatic payment controls without escrow administration costs."),
        ("PAY_STR_001", "PAY_STD_001",
         "Standard Payment Terms is appropriate when contract value and risk profile do not justify milestone-based controls or escrow.",
         "Minimal payment administration for low-value engagements."),

        # ===== SCOPE OF AGREEMENT =====
        ("SCOP_STD_001", "SCOP_MOD_001",
         "Moderate Scope adds formal SOW framework, acceptance testing procedures, and change order process — essential for any engagement with defined deliverables.",
         "Structured engagement framework reducing scope creep and acceptance disputes."),
        ("SCOP_STD_001", "SCOP_STR_001",
         "Strict Scope introduces SLA measurement, geographic scope restrictions, resolution targets, and severity-level-based response times — suited for mission-critical service agreements.",
         "Comprehensive service-level governance with measurable performance criteria."),
        ("SCOP_MOD_001", "SCOP_STD_001",
         "Standard Scope is adequate for engagements where deliverables are few and formal acceptance testing would add unnecessary process overhead.",
         "Lean scope definition for straightforward service engagements."),
        ("SCOP_MOD_001", "SCOP_STR_001",
         "Strict Scope adds SLA-driven performance measurement and detailed technical scope boundaries — appropriate for enterprise SaaS or managed service contracts.",
         "Performance-driven scope management with contractual SLA enforcement."),
        ("SCOP_STR_001", "SCOP_MOD_001",
         "Strict Scope with detailed SLAs, severity levels, and response matrices may be excessive for standard consulting or vendor agreements.",
         "Appropriate scope governance without SLA administration overhead."),
        ("SCOP_STR_001", "SCOP_STD_001",
         "Standard Scope provides basic service description adequate for low-complexity, fixed-scope engagements.",
         "Minimal scope definition for well-understood, low-risk service arrangements."),

        # ===== TERM AND RENEWAL =====
        ("TERM_STD_001", "TERM_MOD_001",
         "Moderate Term adds structured auto-renewal with price adjustment mechanism and renewal deadlines — critical for SaaS and vendor agreements to avoid unintended lock-in.",
         "Controlled renewal process preventing unintended perpetual commitments."),
        ("TERM_STD_001", "TERM_STR_001",
         "Strict Term introduces minimum commitments, holdover rate multipliers, and detailed renewal acceptance windows — appropriate for enterprise contracts with significant switching costs.",
         "Complete contract lifecycle control with holdover protections."),
        ("TERM_MOD_001", "TERM_STD_001",
         "Standard Term's simple notice-period model is adequate for engagements where auto-renewal complexity is not justified.",
         "Straightforward term with basic renewal by mutual agreement."),
        ("TERM_MOD_001", "TERM_STR_001",
         "Strict Term adds holdover penalties and minimum commitment periods — warranted when early termination would cause significant operational disruption.",
         "Maximum contract stability with financial deterrents against unplanned termination."),
        ("TERM_STR_001", "TERM_MOD_001",
         "Strict Term's holdover penalties and minimum commitments may create commercially unreasonable lock-in; Moderate provides balanced renewal governance.",
         "Balanced renewal controls without excessive lock-in provisions."),
        ("TERM_STR_001", "TERM_STD_001",
         "Standard Term provides flexibility for short-term or project-based engagements where long-term commitment is unnecessary.",
         "Maximum flexibility with mutual termination and simple renewal."),

        # ===== INDEMNIFICATION =====
        ("INDEM_STD_001", "INDEM_MOD_001",
         "Moderate Indemnification adds IP infringement and data breach specific indemnity triggers, bilateral obligations, and defence/settlement control mechanisms.",
         "Comprehensive risk allocation covering both IP and data protection scenarios."),
        ("INDEM_STD_001", "INDEM_STR_001",
         "Strict Indemnification extends to consequential damages, adds first-dollar indemnity with no basket/threshold, and includes IP ownership representation indemnity.",
         "Maximum risk transfer with no deductible and full consequential damage coverage."),
        ("INDEM_MOD_001", "INDEM_STD_001",
         "Standard Indemnification is appropriate for low-risk engagements where IP and data breach-specific triggers add unnecessary complexity.",
         "Basic indemnity coverage adequate for routine commercial relationships."),
        ("INDEM_MOD_001", "INDEM_STR_001",
         "Strict Indemnification adds consequential damage coverage and removes indemnity thresholds — justified for contracts with significant potential third-party exposure.",
         "First-dollar coverage with consequential damage protection for high-risk engagements."),
        ("INDEM_STR_001", "INDEM_MOD_001",
         "Strict Indemnification's first-dollar, unlimited consequential damage coverage may be commercially unacceptable to counterparties and disproportionate for mid-range deals.",
         "Commercially reasonable indemnity with defined triggers and proportionate coverage."),
        ("INDEM_STR_001", "INDEM_STD_001",
         "Standard Indemnification provides basic third-party claim coverage adequate when exposure is limited and both parties carry adequate insurance.",
         "Streamlined indemnity relying on insurance coverage for excess risk."),

        # ===== IP OWNERSHIP =====
        ("IP_STD_001", "IP_MOD_001",
         "Moderate IP Ownership adds explicit background/foreground IP distinction, pre-existing IP carve-outs, and joint IP handling — critical when both parties contribute IP.",
         "Clear IP ownership boundaries preventing disputes over who owns what after engagement ends."),
        ("IP_STD_001", "IP_STR_001",
         "Strict IP Ownership introduces moral rights waivers, invention assignment with adequate consideration, and work-made-for-hire provisions across jurisdictions.",
         "Airtight IP assignment suitable for R&D partnerships or strategic technology development."),
        ("IP_MOD_001", "IP_STD_001",
         "Standard IP Ownership is adequate when the engagement produces minimal new IP and both parties retain their existing portfolios.",
         "Simple IP assignment for engagements with limited intellectual property creation."),
        ("IP_MOD_001", "IP_STR_001",
         "Strict IP Ownership adds moral rights waivers and consideration-backed invention assignment — necessary for engagements where the commissioned IP is strategically valuable.",
         "Complete IP protection with jurisdiction-aware assignment and moral rights provisions."),
        ("IP_STR_001", "IP_MOD_001",
         "Strict IP Ownership's moral rights waivers and broad assignment may face resistance from counterparties and enforceability challenges in certain jurisdictions.",
         "Practical IP governance that balances both parties' pre-existing portfolios."),
        ("IP_STR_001", "IP_STD_001",
         "Standard IP Ownership provides basic assignment suitable when IP creation is incidental to the primary engagement.",
         "Lean IP provisions for engagements where IP is not the primary deliverable."),

        # ===== LIMITATION OF LIABILITY =====
        ("LIAB_STD_001", "LIAB_MOD_001",
         "Moderate Liability Limitation adds annual contract value multiplier cap, carved-out super-liability categories, and data breach sub-limits.",
         "Balanced cap structure that protects against catastrophic loss while maintaining commercial viability."),
        ("LIAB_STD_001", "LIAB_STR_001",
         "Strict Liability Limitation introduces per-incident caps, uncapped categories (gross negligence, wilful misconduct), and insurance adequacy requirements.",
         "Granular liability governance with per-incident and per-annum controls."),
        ("LIAB_MOD_001", "LIAB_STD_001",
         "Standard Liability Limitation is appropriate for low-risk engagements where category-specific caps add unnecessary negotiation complexity.",
         "Simple aggregate cap for routine commercial relationships."),
        ("LIAB_MOD_001", "LIAB_STR_001",
         "Strict Liability adds per-incident limits and uncapped carve-outs for egregious conduct — warranted for mission-critical services.",
         "Per-incident accountability with insurance-backed protection."),
        ("LIAB_STR_001", "LIAB_MOD_001",
         "Strict Liability's granular per-incident caps and uncapped categories may be commercially onerous; Moderate provides adequate risk allocation.",
         "Commercially reasonable caps with defined super-liability carve-outs."),
        ("LIAB_STR_001", "LIAB_STD_001",
         "Standard Liability provides a simple aggregate cap suitable when the risk profile does not justify per-incident controls.",
         "Simple, negotiation-friendly liability cap for standard engagements."),

        # ===== REPRESENTATIONS AND WARRANTIES =====
        ("WARR_STD_001", "WARR_MOD_001",
         "Moderate Warranties adds operation-specific representations (regulatory compliance, financial solvency, no pending litigation) extending beyond basic authority and performance warranties.",
         "Comprehensive representations covering regulatory and financial risks."),
        ("WARR_STD_001", "WARR_STR_001",
         "Strict Warranties introduces ongoing disclosure obligations, annual compliance certifications, and materiality-qualified remediation with liquidated damages for breach.",
         "Maximum warranty coverage with continuous compliance monitoring."),
        ("WARR_MOD_001", "WARR_STD_001",
         "Standard Warranties are adequate for routine engagements where regulatory and financial solvency representations are unnecessary.",
         "Basic authority and performance warranties for low-risk relationships."),
        ("WARR_MOD_001", "WARR_STR_001",
         "Strict Warranties adds ongoing certification and liquidated damages for misrepresentation — appropriate for highly regulated sectors.",
         "Continuous compliance assurance with financial consequences for breach."),
        ("WARR_STR_001", "WARR_MOD_001",
         "Strict Warranties' ongoing certifications and liquidated damages may be administratively burdensome and face pushback from counterparties.",
         "Proportionate warranty coverage without continuous certification overhead."),
        ("WARR_STR_001", "WARR_STD_001",
         "Standard Warranties provide adequate protection for engagements where the counterparty's regulatory compliance is not a primary concern.",
         "Lean warranty provisions for standard commercial arrangements."),

        # ===== FORCE MAJEURE =====
        ("FM_STD_001", "FM_MOD_001",
         "Moderate Force Majeure adds pandemic and cyber-attack as enumerated events, mitigation obligations, alternative performance duty, and termination trigger threshold.",
         "Post-COVID appropriate protection covering modern disruption scenarios including cyber events."),
        ("FM_STD_001", "FM_STR_001",
         "Strict Force Majeure introduces business continuity plan requirements, insurance adequacy verification, and tiered suspension with escalating cure obligations.",
         "Maximum operational resilience with mandatory BCP and insurance verification."),
        ("FM_MOD_001", "FM_STD_001",
         "Standard Force Majeure is adequate for engagements where pandemic/cyber enumeration and mitigation obligations add unnecessary complexity.",
         "Traditional FM protection with standard excuse-of-performance provisions."),
        ("FM_MOD_001", "FM_STR_001",
         "Strict Force Majeure adds BCP mandates and insurance verification — appropriate for critical infrastructure or high-availability services.",
         "Proactive resilience requirements preventing FM events before they occur."),
        ("FM_STR_001", "FM_MOD_001",
         "Strict Force Majeure's BCP and insurance requirements may be excessive for mid-range contracts; Moderate provides adequate pandemic/cyber protection.",
         "Proportionate FM protection covering modern events without administrative burden."),
        ("FM_STR_001", "FM_STD_001",
         "Standard Force Majeure provides essential excuse-of-performance for acts of God, suitable for low-criticality engagements.",
         "Basic FM coverage for standard commercial arrangements."),

        # ===== TERMINATION FOR CAUSE =====
        ("TERMB_STD_001", "TERMB_MOD_001",
         "Moderate Termination for Cause adds graduated cure periods, SLA failure thresholds, and cumulative breach triggers — more nuanced than simple 30-day cure.",
         "Proportionate termination rights preventing premature contract exit for minor issues."),
        ("TERMB_STD_001", "TERMB_STR_001",
         "Strict Termination for Cause introduces automatic termination triggers, reinstatement fees, and vendor-specific cure periods — suited for service-critical agreements.",
         "Zero-tolerance enforcement for material breaches with automatic trigger mechanisms."),
        ("TERMB_MOD_001", "TERMB_STD_001",
         "Standard Termination for Cause with a simple cure period is adequate for engagements where SLA metrics and cumulative failures are not applicable.",
         "Simple breach-and-cure model for straightforward commercial relationships."),
        ("TERMB_MOD_001", "TERMB_STR_001",
         "Strict Termination for Cause adds automatic triggers and reinstatement fees — warranted for SaaS/managed services with strict availability requirements.",
         "Automatic enforcement ensuring service continuity without manual intervention."),
        ("TERMB_STR_001", "TERMB_MOD_001",
         "Strict Termination for Cause's automatic triggers and reinstatement fees may create adversarial dynamics; Moderate provides proportionate enforcement.",
         "Graduated enforcement that preserves the commercial relationship during remediation."),
        ("TERMB_STR_001", "TERMB_STD_001",
         "Standard Termination for Cause provides basic breach remediation for engagements where automatic triggers would be disproportionate.",
         "Basic cure-period model suitable for non-critical service arrangements."),

        # ===== TERMINATION FOR CONVENIENCE =====
        ("TERMC_STD_001", "TERMC_MOD_001",
         "Moderate Termination for Convenience adds transition assistance obligations, WIP payment protections, and structured wind-down timelines.",
         "Orderly exit process protecting both parties' interests during transition."),
        ("TERMC_STD_001", "TERMC_STR_001",
         "Strict Termination for Convenience introduces early termination fees, minimum commitment enforcement, and detailed transition assistance rates.",
         "Full exit cost governance preventing opportunistic convenience terminations."),
        ("TERMC_MOD_001", "TERMC_STD_001",
         "Standard Termination for Convenience with simple notice is adequate for engagements where WIP protection and transition assistance are not significant concerns.",
         "Maximum exit flexibility with minimal procedural requirements."),
        ("TERMC_MOD_001", "TERMC_STR_001",
         "Strict Termination for Convenience adds early termination penalties and detailed transition assistance — appropriate when premature exit would cause significant operational disruption.",
         "Financial deterrent against opportunistic termination with comprehensive transition support."),
        ("TERMC_STR_001", "TERMC_MOD_001",
         "Strict Termination for Convenience's early termination fees and minimum commitments may be commercially unreasonable for shorter engagements.",
         "Balanced exit provisions with transition support but without punitive fees."),
        ("TERMC_STR_001", "TERMC_STD_001",
         "Standard Termination for Convenience provides maximum flexibility, appropriate for short-term or project-based contracts.",
         "Simple notice-period exit for low-commitment arrangements."),

        # ===== EFFECT OF TERMINATION AND SURVIVAL =====
        ("SURV_STD_001", "SURV_MOD_001",
         "Moderate Effect of Termination adds transition assistance obligations, data return timelines, and accrued rights preservation.",
         "Orderly wind-down process protecting both parties during transition period."),
        ("SURV_STD_001", "SURV_STR_001",
         "Strict Effect of Termination introduces mandatory knowledge transfer, detailed data deletion certification, and extended survival for key obligations.",
         "Comprehensive post-termination governance with verifiable data handling."),
        ("SURV_MOD_001", "SURV_STD_001",
         "Standard Effect of Termination provides basic survival provisions adequate for engagements with minimal post-termination obligations.",
         "Simple survival clause for low-complexity arrangements."),
        ("SURV_MOD_001", "SURV_STR_001",
         "Strict Effect of Termination adds knowledge transfer mandates and data deletion certification — essential for data-heavy engagements.",
         "Auditable post-termination data handling with mandatory knowledge transfer."),
        ("SURV_STR_001", "SURV_MOD_001",
         "Strict Effect of Termination's knowledge transfer and deletion certification may be excessive for routine engagements.",
         "Practical wind-down with data return timelines and accrued rights preservation."),
        ("SURV_STR_001", "SURV_STD_001",
         "Standard Effect of Termination provides basic survival provisions appropriate when post-termination complexity is low.",
         "Minimal post-termination obligations for straightforward exit scenarios."),

        # ===== GOVERNING LAW =====
        ("GOV_STD_001", "GOV_MOD_001",
         "Moderate Governing Law adds institutional arbitration as primary dispute mechanism, specific seat and venue selection, and provisional remedies carve-out.",
         "Faster, private dispute resolution through arbitration rather than protracted court litigation."),
        ("GOV_STD_001", "GOV_STR_001",
         "Strict Governing Law introduces multi-jurisdictional choice-of-law provisions, arbitration panel selection criteria, and appellate review carve-outs.",
         "International dispute governance with sophisticated arbitration panel selection."),
        ("GOV_MOD_001", "GOV_STD_001",
         "Standard Governing Law with court jurisdiction is adequate for purely domestic engagements where arbitration is unnecessary.",
         "Straightforward court-based dispute resolution for domestic contracts."),
        ("GOV_MOD_001", "GOV_STR_001",
         "Strict Governing Law adds panel selection criteria and appellate provisions — justified for complex cross-border or high-value disputes.",
         "Complete dispute governance with institutional arbitration safeguards."),
        ("GOV_STR_001", "GOV_MOD_001",
         "Strict Governing Law's multi-jurisdictional provisions and panel selection criteria may be unnecessary for domestic Indian contracts.",
         "Efficient institutional arbitration without multi-jurisdictional complexity."),
        ("GOV_STR_001", "GOV_STD_001",
         "Standard Governing Law provides simple Indian court jurisdiction adequate for low-value domestic contracts.",
         "Simple and cost-effective court-based dispute resolution."),

        # ===== DISPUTE RESOLUTION =====
        ("DISP_STD_001", "DISP_MOD_001",
         "Moderate Dispute Resolution adds multi-tier escalation (negotiation → mediation → arbitration) with defined timelines for each stage.",
         "Structured de-escalation process that resolves most disputes before arbitration costs are incurred."),
        ("DISP_STD_001", "DISP_STR_001",
         "Strict Dispute Resolution introduces emergency arbitrator provisions, interim relief mechanics, and detailed cost-allocation rules.",
         "Maximum procedural protection with emergency relief and detailed cost management."),
        ("DISP_MOD_001", "DISP_STD_001",
         "Standard Dispute Resolution is adequate for engagements where multi-tier escalation would add unnecessary process delay.",
         "Direct access to dispute resolution without mandatory escalation stages."),
        ("DISP_MOD_001", "DISP_STR_001",
         "Strict Dispute Resolution adds emergency arbitrator and interim relief — appropriate for time-sensitive commercial disputes.",
         "Rapid interim relief availability without waiting for full arbitration panel constitution."),
        ("DISP_STR_001", "DISP_MOD_001",
         "Strict Dispute Resolution's emergency arbitrator provisions and detailed cost rules add complexity that may be unnecessary for most commercial disputes.",
         "Proportionate dispute resolution with structured escalation."),
        ("DISP_STR_001", "DISP_STD_001",
         "Standard Dispute Resolution provides basic resolution mechanisms adequate for low-risk commercial arrangements.",
         "Simple dispute resolution for straightforward engagements."),

        # ===== NON-COMPETE =====
        ("NONCOMP_STD_001", "NONCOMP_MOD_001",
         "Moderate Non-Compete adds reasonable time (12 months) and geographic limitations that are more likely to be enforced by Indian courts under Section 27 of the Indian Contract Act.",
         "Better enforceability with court-friendly temporal and geographic restrictions."),
        ("NONCOMP_STD_001", "NONCOMP_STR_001",
         "Strict Non-Compete introduces broad industry exclusion, liquidated damages, and extended restriction periods — high enforceability risk under Indian law.",
         "Maximum competitive protection (note: enforceability concerns under Section 27)."),
        ("NONCOMP_MOD_001", "NONCOMP_STD_001",
         "Standard Non-Compete provides basic restrictions suitable for engagements where competitive risk is low.",
         "Light-touch competitive restriction for routine commercial arrangements."),
        ("NONCOMP_MOD_001", "NONCOMP_STR_001",
         "Strict Non-Compete's broad scope and liquidated damages face significant enforceability risk under Indian law; use only where competitive threat is existential.",
         "Maximum protection (with acknowledged enforceability limitations)."),
        ("NONCOMP_STR_001", "NONCOMP_MOD_001",
         "Strict Non-Compete may be void under Section 27 of the Indian Contract Act, 1872. Moderate variant acknowledges this limitation while still protecting trade secrets through reasonable restrictions.",
         "Enforceable protection that balances employer interests with employee rights under Indian law."),
        ("NONCOMP_STR_001", "NONCOMP_STD_001",
         "Standard Non-Compete provides basic protection adequate when Section 27 concerns outweigh the need for strict competitive restrictions.",
         "Minimal restraint-of-trade risk with basic competitive boundaries."),

        # ===== NON-SOLICITATION =====
        ("NONSOL_STD_001", "NONSOL_MOD_001",
         "Moderate Non-Solicitation adds specific employee categories, client/prospect protection, and reasonable lookback periods.",
         "Targeted protection covering both employee and client solicitation risks."),
        ("NONSOL_STD_001", "NONSOL_STR_001",
         "Strict Non-Solicitation introduces liquidated damages, broad lookback periods, and indirect solicitation prohibitions.",
         "Comprehensive solicitation protection with financial consequences for breach."),
        ("NONSOL_MOD_001", "NONSOL_STD_001",
         "Standard Non-Solicitation provides basic employee/client protection adequate for routine commercial relationships.",
         "Simple solicitation restriction for low-risk engagements."),
        ("NONSOL_MOD_001", "NONSOL_STR_001",
         "Strict Non-Solicitation's broad lookback and liquidated damages are warranted when losing key employees or clients would be existentially damaging.",
         "Maximum solicitation deterrent with pre-agreed financial consequences."),
        ("NONSOL_STR_001", "NONSOL_MOD_001",
         "Strict Non-Solicitation with broad lookback and liquidated damages may face enforceability challenges under Section 27 of the Indian Contract Act.",
         "Enforceable protection with reasonable temporal and scope restrictions that Indian courts are likely to uphold."),
        ("NONSOL_STR_001", "NONSOL_STD_001",
         "Standard Non-Solicitation provides adequate protection when broad indirect-solicitation prohibitions are commercially unnecessary.",
         "Basic solicitation boundaries for standard engagements."),

        # ===== NON-DISCLOSURE (EMPLOYMENT) =====
        ("NDISC_STD_001", "NDISC_MOD_001",
         "Moderate Non-Disclosure adds specific information categories, return obligations, and bilateral confidentiality where applicable.",
         "Categorized information protection with defined handling procedures."),
        ("NDISC_STD_001", "NDISC_STR_001",
         "Strict Non-Disclosure introduces lifetime obligations, injunctive relief provisions, and mandatory security controls.",
         "Maximum information security with court-enforceable remedies and technical controls."),
        ("NDISC_MOD_001", "NDISC_STD_001",
         "Standard Non-Disclosure is adequate for routine employment relationships with minimal sensitive information exposure.",
         "Basic confidentiality for standard employment arrangements."),
        ("NDISC_MOD_001", "NDISC_STR_001",
         "Strict Non-Disclosure adds lifetime obligations and mandatory security controls — appropriate for employees with access to critical trade secrets.",
         "Permanent protection with enforceable security requirements."),
        ("NDISC_STR_001", "NDISC_MOD_001",
         "Strict Non-Disclosure's lifetime obligations and broad injunctive relief may be disproportionate for standard employment roles.",
         "Proportionate information protection with time-bound obligations."),
        ("NDISC_STR_001", "NDISC_STD_001",
         "Standard Non-Disclosure provides basic employee confidentiality adequate when trade secret exposure is limited.",
         "Simple confidentiality for routine employment relationships."),

        # ===== DEFINITIONS =====
        ("DEFN_STD_001", "DEFN_MOD_001",
         "Moderate Definitions adds comprehensive term coverage for financial, operational, and regulatory terms — essential for complex agreements.",
         "Reduced ambiguity through exhaustive term definitions."),
        ("DEFN_STD_001", "DEFN_STR_001",
         "Strict Definitions introduces cross-referenced definitions, hierarchical interpretation rules, and defined terminology for all capitalized terms.",
         "Maximum interpretive clarity with cross-referenced and hierarchical definitions."),
        ("DEFN_MOD_001", "DEFN_STD_001",
         "Standard Definitions is adequate for simple agreements where only core terms need definition.",
         "Lean definitions for straightforward commercial arrangements."),
        ("DEFN_MOD_001", "DEFN_STR_001",
         "Strict Definitions adds interpretation hierarchies and cross-referencing — appropriate for complex multi-party or regulated agreements.",
         "Comprehensive interpretive framework preventing definitional disputes."),
        ("DEFN_STR_001", "DEFN_MOD_001",
         "Strict Definitions' hierarchical interpretation rules may be unnecessarily complex for standard agreements.",
         "Adequate term coverage without interpretive complexity."),
        ("DEFN_STR_001", "DEFN_STD_001",
         "Standard Definitions provides basic term coverage suitable for simple, low-risk agreements.",
         "Minimal definitions for simple contractual arrangements."),

        # ===== PARTIES AND RECITALS =====
        ("PART_STD_001", "PART_MOD_001",
         "Moderate Parties and Recitals adds detailed entity identification, registration verification, and authorized signatory provisions.",
         "Enhanced party verification reducing identity and authority disputes."),
        ("PART_STD_001", "PART_STR_001",
         "Strict Parties and Recitals introduces KYC verification, beneficial ownership disclosure, and anti-corruption representations.",
         "Maximum counterparty due diligence with compliance-grade verification."),
        ("PART_MOD_001", "PART_STD_001",
         "Standard Parties and Recitals is adequate for known counterparties where detailed entity verification is unnecessary.",
         "Simple party identification for established relationships."),
        ("PART_MOD_001", "PART_STR_001",
         "Strict Parties adds KYC and beneficial ownership — essential for regulated industries or engagements with new counterparties.",
         "Compliance-grade counterparty verification mitigating regulatory risk."),
        ("PART_STR_001", "PART_MOD_001",
         "Strict Parties' KYC and beneficial ownership requirements may be disproportionate for established, trusted counterparties.",
         "Practical party identification without compliance-heavy KYC procedures."),
        ("PART_STR_001", "PART_STD_001",
         "Standard Parties provides basic identification adequate for routine engagements between known entities.",
         "Minimal party identification for low-risk, established relationships."),

        # ===== ENTIRE AGREEMENT =====
        ("ENTIRE_STD_001", "ENTIRE_MOD_001",
         "Moderate Entire Agreement adds amendment tracking procedures, specific severability provisions, and conflict-of-terms resolution hierarchy.",
         "Structured amendment process preventing informal modifications."),
        ("ENTIRE_STD_001", "ENTIRE_STR_001",
         "Strict Entire Agreement introduces formal amendment registers, board approval requirements for material changes, and detailed precedence hierarchies.",
         "Maximum contractual integrity with governance-grade amendment controls."),
        ("ENTIRE_MOD_001", "ENTIRE_STD_001",
         "Standard Entire Agreement is adequate for simple contracts where formal amendment registers are unnecessary.",
         "Basic merger clause for straightforward agreements."),
        ("ENTIRE_MOD_001", "ENTIRE_STR_001",
         "Strict Entire Agreement adds board-level approval and amendment registers — appropriate for high-value or regulated agreements.",
         "Governance-grade amendment control with complete audit trail."),
        ("ENTIRE_STR_001", "ENTIRE_MOD_001",
         "Strict Entire Agreement's board approval and amendment registers may be excessive for mid-range agreements.",
         "Practical amendment tracking without governance-heavy approval processes."),
        ("ENTIRE_STR_001", "ENTIRE_STD_001",
         "Standard Entire Agreement provides basic merger and severability provisions for simple arrangements.",
         "Lean boilerplate adequate for routine commercial contracts."),
    ]

    updated = 0
    created = 0
    for from_id, to_id, reason, benefit in clause_specific_reasons:
        # Try to update existing edge first
        r = session.run("""
            MATCH (a:Clause {id: $from_id})-[r:ALTERNATIVE_TO]->(b:Clause {id: $to_id})
            RETURN count(*) AS cnt
        """, {"from_id": from_id, "to_id": to_id})

        if r.single()["cnt"] > 0:
            session.run("""
                MATCH (a:Clause {id: $from_id})-[r:ALTERNATIVE_TO]->(b:Clause {id: $to_id})
                SET r.reason = $reason, r.benefit = $benefit
            """, {"from_id": from_id, "to_id": to_id, "reason": reason, "benefit": benefit})
            updated += 1
        else:
            print(f"  ⚠ No edge found: {from_id} → {to_id} (skipping reason update)")

    print(f"\n✅ Phase 3 complete! Updated {updated} ALTERNATIVE_TO edges with clause-specific reasoning.")


if __name__ == "__main__":
    with driver.session() as session:
        phase3(session)
    driver.close()
