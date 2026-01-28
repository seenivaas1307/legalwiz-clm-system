import psycopg2

DDL = """
-- 1) ENUMS FOR PARAMETER METADATA
DO $$
BEGIN
    -- Data type of the parameter value
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'param_data_type_enum') THEN
        CREATE TYPE param_data_type_enum AS ENUM (
            'string',
            'integer',
            'decimal',
            'date',
            'currency',
            'boolean'
        );
    END IF;

    -- Category group from Sheet 2 (Core, Scope, etc.)
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'param_category_enum') THEN
        CREATE TYPE param_category_enum AS ENUM (
            'core',
            'scope',
            'confidentiality',
            'non_compete',
            'ip',
            'payment',
            'term',
            'termination',
            'liability',
            'sla',
            'dispute_resolution',
            'governing_law',
            'data_protection',
            'other'
        );
    END IF;

    -- Required vs optional
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'param_required_enum') THEN
        CREATE TYPE param_required_enum AS ENUM (
            'required',
            'optional'
        );
    END IF;
END$$;

-- 2) PARAMETER_DEFINITIONS TABLE
CREATE TABLE IF NOT EXISTS parameter_definitions (
    -- P_001, P_002 ... from Sheet 2
    parameter_id         TEXT PRIMARY KEY,      -- e.g. 'P_001'
    
    -- Placeholder name used in clause templates
    parameter_name       TEXT NOT NULL,         -- e.g. '{{PARTY_A_NAME}}' or '[CITY]'
    
    -- Typed metadata
    data_type            param_data_type_enum NOT NULL,
    category             param_category_enum   NOT NULL,
    required_optional    param_required_enum   NOT NULL DEFAULT 'required',
    
    -- Docs
    description          TEXT,
    example_value        TEXT,
    validation_rule      TEXT,                  -- e.g. 'positive_integer', 'email', 'date_yyyy_mm_dd'
    input_format         TEXT,                  -- e.g. 'text', 'textarea', 'select', 'date', 'number',
    
    -- Link to clauses (Neo4j ids) where this parameter is used
    -- Example: ['CONF_STD_001', 'CONF_MOD_001']
    used_in_clauses      TEXT[] NOT NULL DEFAULT '{}',
    
    -- Optional: allow quick search by name/category
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3) Indexes for faster lookups
-- Find all parameters used by a given clause_id
CREATE INDEX IF NOT EXISTS idx_param_defs_used_in_clauses
    ON parameter_definitions
    USING GIN (used_in_clauses);

-- Search by category (e.g. show all Core parameters)
CREATE INDEX IF NOT EXISTS idx_param_defs_category
    ON parameter_definitions(category);

-- Search by data_type (for UI rendering)
CREATE INDEX IF NOT EXISTS idx_param_defs_data_type
    ON parameter_definitions(data_type);
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
        print("✅ parameter_definitions table created with enums + GIN index on used_in_clauses!")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    create_schema()
