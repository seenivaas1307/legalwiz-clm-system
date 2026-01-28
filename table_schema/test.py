import psycopg2

DDL = """
-- 1) ENUMs (your 7 contract types)
DROP TYPE IF EXISTS contract_type_enum CASCADE;
DROP TYPE IF EXISTS contract_status_enum CASCADE;
DROP TYPE IF EXISTS jurisdiction_enum CASCADE;

CREATE TYPE contract_type_enum AS ENUM (
    'employment_nda',
    'saas_service_agreement',
    'consulting_service_agreement',
    'software_license_agreement',
    'data_processing_agreement',
    'vendor_agreement',
    'partnership_agreement'
);

CREATE TYPE contract_status_enum AS ENUM (
    'draft', 'in_review', 'approved', 'signed', 'active', 'terminated'
);

CREATE TYPE jurisdiction_enum AS ENUM ('India', 'USA', 'UK');

-- 2) CONTRACTS TABLE (NO AUTH FK)
DROP TABLE IF EXISTS contracts CASCADE;

CREATE TABLE contracts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title           TEXT NOT NULL CHECK (LENGTH(title) <= 500),
    contract_type   contract_type_enum NOT NULL,
    jurisdiction    jurisdiction_enum NOT NULL DEFAULT 'India'::jurisdiction_enum,
    status          contract_status_enum NOT NULL DEFAULT 'draft'::contract_status_enum,
    
    -- No FK - just UUID
    created_by      UUID NOT NULL,
    
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    description     TEXT CHECK (description IS NULL OR LENGTH(description) <= 2000),
    tags            TEXT[]
);

-- 3) Indexes
CREATE INDEX idx_contracts_created_by ON contracts(created_by);
CREATE INDEX idx_contracts_status ON contracts(status);
CREATE INDEX idx_contracts_type ON contracts(contract_type);
CREATE INDEX idx_contracts_created_at ON contracts(created_at DESC);

-- 4) No RLS (open for dev)
-- ALTER TABLE contracts ENABLE ROW LEVEL SECURITY; -- commented out

SELECT '✅ Contracts table created WITHOUT auth dependency!' as status;
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
        print("✅ contracts table created WITHOUT auth FK!")
        print("   🎯 7 contract types ready")
        print("   🔓 No auth.users dependency")
        print("   🚀 Ready for API testing")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    create_schema()
