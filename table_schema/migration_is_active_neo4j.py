import psycopg2

DDL = """
-- Add is_active column to contract_clauses
ALTER TABLE contract_clauses 
ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT true;

-- Add index for faster filtering
CREATE INDEX IF NOT EXISTS idx_contract_clauses_active 
ON contract_clauses(contract_id, is_active) 
WHERE is_active = true;

-- Add index for clause_type filtering (for variant switching)
CREATE INDEX IF NOT EXISTS idx_contract_clauses_type_variant
ON contract_clauses(contract_id, clause_type, variant);

-- Drop old unique constraint (allows multiple variants per clause_type)
ALTER TABLE contract_clauses
DROP CONSTRAINT IF EXISTS unique_clause_per_contract;

-- Add new unique constraint (clause_id still unique per contract)
ALTER TABLE contract_clauses
ADD CONSTRAINT unique_clause_id_per_contract 
UNIQUE (contract_id, clause_id);
"""

def run_migration():
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
            print("✅ Migration completed!")
            print("  ✓ Added is_active column")
            print("  ✓ Created indexes")
            print("  ✓ Updated constraints")
    
    except Exception as e:
        print("❌ Error:", e)
    
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    run_migration()
