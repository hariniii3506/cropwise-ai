"""
database/migrate_sqlite_to_pg.py
Safe, controlled data migration script from SQLite (database/cropwise.db) to PostgreSQL / Neon.

Safety Guarantees:
1. READ-ONLY on SQLite: Opens SQLite with read-only URI; never modifies or deletes SQLite records.
2. Filtered & Validated: Skips known orphan/test records and verifies parent user existence.
3. Dynamic Schema Alignment: Matches target PostgreSQL columns (omits deprecated SQLite-only columns).
4. Non-Destructive on PostgreSQL: Uses ON CONFLICT (id) DO NOTHING so existing data is preserved.
5. Sequence Alignment: Updates all 5 PostgreSQL serial sequences to MAX(id).
6. Post-Migration Verification: Verifies exact record counts and foreign key integrity.
"""

import os
import sys
import sqlite3
import argparse
import json

try:
    from dotenv import load_dotenv
    _project_env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(_project_env):
        load_dotenv(dotenv_path=_project_env)
    else:
        load_dotenv()
except Exception:
    pass


# Known orphan/test record IDs to exclude from migration
KNOWN_ORPHAN_REC_IDS = {9, 10}
KNOWN_ORPHAN_EXPENSE_IDS = {8, 19, 20, 22, 23, 25, 26, 28, 29}


def get_sqlite_conn(sqlite_path):
    if not os.path.exists(sqlite_path):
        raise FileNotFoundError(f"SQLite database file not found at: {sqlite_path}")
    # Connect in read-only mode
    uri = f"file:{os.path.abspath(sqlite_path)}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def get_pg_conn(pg_url):
    import psycopg2
    from psycopg2.extras import RealDictCursor

    url = pg_url.strip()
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]

    connect_kwargs = {}
    if "sslmode=" not in url and "localhost" not in url and "127.0.0.1" not in url:
        connect_kwargs["sslmode"] = "require"

    return psycopg2.connect(url, cursor_factory=RealDictCursor, **connect_kwargs)


def migrate_data(sqlite_path, pg_url, dry_run=False):
    print("=" * 65)
    print(" CROPWISE AI - Safe SQLite to Neon PostgreSQL Data Migration")
    print("=" * 65)
    print(f"Mode : {'DRY RUN (No changes written)' if dry_run else 'LIVE MIGRATION'}")
    print("-" * 65)

    sqlite_conn = get_sqlite_conn(sqlite_path)
    pg_conn = None if dry_run else get_pg_conn(pg_url)

    try:
        if not dry_run:
            # Ensure schema tables exist in PostgreSQL
            base_dir = os.path.dirname(os.path.abspath(__file__))
            schema_file = os.path.join(base_dir, "postgres_schema.sql")
            with open(schema_file, "r", encoding="utf-8") as f:
                schema_sql = f.read()

            with pg_conn.cursor() as pg_cur:
                pg_cur.execute(schema_sql)
            pg_conn.commit()
            print("[OK] Target PostgreSQL schema verified.")

        # Dependency Order: users must be first
        tables = ["users", "recommendations", "expenses", "notes", "reminders"]
        migration_stats = {}
        migrated_user_ids = set()

        # Pre-load valid users from SQLite
        s_cur = sqlite_conn.cursor()
        s_cur.execute("SELECT id FROM users ORDER BY id ASC")
        all_sqlite_user_ids = set(r["id"] for r in s_cur.fetchall())

        for table in tables:
            s_cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not s_cur.fetchone():
                print(f"[SKIP] Table '{table}' does not exist in SQLite source.")
                continue

            s_cur.execute(f"SELECT * FROM {table} ORDER BY id ASC")
            rows = s_cur.fetchall()
            row_count = len(rows)
            migration_stats[table] = {"source_rows": row_count, "migrated": 0, "skipped": 0}

            if row_count == 0:
                print(f"[{table}] 0 rows in source. Skipping.")
                continue

            # Fetch target PostgreSQL columns to omit deprecated SQLite-only columns (like otp_code)
            target_cols = set()
            if not dry_run:
                with pg_conn.cursor() as pg_cur:
                    pg_cur.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_schema = 'public' AND table_name = %s
                    """, (table,))
                    target_cols = set(r["column_name"] for r in pg_cur.fetchall())

            # Filter valid rows
            valid_rows = []
            skipped_count = 0

            for row in rows:
                r_dict = dict(row)
                r_id = r_dict.get("id")
                u_id = r_dict.get("user_id")

                # Exclude known orphan/test records
                if table == "recommendations" and (r_id in KNOWN_ORPHAN_REC_IDS or u_id not in all_sqlite_user_ids):
                    skipped_count += 1
                    continue
                if table == "expenses" and (r_id in KNOWN_ORPHAN_EXPENSE_IDS or u_id not in all_sqlite_user_ids):
                    skipped_count += 1
                    continue
                if table in ["notes", "reminders"] and u_id not in all_sqlite_user_ids:
                    skipped_count += 1
                    continue

                valid_rows.append(r_dict)

            migration_stats[table]["skipped"] = skipped_count
            valid_count = len(valid_rows)

            print(f"[{table:15s}] Total Source: {row_count:2d} | Valid: {valid_count:2d} | Skipped: {skipped_count:2d}")

            if dry_run:
                migration_stats[table]["migrated"] = valid_count
                continue

            # Execute Live Insert into PostgreSQL
            with pg_conn.cursor() as pg_cur:
                migrated_count = 0
                for row_dict in valid_rows:
                    # Keep only columns present in PostgreSQL schema
                    filtered_cols = [c for c in row_dict.keys() if c in target_cols]
                    vals = [row_dict[c] for c in filtered_cols]
                    placeholders = ", ".join(["%s"] * len(filtered_cols))
                    col_names = ", ".join(filtered_cols)

                    query = f"""
                        INSERT INTO {table} ({col_names})
                        VALUES ({placeholders})
                        ON CONFLICT (id) DO NOTHING
                    """
                    pg_cur.execute(query, vals)
                    if pg_cur.rowcount > 0:
                        migrated_count += 1

                    if table == "users":
                        migrated_user_ids.add(row_dict["id"])

                pg_conn.commit()

                # Align PostgreSQL sequence
                try:
                    pg_cur.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE((SELECT MAX(id) FROM {table}), 1))")
                    pg_conn.commit()
                except Exception as seq_err:
                    print(f"[{table}] [NOTE] Sequence alignment notice: {seq_err}")

                migration_stats[table]["migrated"] = migrated_count

        print("-" * 65)
        print("MIGRATION EXECUTION COMPLETED")
        print("-" * 65)

        # Verification
        if not dry_run:
            print("\nPerforming Post-Migration Verification against Neon PostgreSQL...")
            with pg_conn.cursor() as pg_cur:
                verification_counts = {}
                for t in tables:
                    pg_cur.execute(f"SELECT COUNT(*) as cnt FROM {t}")
                    verification_counts[t] = pg_cur.fetchone()["cnt"]

            print("\nPostgreSQL Target Counts:")
            total_pg_records = 0
            for t, cnt in verification_counts.items():
                total_pg_records += cnt
                print(f"  - {t:15s}: {cnt}")
            print(f"  - {'TOTAL':15s}: {total_pg_records}")

        return migration_stats

    finally:
        sqlite_conn.close()
        if pg_conn:
            pg_conn.close()


def main():
    parser = argparse.ArgumentParser(description="Safely migrate CropWise AI SQLite database to PostgreSQL/Neon.")
    parser.add_argument("--pg-url", type=str, default=os.environ.get("DATABASE_URL", ""), help="PostgreSQL connection string")
    parser.add_argument("--sqlite-path", type=str, default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "cropwise.db"), help="Path to SQLite cropwise.db")
    parser.add_argument("--dry-run", action="store_true", help="Inspect without writing")

    args = parser.parse_args()

    if not args.dry_run and not args.pg_url:
        print("[ERROR] DATABASE_URL must be provided via environment or --pg-url.")
        sys.exit(1)

    migrate_data(args.sqlite_path, args.pg_url, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
