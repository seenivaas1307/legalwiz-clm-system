"""
Audit script: Dump full graph structure for legal review.
"""
import os, json
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

with driver.session(database=NEO4J_DATABASE) as session:
    # 1. Node labels + counts
    print("=== NODE LABELS ===")
    r = session.run("CALL db.labels() YIELD label RETURN label ORDER BY label")
    labels = [rec["label"] for rec in r]
    for label in labels:
        c = session.run(f"MATCH (n:`{label}`) RETURN count(n) AS c").single()["c"]
        print(f"  :{label} -> {c}")

    # 2. Relationship types + counts
    print("\n=== RELATIONSHIP TYPES ===")
    r = session.run("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType ORDER BY relationshipType")
    rel_types = [rec["relationshipType"] for rec in r]
    for rt in rel_types:
        c = session.run(f"MATCH ()-[r:`{rt}`]->() RETURN count(r) AS c").single()["c"]
        print(f"  [:{rt}] -> {c}")

    # 3. Relationship patterns
    print("\n=== RELATIONSHIP PATTERNS ===")
    r = session.run("""
        MATCH (a)-[r]->(b)
        RETURN DISTINCT labels(a) AS from_labels, type(r) AS rel_type, labels(b) AS to_labels,
               count(*) AS count
        ORDER BY count DESC
    """)
    for rec in r:
        fl = ":".join(rec["from_labels"])
        tl = ":".join(rec["to_labels"])
        print(f"  (:{fl})-[:{rec['rel_type']}]->(:{tl})  x{rec['count']}")

    # 4. ALL ContractType nodes
    print("\n=== ALL CONTRACT TYPES ===")
    r = session.run("MATCH (ct:ContractType) RETURN ct ORDER BY ct.id")
    for rec in r:
        print(f"  {dict(rec['ct'])}")

    # 5. ALL ClauseType nodes
    print("\n=== ALL CLAUSE TYPES ===")
    r = session.run("MATCH (ct:ClauseType) RETURN ct ORDER BY ct.id")
    for rec in r:
        print(f"  {dict(rec['ct'])}")

    # 6. Which ContractType CONTAINS_CLAUSE which ClauseType
    print("\n=== CONTRACT-TYPE -> CLAUSE-TYPE MAPPING ===")
    r = session.run("""
        MATCH (ct:ContractType)-[rel:CONTAINS_CLAUSE]->(ctype:ClauseType)
        RETURN ct.id AS contract_type, ct.name AS ct_name,
               ctype.id AS clause_type, ctype.name AS ctype_name,
               rel.sequence AS seq, rel.mandatory AS mandatory,
               rel.description AS description
        ORDER BY ct.id, rel.sequence
    """)
    current_ct = None
    for rec in r:
        if rec["contract_type"] != current_ct:
            current_ct = rec["contract_type"]
            print(f"\n  [{current_ct}] {rec['ct_name']}")
        mand = "MANDATORY" if rec["mandatory"] else "optional"
        print(f"    seq={rec['seq']} {rec['clause_type']} ({rec['ctype_name']}) [{mand}]")

    # 7. REQUIRES relationships
    print("\n\n=== REQUIRES RELATIONSHIPS ===")
    r = session.run("""
        MATCH (a:ClauseType)-[req:REQUIRES]->(b:ClauseType)
        RETURN a.id AS from_type, a.name AS from_name,
               b.id AS to_type, b.name AS to_name,
               req.dependency_type AS dep_type, req.is_critical AS critical,
               req.reason AS reason
        ORDER BY a.id
    """)
    for rec in r:
        crit = "CRITICAL" if rec["critical"] else "soft"
        print(f"  {rec['from_type']}({rec['from_name']}) --REQUIRES--> {rec['to_type']}({rec['to_name']}) [{crit}] {rec['dep_type']}")
        print(f"    reason: {rec['reason']}")

    # 8. CONFLICTS_WITH relationships
    print("\n=== CONFLICTS_WITH RELATIONSHIPS ===")
    r = session.run("""
        MATCH (a:Clause)-[conf:CONFLICTS_WITH]->(b:Clause)
        RETURN a.id AS a_id, a.clause_type AS a_type, a.variant AS a_var,
               b.id AS b_id, b.clause_type AS b_type, b.variant AS b_var,
               conf.severity AS severity, conf.reason AS reason,
               conf.conflict_type AS conflict_type, conf.resolution_advice AS advice
        ORDER BY conf.severity DESC
    """)
    for rec in r:
        print(f"  {rec['a_id']}({rec['a_type']}/{rec['a_var']}) --CONFLICTS_WITH--> {rec['b_id']}({rec['b_type']}/{rec['b_var']})")
        print(f"    severity={rec['severity']}, type={rec['conflict_type']}")
        print(f"    reason: {rec['reason']}")
        print(f"    advice: {rec['advice']}")

    # 9. ALTERNATIVE_TO relationships
    print("\n=== ALTERNATIVE_TO RELATIONSHIPS ===")
    r = session.run("""
        MATCH (a:Clause)-[alt:ALTERNATIVE_TO]->(b:Clause)
        RETURN a.id AS a_id, a.clause_type AS a_type, a.variant AS a_var,
               b.id AS b_id, b.clause_type AS b_type, b.variant AS b_var,
               alt.alternative_type AS alt_type, alt.reason AS reason,
               alt.benefit AS benefit, alt.recommendation_strength AS strength
        ORDER BY alt.recommendation_strength DESC
    """)
    for rec in r:
        print(f"  {rec['a_id']}({rec['a_type']}/{rec['a_var']}) --ALTERNATIVE_TO--> {rec['b_id']}({rec['b_type']}/{rec['b_var']})")
        print(f"    type={rec['alt_type']}, strength={rec['strength']}")
        print(f"    reason: {rec['reason']}")
        print(f"    benefit: {rec['benefit']}")

    # 10. Clause->Parameter relationships (all)
    print("\n=== ALL CLAUSE->PARAMETER RELATIONSHIPS ===")
    r = session.run("""
        MATCH (c:Clause)-[:CONTAINS_PARAM]->(p:Parameter)
        RETURN c.id AS clause_id, c.clause_type AS ctype, c.variant AS variant,
               p.id AS param_id, p.name AS param_name
        ORDER BY c.clause_type, c.variant, p.name
    """)
    current_clause = None
    for rec in r:
        cid = rec["clause_id"]
        if cid != current_clause:
            current_clause = cid
            print(f"\n  {cid} ({rec['ctype']}/{rec['variant']}):")
        print(f"    -> {rec['param_id']} {rec['param_name']}")

driver.close()
