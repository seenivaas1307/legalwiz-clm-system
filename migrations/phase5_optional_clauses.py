"""
Phase 5: Add Optional Clause Types to More Contract Types
- Add non-compete and non-solicitation as optional to consulting-agreement
- Add termination-for-convenience as optional to software-license
- Make force-majeure mandatory for saas-agreement
"""

from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)


def phase5(session):
    print("\n=== PHASE 5: Optional Clause Additions ===\n")

    # 5a. Add non-compete as optional to consulting-agreement
    print("[5a] Adding non-compete to consulting-agreement (optional)...")
    r = session.run("""
        MATCH (ct:ContractType {id: 'consulting-agreement'})-[:CONTAINS_CLAUSE]->(ctype:ClauseType {id: 'non-compete'})
        RETURN count(*) AS cnt
    """)
    if r.single()["cnt"] == 0:
        # Get max existing sequence
        r = session.run("""
            MATCH (ct:ContractType {id: 'consulting-agreement'})-[r:CONTAINS_CLAUSE]->(ctype:ClauseType)
            RETURN max(r.sequence) AS max_seq
        """)
        max_seq = r.single()["max_seq"] or 16
        session.run("""
            MATCH (ct:ContractType {id: 'consulting-agreement'}),
                  (ctype:ClauseType {id: 'non-compete'})
            CREATE (ct)-[:CONTAINS_CLAUSE {
                sequence: $seq, mandatory: false,
                description: 'Restrictive covenant to prevent consultant from competing during and after engagement'
            }]->(ctype)
        """, {"seq": max_seq + 1})
        print(f"  ✓ Added at seq={max_seq + 1}")
    else:
        print("  ⏭ Already exists")

    # 5b. Add non-solicitation as optional to consulting-agreement
    print("[5b] Adding non-solicitation to consulting-agreement (optional)...")
    r = session.run("""
        MATCH (ct:ContractType {id: 'consulting-agreement'})-[:CONTAINS_CLAUSE]->(ctype:ClauseType {id: 'non-solicitation'})
        RETURN count(*) AS cnt
    """)
    if r.single()["cnt"] == 0:
        r = session.run("""
            MATCH (ct:ContractType {id: 'consulting-agreement'})-[r:CONTAINS_CLAUSE]->(ctype:ClauseType)
            RETURN max(r.sequence) AS max_seq
        """)
        max_seq = r.single()["max_seq"] or 17
        session.run("""
            MATCH (ct:ContractType {id: 'consulting-agreement'}),
                  (ctype:ClauseType {id: 'non-solicitation'})
            CREATE (ct)-[:CONTAINS_CLAUSE {
                sequence: $seq, mandatory: false,
                description: 'Prevent consultant from soliciting employees or clients of the company'
            }]->(ctype)
        """, {"seq": max_seq + 1})
        print(f"  ✓ Added at seq={max_seq + 1}")
    else:
        print("  ⏭ Already exists")

    # 5c. Add termination-for-convenience as optional to software-license
    print("[5c] Adding termination-for-convenience to software-license (optional)...")
    r = session.run("""
        MATCH (ct:ContractType {id: 'software-license'})-[:CONTAINS_CLAUSE]->(ctype:ClauseType {id: 'termination-for-convenience'})
        RETURN count(*) AS cnt
    """)
    if r.single()["cnt"] == 0:
        r = session.run("""
            MATCH (ct:ContractType {id: 'software-license'})-[r:CONTAINS_CLAUSE]->(ctype:ClauseType)
            RETURN max(r.sequence) AS max_seq
        """)
        max_seq = r.single()["max_seq"] or 16
        session.run("""
            MATCH (ct:ContractType {id: 'software-license'}),
                  (ctype:ClauseType {id: 'termination-for-convenience'})
            CREATE (ct)-[:CONTAINS_CLAUSE {
                sequence: $seq, mandatory: false,
                description: 'Allow licensee to terminate the license for convenience with notice'
            }]->(ctype)
        """, {"seq": max_seq + 1})
        print(f"  ✓ Added at seq={max_seq + 1}")
    else:
        print("  ⏭ Already exists")

    # 5d. Make force-majeure mandatory for saas-agreement
    print("[5d] Making force-majeure mandatory for saas-agreement...")
    r = session.run("""
        MATCH (ct:ContractType {id: 'saas-agreement'})-[r:CONTAINS_CLAUSE]->(ctype:ClauseType {id: 'force-majeure'})
        RETURN r.mandatory AS mandatory
    """)
    rec = r.single()
    if rec and not rec["mandatory"]:
        session.run("""
            MATCH (ct:ContractType {id: 'saas-agreement'})-[r:CONTAINS_CLAUSE]->(ctype:ClauseType {id: 'force-majeure'})
            SET r.mandatory = true
        """)
        print("  ✓ Set force-majeure to mandatory")
    elif rec and rec["mandatory"]:
        print("  ⏭ Already mandatory")
    else:
        print("  ⚠ force-majeure not found in saas-agreement")

    print("\n✅ Phase 5 complete!")


if __name__ == "__main__":
    with driver.session() as session:
        phase5(session)
    driver.close()
