"""
Migration script: organization_profiles table
Run: python table_schema/organization_profile.py
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DDL = """
CREATE TABLE IF NOT EXISTS organization_profiles (
    id                  SERIAL PRIMARY KEY,
    user_id             UUID NOT NULL,

    -- Core identity
    company_name        TEXT NOT NULL,
    legal_entity_type   TEXT,               -- 'company', 'llp', 'individual', 'partnership'
    registration_number TEXT,               -- CIN, LLPIN, etc.

    -- Address
    address_line1       TEXT,
    address_line2       TEXT,
    city                TEXT,
    state               TEXT,
    postal_code         TEXT,
    country             TEXT NOT NULL DEFAULT 'India',

    -- Signatory
    signatory_name          TEXT,
    signatory_designation   TEXT,

    -- Contact
    email               TEXT,
    phone               TEXT,

    -- Tax identifiers
    pan                 TEXT,
    gst                 TEXT,

    -- Timestamps
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- One profile per user
    CONSTRAINT uq_org_profile_user UNIQUE (user_id)
);

CREATE INDEX IF NOT EXISTS idx_org_profiles_user_id
    ON organization_profiles (user_id);
"""


def _get_db_config():
    config = {
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME", "postgres"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD"),
        "sslmode": os.getenv("DB_SSLMODE", "require"),
    }
    missing = [k for k, v in config.items() if v is None]
    if missing:
        raise EnvironmentError(
            f"Missing required env vars: {', '.join(f'DB_{k.upper()}' for k in missing)}"
        )
    return config


def create_schema():
    conn = None
    try:
        conn = psycopg2.connect(**_get_db_config())
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(DDL)
        print("✅ organization_profiles table created successfully!")
        print("   🎯 UNIQUE(user_id) enforced — one profile per user")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    create_schema()
