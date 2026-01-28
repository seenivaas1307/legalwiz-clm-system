import psycopg2

DDL = """
-- 1) ENUM TYPES (safe creation)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'contract_type_enum') THEN
        CREATE TYPE contract_type_enum AS ENUM ('employment-nda', 'service-agreement', 'sales-agreement');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'contract_status_enum') THEN
        CREATE TYPE contract_status_enum AS ENUM (
            'draft', 'in_review', 'approved', 'signed', 'active', 'terminated'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'jurisdiction_enum') THEN
        CREATE TYPE jurisdiction_enum AS ENUM ('India', 'USA', 'UK');
    END IF;
END$$;

-- 2) MAIN CONTRACTS TABLE
CREATE TABLE IF NOT EXISTS contracts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title           TEXT NOT NULL CHECK (LENGTH(title) <= 500),
    contract_type   contract_type_enum NOT NULL,
    jurisdiction    jurisdiction_enum NOT NULL DEFAULT 'India'::jurisdiction_enum,
    status          contract_status_enum NOT NULL DEFAULT 'draft'::contract_status_enum,
    created_by      UUID NOT NULL REFERENCES auth.users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    description     TEXT CHECK (description IS NULL OR LENGTH(description) <= 2000),
    tags            TEXT[]
);

-- 3) INDEXES
CREATE INDEX IF NOT EXISTS idx_contracts_created_by ON contracts(created_by);
CREATE INDEX IF NOT EXISTS idx_contracts_status ON contracts(status);
CREATE INDEX IF NOT EXISTS idx_contracts_type ON contracts(contract_type);
CREATE INDEX IF NOT EXISTS idx_contracts_jurisdiction ON contracts(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_contracts_created_at ON contracts(created_at DESC);

-- 4) Enable RLS
ALTER TABLE contracts ENABLE ROW LEVEL SECURITY;

-- 5) DROP existing policies first (fixes IF NOT EXISTS error)
DROP POLICY IF EXISTS "Users view own contracts" ON contracts;
DROP POLICY IF EXISTS "Users create contracts" ON contracts;
DROP POLICY IF EXISTS "Users update own drafts" ON contracts;

-- 6) CREATE RLS policies (no IF NOT EXISTS needed now)
CREATE POLICY "Users view own contracts" 
ON contracts FOR SELECT 
USING (auth.uid() = created_by);

CREATE POLICY "Users create contracts" 
ON contracts FOR INSERT 
WITH CHECK (auth.uid() = created_by);

CREATE POLICY "Users update own drafts" 
ON contracts FOR UPDATE 
USING (auth.uid() = created_by AND status IN ('draft', 'in_review'));
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
        print("✅ Contracts table created successfully!")
        print("   🎯 Enums + Table + Indexes + RLS (fixed policy error)")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    create_schema()
