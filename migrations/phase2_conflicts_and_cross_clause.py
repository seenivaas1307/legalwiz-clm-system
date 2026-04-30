"""
Phase 2: Complete CONFLICTS_WITH Coverage
- Variant-pair conflicts already exist (120 edges). No action needed.
- Add cross-clause semantic conflicts (legally meaningful cross-type conflicts).
"""

from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

CROSS_CLAUSE_CONFLICTS = [
    # Non-Compete/Strict × Indian Governing Law — Section 27 enforceability risk
    {
        "from_id": "NONCOMP_STR_001",
        "to_id": "GOV_STD_001",
        "severity": "high",
        "conflict_type": "legal_enforceability",
        "reason": (
            "Strict non-compete may be unenforceable under Section 27 of the Indian Contract Act, 1872, "
            "which renders agreements in restraint of trade void. Combined with Indian governing law, "
            "this clause carries significant litigation risk."
        ),
        "resolution_advice": (
            "Use Moderate non-compete variant which explicitly acknowledges Section 27 limitations, "
            "or add a carve-out for post-employment trade secret protection."
        ),
    },
    # Non-Compete/Strict × Indian Governing Law (Moderate) — same Section 27 issue
    {
        "from_id": "NONCOMP_STR_001",
        "to_id": "GOV_MOD_001",
        "severity": "medium",
        "conflict_type": "legal_enforceability",
        "reason": (
            "Strict non-compete restrictions face enforceability challenges under Indian law "
            "(Section 27, Indian Contract Act) even when paired with Moderate governing law "
            "that specifies Indian jurisdiction with institutional arbitration."
        ),
        "resolution_advice": (
            "Switch to Moderate non-compete, or narrow the scope to trade-secret protection only "
            "and add reasonable time and geographic boundaries."
        ),
    },
    # Limitation of Liability/Standard × Indemnification/Strict — scope mismatch
    {
        "from_id": "LIAB_STD_001",
        "to_id": "INDEM_STR_001",
        "severity": "medium",
        "conflict_type": "scope_mismatch",
        "reason": (
            "Standard Limitation of Liability typically excludes consequential damages, "
            "but Strict Indemnification may require indemnity for consequential losses, "
            "creating an internal contradiction in the contract's risk allocation."
        ),
        "resolution_advice": (
            "Align liability cap scope with indemnification scope — either use Moderate or Strict "
            "variants for both, or explicitly carve out indemnified claims from the liability cap."
        ),
    },
    # Force Majeure/Strict × Payment Terms/Strict — obligation tension
    {
        "from_id": "FM_STR_001",
        "to_id": "PAY_STR_001",
        "severity": "low",
        "conflict_type": "obligation_tension",
        "reason": (
            "Strict Force Majeure excuses performance obligations broadly, but Strict Payment Terms "
            "impose stringent payment deadlines with penalties — it is ambiguous whether payment "
            "obligations are excused during FM events."
        ),
        "resolution_advice": (
            "Add explicit carve-out in Payment Terms stating whether payment obligations are "
            "suspended during Force Majeure events, or add an FM-specific payment deferral clause."
        ),
    },
    # Termination for Convenience/Strict × Term and Renewal/Strict — competing lock-in
    {
        "from_id": "TERMC_STR_001",
        "to_id": "TERM_STR_001",
        "severity": "low",
        "conflict_type": "obligation_tension",
        "reason": (
            "Strict Termination for Convenience with high early-termination fees combined with "
            "Strict Term and Renewal with minimum commitments and holdover penalties creates "
            "a double-lock-in that may be commercially unreasonable."
        ),
        "resolution_advice": (
            "Use Moderate for one of the two clauses. If early termination fees apply, relax "
            "the minimum commitment or holdover provisions, and vice versa."
        ),
    },
    # Confidentiality/Strict × IP Ownership/Standard — inadequate IP protection
    {
        "from_id": "CONF_STR_001",
        "to_id": "IP_STD_001",
        "severity": "low",
        "conflict_type": "protection_asymmetry",
        "reason": (
            "Strict Confidentiality imposes lifetime obligations and broad injunctive relief "
            "for confidential information, but Standard IP Ownership provides only basic IP "
            "assignment without background/foreground IP distinction, creating asymmetric "
            "protection — trade secrets are heavily guarded but IP ownership is loosely defined."
        ),
        "resolution_advice": (
            "Upgrade IP Ownership to Moderate or Strict to match the rigour of confidentiality "
            "protection, ensuring pre-existing IP carve-outs and joint IP handling are defined."
        ),
    },
]


def phase2(session):
    print("\n=== PHASE 2: Cross-Clause Semantic Conflicts ===\n")

    added = 0
    skipped = 0
    for edge in CROSS_CLAUSE_CONFLICTS:
        r = session.run("""
            MATCH (a:Clause {id: $from_id})-[r:CONFLICTS_WITH]->(b:Clause {id: $to_id})
            RETURN count(*) AS cnt
        """, {"from_id": edge["from_id"], "to_id": edge["to_id"]})
        if r.single()["cnt"] > 0:
            print(f"  ⏭ {edge['from_id']} → {edge['to_id']} already exists")
            skipped += 1
            continue

        session.run("""
            MATCH (a:Clause {id: $from_id}), (b:Clause {id: $to_id})
            CREATE (a)-[:CONFLICTS_WITH {
                severity: $severity,
                conflict_type: $conflict_type,
                reason: $reason,
                resolution_advice: $advice
            }]->(b)
        """, {
            "from_id": edge["from_id"],
            "to_id": edge["to_id"],
            "severity": edge["severity"],
            "conflict_type": edge["conflict_type"],
            "reason": edge["reason"],
            "advice": edge["resolution_advice"],
        })
        print(f"  ✓ {edge['from_id']} → {edge['to_id']} [{edge['severity']}]")
        added += 1

    print(f"\n✅ Phase 2 complete! Added {added} cross-clause conflicts, skipped {skipped}.")


if __name__ == "__main__":
    with driver.session() as session:
        phase2(session)
    driver.close()
