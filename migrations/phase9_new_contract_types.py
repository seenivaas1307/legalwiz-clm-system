"""
Phase 9: New Contract Types
Creates 3 new ContractType nodes and wires them to existing ClauseTypes.
- freelancer-agreement (Services)
- master-service-agreement (Services)
- joint-venture-agreement (Business)
"""

from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

NEW_CONTRACT_TYPES = [
    {
        "id": "freelancer-agreement",
        "name": "Freelance / Independent Contractor Agreement",
        "category": "Services",
        "description": "Agreement for engaging freelance professionals and independent contractors, covering gig economy work, project-based engagements, and contractor-client relationships.",
        "clauses": [
            ("parties-and-recitals", 1, True, "Contractor and client identification"),
            ("definitions", 2, True, "Key terms including Independent Contractor status"),
            ("scope-of-agreement", 3, True, "Project description, deliverables, and work specifications"),
            ("payment-terms", 4, True, "Fixed-fee or hourly rates, invoicing, and payment schedule"),
            ("intellectual-property-ownership", 5, True, "IP assignment for work product"),
            ("confidentiality", 6, True, "Protection of client's business information"),
            ("representations-and-warranties", 7, True, "Contractor representations of competence and authority"),
            ("limitation-of-liability", 8, True, "Liability caps appropriate for freelance engagement"),
            ("term-and-renewal", 9, True, "Project duration or engagement period"),
            ("termination-for-cause", 10, True, "Breach, non-performance, and insolvency triggers"),
            ("termination-for-convenience", 11, True, "Exit provisions with notice"),
            ("effect-of-termination-and-survival", 12, True, "Post-termination obligations"),
            ("governing-law-and-jurisdiction", 13, True, "Applicable law"),
            ("dispute-resolution", 14, True, "Dispute resolution mechanism"),
            ("entire-agreement-amendments-severability", 15, True, "Boilerplate provisions"),
            ("non-compete", 16, False, "Optional non-compete (jurisdiction-dependent enforceability)"),
            ("non-solicitation", 17, False, "Optional client/employee non-solicitation"),
        ]
    },
    {
        "id": "master-service-agreement",
        "name": "Master Service Agreement (MSA)",
        "category": "Services",
        "description": "Umbrella agreement establishing general terms governing multiple statements of work (SOWs) between parties, common in enterprise B2B relationships.",
        "clauses": [
            ("parties-and-recitals", 1, True, "Identification of parties and business context"),
            ("definitions", 2, True, "Comprehensive definitions including SOW, Change Order, and Deliverables"),
            ("scope-of-agreement", 3, True, "SOW framework and change control procedures"),
            ("payment-terms", 4, True, "Billing, invoicing, and payment terms"),
            ("intellectual-property-ownership", 5, True, "Background IP, Foreground IP, and licensing"),
            ("confidentiality", 6, True, "Bilateral confidentiality obligations"),
            ("representations-and-warranties", 7, True, "Mutual and service-specific warranties"),
            ("indemnification", 8, True, "Mutual and IP indemnification"),
            ("limitation-of-liability", 9, True, "Tiered liability caps"),
            ("force-majeure", 10, True, "Force majeure provisions for extended engagements"),
            ("term-and-renewal", 11, True, "MSA term with auto-renewal"),
            ("termination-for-cause", 12, True, "Breach, insolvency, and SLA-based triggers"),
            ("termination-for-convenience", 13, True, "SOW and MSA level termination"),
            ("effect-of-termination-and-survival", 14, True, "Transition assistance and survival"),
            ("governing-law-and-jurisdiction", 15, True, "Applicable law and jurisdiction"),
            ("dispute-resolution", 16, True, "Multi-tier dispute resolution"),
            ("entire-agreement-amendments-severability", 17, True, "Integration and amendment procedures"),
            ("data-processing-obligations", 18, False, "DPA addendum where personal data is processed"),
            ("non-solicitation", 19, False, "Employee and client non-solicitation"),
        ]
    },
    {
        "id": "joint-venture-agreement",
        "name": "Joint Venture Agreement",
        "category": "Business",
        "description": "Agreement for project-specific collaboration between parties who remain independent entities, covering shared investment, governance, profit sharing, and exit mechanisms.",
        "clauses": [
            ("parties-and-recitals", 1, True, "JV participants and background"),
            ("definitions", 2, True, "JV-specific terms including JV Entity, Capital Contribution, etc."),
            ("scope-of-agreement", 3, True, "JV purpose, scope, and exclusivity"),
            ("profit-sharing-terms", 4, True, "Profit/loss allocation and distribution mechanics"),
            ("payment-terms", 5, True, "Capital contributions, funding, and operational costs"),
            ("intellectual-property-ownership", 6, True, "Background IP, JV-created IP, and licensing back"),
            ("confidentiality", 7, True, "Protection of each party's proprietary information"),
            ("representations-and-warranties", 8, True, "Capacity, authority, and solvency representations"),
            ("indemnification", 9, True, "Mutual indemnification for JV-related claims"),
            ("limitation-of-liability", 10, True, "Liability allocation between JV participants"),
            ("force-majeure", 11, True, "FM provisions for long-term JV"),
            ("term-and-renewal", 12, True, "JV duration, milestones, and extension"),
            ("termination-for-cause", 13, True, "Default, deadlock, and exit triggers"),
            ("termination-for-convenience", 14, True, "Voluntary exit and buy-out mechanisms"),
            ("effect-of-termination-and-survival", 15, True, "Wind-down, asset distribution, and survival"),
            ("governing-law-and-jurisdiction", 16, True, "Applicable law"),
            ("dispute-resolution", 17, True, "Deadlock resolution and arbitration"),
            ("entire-agreement-amendments-severability", 18, True, "Integration and amendment"),
            ("non-compete", 19, False, "Restriction on competing with JV during term"),
            ("non-solicitation", 20, False, "Protection against poaching JV personnel"),
        ]
    }
]


def phase9(session):
    print("\n=== PHASE 9: New Contract Types ===\n")

    for ct in NEW_CONTRACT_TYPES:
        r = session.run("MATCH (c:ContractType {id: $id}) RETURN count(*) AS cnt", {"id": ct["id"]})
        if r.single()["cnt"] > 0:
            print(f"  ⏭ {ct['id']} already exists")
            continue

        session.run("""
            CREATE (ct:ContractType {
                id: $id, name: $name, category: $category, description: $description
            })
        """, ct)
        print(f"  ✓ Created ContractType: {ct['id']}")

        for clause_id, seq, mandatory, desc in ct["clauses"]:
            r = session.run("MATCH (ct2:ClauseType {id: $id}) RETURN count(*) AS cnt", {"id": clause_id})
            if r.single()["cnt"] == 0:
                print(f"    ⚠ ClauseType {clause_id} not found, skipping")
                continue

            session.run("""
                MATCH (ct:ContractType {id: $ct_id}), (ctype:ClauseType {id: $clause_id})
                CREATE (ct)-[:CONTAINS_CLAUSE {
                    sequence: $seq, mandatory: $mandatory, description: $desc
                }]->(ctype)
            """, {"ct_id": ct["id"], "clause_id": clause_id, "seq": seq, "mandatory": mandatory, "desc": desc})
            print(f"    ✓ Wired {clause_id} (seq={seq}, {'mandatory' if mandatory else 'optional'})")

    print("\n✅ Phase 9 complete!")


if __name__ == "__main__":
    with driver.session() as session:
        phase9(session)
    driver.close()
