import psycopg2

DDL = """
-- 1) BOOLEAN defaults for clause flags
-- No ENUM needed for this table

-- 2) CONTRACT_CLAUSES TABLE
CREATE TABLE IF NOT EXISTS contract_clauses (
    id              SERIAL PRIMARY KEY,
    
    -- Link to contracts table
    contract_id     UUID NOT NULL
                    REFERENCES contracts(id)
                    ON DELETE CASCADE,
    
    -- Neo4j clause references
    clause_id       TEXT NOT NULL,           -- 'NONCOMPSTR001', 'CONFSTD001'
    clause_type     TEXT NOT NULL,           -- 'Non-Compete', 'Confidentiality'
    variant         TEXT NOT NULL,           -- 'Strict', 'Moderate', 'Standard'
    
    -- Ordering & flags
    sequence        INTEGER NOT NULL,        -- Display order: 1, 2, 3...
    is_mandatory    BOOLEAN NOT NULL DEFAULT false,
    is_customized   BOOLEAN NOT NULL DEFAULT false,
    
    -- User overrides (optional)
    overridden_text TEXT,                    -- Custom clause text if modified
    
    -- Parameter binding status
    parameters_bound JSONB DEFAULT '{}',     -- {{"{{PARTY_A}}": "bound"}}
    
    -- Timestamps
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3) Unique constraint: no duplicate clauses per contract
ALTER TABLE contract_clauses 
ADD CONSTRAINT unique_clause_per_contract 
UNIQUE (contract_id, clause_id);

-- 4) Indexes for performance
CREATE INDEX IF NOT EXISTS idx_contract_clauses_contract_id 
    ON contract_clauses(contract_id);

CREATE INDEX IF NOT EXISTS idx_contract_clauses_sequence 
    ON contract_clauses(contract_id, sequence);

CREATE INDEX IF NOT EXISTS idx_contract_clauses_clause_id 
    ON contract_clauses(clause_id);
"""

def create_schema():
    conn = None
    try:
        conn = psycopg2.connect(
            host="db.wjbijphzxqizbbgpbacg.supabase.co",
            port=5432,
            dbname="postgres",
            user="postgres",
            password="Sapvoyagers@1234",
            sslmode="require"
        )
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(DDL)
        print("✅ contract_clauses table created!")
        print("   🔗 FK → contracts(id)")
        print("   📋 Neo4j clause_id storage")
        print("   🔢 sequence ordering")
        print("   ✅ UNIQUE(contract_id, clause_id)")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    create_schema()
