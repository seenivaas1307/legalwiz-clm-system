"""
Phase 1: Fix Critical Structural Gaps
- Add effect-of-termination-and-survival to consulting-agreement and vendor-agreement
- Add missing REQUIRES edges
- Fix force-majeure REQUIRES target
"""

from neo4j import GraphDatabase
from dotenv import load_dotenv
import os, sys

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

def run(tx, query, params=None):
    result = tx.run(query, params or {})
    summary = result.consume()
    return summary.counters

def phase1(session):
    print("\n=== PHASE 1: Structural Fixes ===\n")

    # 1a. Add effect-of-termination-and-survival to consulting-agreement
    print("[1a] Adding effect-of-termination-and-survival to consulting-agreement...")

    # Check if it already exists
    r = session.run("""
        MATCH (ct:ContractType {id: 'consulting-agreement'})-[:CONTAINS_CLAUSE]->(ctype:ClauseType {id: 'effect-of-termination-and-survival'})
        RETURN count(*) AS cnt
    """)
    if r.single()["cnt"] == 0:
        # Shift sequences >= 13
        session.run("""
            MATCH (ct:ContractType {id: 'consulting-agreement'})-[r:CONTAINS_CLAUSE]->(ctype:ClauseType)
            WHERE r.sequence >= 13
            SET r.sequence = r.sequence + 1
        """)
        session.run("""
            MATCH (ct:ContractType {id: 'consulting-agreement'}),
                  (ctype:ClauseType {id: 'effect-of-termination-and-survival'})
            CREATE (ct)-[:CONTAINS_CLAUSE {sequence: 13, mandatory: true, description: 'Survival and wind-down obligations post-termination'}]->(ctype)
        """)
        print("  ✓ Added")
    else:
        print("  ⏭ Already exists, skipping")

    # 1b. Add effect-of-termination-and-survival to vendor-agreement
    print("[1b] Adding effect-of-termination-and-survival to vendor-agreement...")

    r = session.run("""
        MATCH (ct:ContractType {id: 'vendor-agreement'})-[:CONTAINS_CLAUSE]->(ctype:ClauseType {id: 'effect-of-termination-and-survival'})
        RETURN count(*) AS cnt
    """)
    if r.single()["cnt"] == 0:
        session.run("""
            MATCH (ct:ContractType {id: 'vendor-agreement'})-[r:CONTAINS_CLAUSE]->(ctype:ClauseType)
            WHERE r.sequence >= 13
            SET r.sequence = r.sequence + 1
        """)
        session.run("""
            MATCH (ct:ContractType {id: 'vendor-agreement'}),
                  (ctype:ClauseType {id: 'effect-of-termination-and-survival'})
            CREATE (ct)-[:CONTAINS_CLAUSE {sequence: 13, mandatory: true, description: 'Consequences of termination, data return, survival of obligations'}]->(ctype)
        """)
        print("  ✓ Added")
    else:
        print("  ⏭ Already exists, skipping")

    # 1c. Add missing REQUIRES edges
    print("[1c] Adding missing REQUIRES edges...")

    requires_edges = [
        {
            "from": "confidentiality",
            "to": "effect-of-termination-and-survival",
            "dep_type": "procedural",
            "critical": True,
            "reason": "Confidentiality obligations must survive contract termination to remain enforceable"
        },
        {
            "from": "indemnification",
            "to": "definitions",
            "dep_type": "definitional",
            "critical": False,
            "reason": "Indemnification requires clear definitions of Indemnified Losses, Excluded Damages, and Third-Party Claims"
        },
        {
            "from": "governing-law-and-jurisdiction",
            "to": "dispute-resolution",
            "dep_type": "procedural",
            "critical": False,
            "reason": "Governing law clause should be complemented by a dispute resolution mechanism for completeness"
        },
    ]

    for edge in requires_edges:
        r = session.run("""
            MATCH (a:ClauseType {id: $from})-[r:REQUIRES]->(b:ClauseType {id: $to})
            RETURN count(*) AS cnt
        """, {"from": edge["from"], "to": edge["to"]})
        if r.single()["cnt"] == 0:
            session.run("""
                MATCH (a:ClauseType {id: $from}), (b:ClauseType {id: $to})
                CREATE (a)-[:REQUIRES {
                    dependency_type: $dep_type,
                    is_critical: $critical,
                    reason: $reason
                }]->(b)
            """, {
                "from": edge["from"], "to": edge["to"],
                "dep_type": edge["dep_type"], "critical": edge["critical"],
                "reason": edge["reason"]
            })
            print(f"  ✓ {edge['from']} → {edge['to']}")
        else:
            print(f"  ⏭ {edge['from']} → {edge['to']} already exists")

    # 1d. Fix force-majeure REQUIRES target
    print("[1d] Fixing force-majeure REQUIRES target...")

    r = session.run("""
        MATCH (a:ClauseType {id: 'force-majeure'})-[r:REQUIRES]->(b:ClauseType {id: 'termination-for-convenience'})
        RETURN count(*) AS cnt
    """)
    if r.single()["cnt"] > 0:
        session.run("""
            MATCH (a:ClauseType {id: 'force-majeure'})-[r:REQUIRES]->(b:ClauseType {id: 'termination-for-convenience'})
            DELETE r
        """)
        print("  ✓ Removed FM → termination-for-convenience")
    else:
        print("  ⏭ FM → termination-for-convenience already removed")

    # Add FM → effect-of-termination-and-survival
    r = session.run("""
        MATCH (a:ClauseType {id: 'force-majeure'})-[r:REQUIRES]->(b:ClauseType {id: 'effect-of-termination-and-survival'})
        RETURN count(*) AS cnt
    """)
    if r.single()["cnt"] == 0:
        session.run("""
            MATCH (a:ClauseType {id: 'force-majeure'}), (b:ClauseType {id: 'effect-of-termination-and-survival'})
            CREATE (a)-[:REQUIRES {
                dependency_type: 'procedural',
                is_critical: false,
                reason: 'Force majeure prolonged beyond threshold may trigger termination; survival obligations must be defined'
            }]->(b)
        """)
        print("  ✓ Added FM → effect-of-termination-and-survival")
    else:
        print("  ⏭ FM → effect-of-termination-and-survival already exists")

    print("\n✅ Phase 1 complete!")


if __name__ == "__main__":
    with driver.session() as session:
        phase1(session)
    driver.close()
