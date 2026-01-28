# fix_parameter_fk.py - Remove FK constraint from contract_parameters
import psycopg2

DB_CONFIG = {
    "host": "db.wjbijphzxqizbbgpbacg.supabase.co",
    "port": 5432,
    "dbname": "postgres",
    "user": "postgres",
    "password": "Sapvoyagers@1234",
    "sslmode": "require"
}

DDL = """
-- Step 1: Remove the foreign key constraint
ALTER TABLE contract_parameters
DROP CONSTRAINT IF EXISTS contract_parameters_parameter_id_fkey;

-- Step 2: Verify it's removed
SELECT 
    conname AS constraint_name,
    contype AS constraint_type
FROM pg_constraint
WHERE conrelid = 'contract_parameters'::regclass;
"""

def fix_foreign_key():
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        
        with conn.cursor() as cur:
            # Remove FK constraint
            cur.execute("""
                ALTER TABLE contract_parameters
                DROP CONSTRAINT IF EXISTS contract_parameters_parameter_id_fkey;
            """)
            print("✅ Foreign key constraint removed!")
            
            # Verify
            cur.execute("""
                SELECT conname 
                FROM pg_constraint 
                WHERE conrelid = 'contract_parameters'::regclass
                  AND conname LIKE '%parameter_id%';
            """)
            
            remaining = cur.fetchall()
            if not remaining:
                print("✅ No parameter_id foreign key constraints remain")
            else:
                print(f"⚠️  Found remaining constraints: {remaining}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔧 Fixing contract_parameters foreign key constraint...\n")
    fix_foreign_key()
    print("\n✅ Migration complete!")
    print("   Neo4j is now the single source of truth for parameter definitions")
    print("   Supabase stores only parameter values")
