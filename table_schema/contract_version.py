import psycopg2

DDL = """
-- 1) CONTRACT_VERSIONS TABLE
CREATE TABLE IF NOT EXISTS contract_versions (
    id              SERIAL PRIMARY KEY,

    -- Link to contracts table
    contract_id     UUID NOT NULL
                    REFERENCES contracts(id)
                    ON DELETE CASCADE,

    -- Version tracking
    version_number  INTEGER NOT NULL,
    
    -- Full snapshot
    content         JSONB NOT NULL,           -- {
                                                --   "clauses": [...],
                                                --   "parameters": {...},
                                                --   "full_text": "Contract text...",
                                                --   "parties": [...]
                                                -- }

    -- Metadata
    change_summary  TEXT,                     -- "Added Confidentiality clause"
    changed_by      UUID,                     -- auth.users(id)

    -- Timestamps
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Ensure one version number per contract
    CONSTRAINT unique_version_per_contract 
        UNIQUE (contract_id, version_number)
);

-- 2) Indexes
CREATE INDEX IF NOT EXISTS idx_contract_versions_contract
    ON contract_versions(contract_id);

CREATE INDEX IF NOT EXISTS idx_contract_versions_number
    ON contract_versions(contract_id, version_number DESC);

-- 3) Trigger for auto-increment version_number
CREATE OR REPLACE FUNCTION increment_version_number()
RETURNS TRIGGER AS $$
BEGIN
    NEW.version_number := COALESCE(
        (SELECT MAX(version_number) + 1 
         FROM contract_versions 
         WHERE contract_id = NEW.contract_id), 1
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_increment_version
    BEFORE INSERT ON contract_versions
    FOR EACH ROW EXECUTE FUNCTION increment_version_number();
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
        print("✅ contract_versions table created with auto-increment versions!")
        print("   🔗 FK → contracts(id)")
        print("   📦 JSONB content snapshot")
        print("   ⚙️  Auto version_number trigger")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    create_schema()
