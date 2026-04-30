"""
Migration script: saved_parties table
Run: python table_schema/saved_parties.py
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DDL = """
CREATE TABLE IF NOT EXISTS saved_parties (
    id                  SERIAL PRIMARY KEY,
    user_id             UUID NOT NULL,

    -- Core identity
    party_name          TEXT NOT NULL,
    legal_entity_type   TEXT,               -- 'company', 'llp', 'individual', 'partnership'

    -- Address
    address_line1       TEXT,
    address_line2       TEXT,
    city                TEXT,
    state               TEXT,
    postal_code         TEXT,
    country             TEXT NOT NULL DEFAULT 'India',

    -- Contact
    contact_person      TEXT,
    email               TEXT,
    phone               TEXT,

    -- Timestamps
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Prevent duplicate party names per user
    CONSTRAINT uq_saved_party_user_name UNIQUE (user_id, party_name)
);

CREATE INDEX IF NOT EXISTS idx_saved_parties_user_id
    ON saved_parties (user_id);
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
        print("✅ saved_parties table created successfully!")
        print("   🎯 UNIQUE(user_id, party_name) enforced — no duplicate names per user")
    except Exception as e:
        print("❌ Error:", e)
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    create_schema()
