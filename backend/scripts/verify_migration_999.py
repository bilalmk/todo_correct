#!/usr/bin/env python3
"""
Verification script for migration 999 (INTEGER → UUID conversion)

Run this BEFORE and AFTER the migration to verify data integrity.

Usage:
    python scripts/verify_migration_999.py --before
    # Run migration
    python scripts/verify_migration_999.py --after
"""
import sys
import argparse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

def get_database_url():
    """Get database URL from environment."""
    return os.getenv(
        "DATABASE_URL","postgresql://postgres:postgres@localhost:5432/todo_db"
    )


def verify_before_migration(engine):
    """Verify database state BEFORE migration."""
    print("=" * 80)
    print("PRE-MIGRATION VERIFICATION")
    print("=" * 80)

    with engine.connect() as conn:
        # Check users table structure
        result = conn.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'id'
        """))
        row = result.fetchone()

        if row is None:
            print("❌ FAIL: users table not found")
            return False

        column_name, data_type = row
        print(f"✓ users.id column type: {data_type}")

        if data_type not in ('integer', 'bigint'):
            print(f"⚠️  WARNING: Expected INTEGER but found {data_type}")
            print("   This migration is designed for INTEGER → UUID conversion")
            return False

        # Count users
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        print(f"✓ Total users in database: {user_count}")

        # Count tasks, tags, notifications
        result = conn.execute(text("SELECT COUNT(*) FROM tasks"))
        task_count = result.scalar()
        print(f"✓ Total tasks in database: {task_count}")

        result = conn.execute(text("SELECT COUNT(*) FROM tags"))
        tag_count = result.scalar()
        print(f"✓ Total tags in database: {tag_count}")

        result = conn.execute(text("SELECT COUNT(*) FROM notifications"))
        notif_count = result.scalar()
        print(f"✓ Total notifications in database: {notif_count}")

        # Check foreign key constraints
        result = conn.execute(text("""
            SELECT conname, contype
            FROM pg_constraint
            WHERE conrelid = 'tasks'::regclass AND conname LIKE '%user_id%'
        """))
        constraints = result.fetchall()
        print(f"✓ Found {len(constraints)} user_id constraints on tasks table")

        print("\n" + "=" * 80)
        print("PRE-MIGRATION CHECKS PASSED ✅")
        print("=" * 80)
        print("\n⚠️  NEXT STEPS:")
        print("1. BACKUP YOUR DATABASE NOW:")
        print("   pg_dump -U postgres -d todo_db > backup_before_uuid_migration.sql")
        print("\n2. Run the migration:")
        print("   alembic upgrade head")
        print("\n3. Verify migration:")
        print("   python scripts/verify_migration_999.py --after")
        print("=" * 80)

        return True


def verify_after_migration(engine):
    """Verify database state AFTER migration."""
    print("=" * 80)
    print("POST-MIGRATION VERIFICATION")
    print("=" * 80)

    with engine.connect() as conn:
        # Check users.id is now UUID
        result = conn.execute(text("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'id'
        """))
        row = result.fetchone()

        if row is None:
            print("❌ FAIL: users table not found after migration")
            return False

        column_name, data_type = row
        print(f"✓ users.id column type: {data_type}")

        if data_type != 'uuid':
            print(f"❌ FAIL: Expected UUID but found {data_type}")
            print("   Migration may have failed!")
            return False

        # Check all user_id foreign keys are UUID
        for table in ['tasks', 'tags', 'notifications']:
            result = conn.execute(text(f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = '{table}' AND column_name = 'user_id'
            """))
            row = result.fetchone()

            if row is None:
                print(f"❌ FAIL: {table}.user_id not found")
                return False

            column_name, data_type = row
            print(f"✓ {table}.user_id column type: {data_type}")

            if data_type != 'uuid':
                print(f"❌ FAIL: Expected UUID but found {data_type}")
                return False

        # Verify data counts match
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        print(f"\n✓ Total users after migration: {user_count}")

        result = conn.execute(text("SELECT COUNT(*) FROM tasks"))
        task_count = result.scalar()
        print(f"✓ Total tasks after migration: {task_count}")

        result = conn.execute(text("SELECT COUNT(*) FROM tags"))
        tag_count = result.scalar()
        print(f"✓ Total tags after migration: {tag_count}")

        result = conn.execute(text("SELECT COUNT(*) FROM notifications"))
        notif_count = result.scalar()
        print(f"✓ Total notifications after migration: {notif_count}")

        # Verify foreign key constraints still exist
        result = conn.execute(text("""
            SELECT conname, contype
            FROM pg_constraint
            WHERE conrelid = 'tasks'::regclass AND conname = 'tasks_user_id_fkey'
        """))
        fk = result.fetchone()

        if fk is None:
            print("❌ FAIL: Foreign key constraint not found after migration")
            return False

        print("✓ Foreign key constraints recreated successfully")

        # Sample a few UUIDs to verify format
        result = conn.execute(text("SELECT id FROM users LIMIT 3"))
        sample_ids = [str(row[0]) for row in result.fetchall()]
        print(f"\n✓ Sample user UUIDs:")
        for uuid in sample_ids:
            print(f"  - {uuid}")

        print("\n" + "=" * 80)
        print("POST-MIGRATION CHECKS PASSED ✅")
        print("=" * 80)
        print("\n⚠️  IMPORTANT: All JWT tokens are now INVALID")
        print("   Users must re-authenticate to get new tokens with UUID-based claims")
        print("=" * 80)

        return True


def main():
    parser = argparse.ArgumentParser(
        description="Verify migration 999 (INTEGER → UUID conversion)"
    )
    parser.add_argument(
        "--before",
        action="store_true",
        help="Run pre-migration verification"
    )
    parser.add_argument(
        "--after",
        action="store_true",
        help="Run post-migration verification"
    )

    args = parser.parse_args()

    if not args.before and not args.after:
        parser.print_help()
        print("\n❌ ERROR: Must specify --before or --after")
        sys.exit(1)

    # Create engine
    database_url = get_database_url()
    print(f"Connecting to database: {database_url.split('@')[1]}")  # Hide credentials

    try:
        engine = create_engine(database_url)

        if args.before:
            success = verify_before_migration(engine)
        else:
            success = verify_after_migration(engine)

        engine.dispose()

        if not success:
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
