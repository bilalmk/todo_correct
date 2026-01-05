#!/bin/bash
# Quick migration execution script for Migration 999
# CRITICAL: Read MIGRATION_999_GUIDE.md before running!

set -e  # Exit on error

echo "=============================================================================="
echo "Migration 999: Convert users.id from INTEGER to UUID"
echo "CRITICAL BREAKING CHANGE - ALL JWT TOKENS WILL BE INVALIDATED"
echo "=============================================================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}ERROR: DATABASE_URL environment variable not set${NC}"
    echo "Set it like: export DATABASE_URL='postgresql://user:pass@host:5432/dbname'"
    exit 1
fi

echo -e "${GREEN}✓ DATABASE_URL is set${NC}"
echo ""

# Confirmation prompt
echo -e "${YELLOW}⚠️  WARNING: This migration will:${NC}"
echo "   1. Convert users.id from INTEGER to UUID"
echo "   2. Update all foreign keys (tasks, tags, notifications)"
echo "   3. INVALIDATE all existing JWT tokens"
echo "   4. Require ALL users to re-authenticate"
echo ""
echo -e "${RED}Have you completed the following?${NC}"
echo "   [ ] Read MIGRATION_999_GUIDE.md"
echo "   [ ] Created database backup"
echo "   [ ] Tested migration on staging environment"
echo "   [ ] Notified users of maintenance window"
echo "   [ ] Stopped application servers"
echo ""

read -p "Type 'I HAVE BACKED UP THE DATABASE' to continue: " confirmation

if [ "$confirmation" != "I HAVE BACKED UP THE DATABASE" ]; then
    echo -e "${RED}Migration aborted. Please backup your database first.${NC}"
    exit 1
fi

echo ""
echo "=============================================================================="
echo "Step 1/4: Pre-Migration Verification"
echo "=============================================================================="
python scripts/verify_migration_999.py --before

if [ $? -ne 0 ]; then
    echo -e "${RED}Pre-migration checks failed. Aborting.${NC}"
    exit 1
fi

echo ""
read -p "Pre-migration checks passed. Continue with migration? (yes/no): " proceed

if [ "$proceed" != "yes" ]; then
    echo "Migration aborted by user."
    exit 0
fi

echo ""
echo "=============================================================================="
echo "Step 2/4: Running Migration"
echo "=============================================================================="

# Run Alembic migration
python -m alembic upgrade head

if [ $? -ne 0 ]; then
    echo -e "${RED}Migration failed! Check errors above.${NC}"
    echo "Restore from backup: psql -U postgres -d todo_db < backup_YYYYMMDD_HHMMSS.sql"
    exit 1
fi

echo ""
echo "=============================================================================="
echo "Step 3/4: Post-Migration Verification"
echo "=============================================================================="
python scripts/verify_migration_999.py --after

if [ $? -ne 0 ]; then
    echo -e "${RED}Post-migration verification failed!${NC}"
    echo "Consider rolling back: psql -U postgres -d todo_db < backup_YYYYMMDD_HHMMSS.sql"
    exit 1
fi

echo ""
echo "=============================================================================="
echo "Step 4/4: Migration Complete"
echo "=============================================================================="
echo -e "${GREEN}✅ Migration 999 completed successfully!${NC}"
echo ""
echo -e "${YELLOW}NEXT STEPS:${NC}"
echo "1. Restart application servers"
echo "2. Test authentication endpoints"
echo "3. Monitor logs for UUID-related errors"
echo "4. Notify users that they need to log in again"
echo ""
echo -e "${YELLOW}⚠️  CRITICAL REMINDERS:${NC}"
echo "- All JWT tokens are now INVALID"
echo "- Users MUST re-authenticate"
echo "- Keep backup file for at least 7 days"
echo ""
echo "=============================================================================="
