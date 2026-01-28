import psycopg2

DDL = """
-- 1) ENUM for party_role (party_a, party_b, etc.)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'party_role_enum') THEN
        CREATE TYPE party_role_enum AS ENUM (
            'party_a',
            'party_b',
            'party_c',
            'witness_1',
            'witness_2'
        );
    END IF;
END$$;

-- 2) CONTRACT_PARTIES TABLE
CREATE TABLE IF NOT EXISTS contract_parties (
    id              SERIAL PRIMARY KEY,
    
    -- Link to main contracts table (UUID)
    contract_id     UUID NOT NULL
                    REFERENCES contracts(id)
                    ON DELETE CASCADE,
    
    -- Role of this party in this contract
    party_role      party_role_enum NOT NULL,
    
    -- Core party info
    party_name      TEXT NOT NULL,
    legal_entity_type TEXT,          -- company / LLP / individual etc.
    
    -- Address fields
    address_line1   TEXT,
    address_line2   TEXT,
    city            TEXT,
    state           TEXT,
    postal_code     TEXT,
    country         TEXT DEFAULT 'India',
    
    -- Contact fields
    contact_person  TEXT,
    email           TEXT,
    phone           TEXT,
    
    -- Timestamps
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3) Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_contract_parties_contract_id
    ON contract_parties(contract_id);

CREATE INDEX IF NOT EXISTS idx_contract_parties_role
    ON contract_parties(contract_id, party_role);
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
        print("✅ contract_parties table created with FK → contracts and party_role_enum!")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    create_schema()
