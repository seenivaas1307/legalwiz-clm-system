import psycopg2

DDL = """
-- 1) CONTRACT_PARAMETERS TABLE
CREATE TABLE IF NOT EXISTS contract_parameters (
    id              SERIAL PRIMARY KEY,

    -- Keys
    contract_id     UUID NOT NULL
                    REFERENCES contracts(id)
                    ON DELETE CASCADE,

    parameter_id    TEXT NOT NULL
                    REFERENCES parameter_definitions(parameter_id)
                    ON DELETE RESTRICT,

    -- Polymorphic value storage
    value_text      TEXT,
    value_integer   INTEGER,
    value_decimal   NUMERIC(20,4),
    value_date      DATE,
    value_currency  JSONB,      -- e.g. {"amount": 500000, "currency": "INR"}

    -- Metadata
    provided_by     UUID,       -- auth.users(id) if you want FK later
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- One value per parameter per contract
    CONSTRAINT unique_contract_parameter UNIQUE (contract_id, parameter_id)
);

-- 2) Indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_contract_params_contract
    ON contract_parameters(contract_id);

CREATE INDEX IF NOT EXISTS idx_contract_params_param
    ON contract_parameters(parameter_id);
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
        print("✅ contract_parameters table created with FK → contracts & parameter_definitions!")
        print("   🎯 UNIQUE(contract_id, parameter_id) enforced")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    create_schema()
