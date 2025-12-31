# Migration 999: Convert users.id from INTEGER to UUID

**Status**: 🔴 **CRITICAL BREAKING CHANGE**
**Estimated Downtime**: 5-15 minutes (depends on data volume)
**Reversibility**: ⚠️ **One-way migration** (downgrade loses data)

---

## 📋 What This Migration Does

Converts the `users` table primary key from `INTEGER` to `UUID`, and updates all foreign key references:

| Table | Column | Before | After |
|-------|--------|--------|-------|
| **users** | `id` | INTEGER (AUTO) | UUID |
| **tasks** | `user_id` | INTEGER (FK) | UUID (FK) |
| **tags** | `user_id` | INTEGER (FK) | UUID (FK) |
| **notifications** | `user_id` | INTEGER (FK) | UUID (FK) |

**Why this is needed**: Constitution mandates UUID for user IDs to prevent enumeration attacks and enhance security.

---

## ⚠️ CRITICAL WARNINGS

### 1. **Breaking Changes**
- ❌ All existing JWT tokens will become **INVALID**
- ❌ Users **MUST re-authenticate** after migration
- ❌ Any external systems referencing user IDs must be updated
- ❌ Frontend applications must handle UUID format (36 chars vs integers)

### 2. **Data Integrity**
- ✅ User data is preserved (no deletion)
- ✅ Task/Tag/Notification relationships maintained
- ⚠️ Integer → UUID mapping is **PERMANENT** (cannot reverse without data loss)

### 3. **Downtime Required**
- Database will be **LOCKED** during migration
- Estimated time: 1-2 seconds per 1000 users
- 10,000 users ≈ 10-20 seconds downtime

---

## 📝 Pre-Migration Checklist

### 1. **Environment Verification**

```bash
# Verify you're targeting the correct database
echo $DATABASE_URL

# Check current migration status
cd backend
python -m alembic current

# Should show: 7153bd9cdab5 (head) - GIN index migration
```

### 2. **Backup Database**

**MANDATORY** - Do not skip this step!

```bash
# PostgreSQL backup
pg_dump -U postgres -h localhost -d todo_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup file exists and is not empty
ls -lh backup_*.sql

# Test backup can be restored (on test database)
# createdb todo_db_test
# psql -U postgres -d todo_db_test < backup_YYYYMMDD_HHMMSS.sql
```

### 3. **Pre-Migration Verification**

```bash
cd backend
python scripts/verify_migration_999.py --before
```

**Expected output**:
```
PRE-MIGRATION VERIFICATION
================================================================================
✓ users.id column type: integer
✓ Total users in database: X
✓ Total tasks in database: Y
✓ Total tags in database: Z
✓ Total notifications in database: N
✓ Found 1 user_id constraints on tasks table
================================================================================
PRE-MIGRATION CHECKS PASSED ✅
```

If checks fail, **DO NOT PROCEED**. Investigate errors first.

---

## 🚀 Migration Execution

### Step-by-Step Process

#### 1. **Notify Users** (Production Only)
Send notification to all users 24-48 hours before migration:

> "Scheduled maintenance on [DATE] at [TIME]. You will need to log in again after maintenance completes. Estimated downtime: 10-15 minutes."

#### 2. **Enable Maintenance Mode** (Optional)
Put application in read-only or maintenance mode:

```bash
# Example: Set environment variable
export MAINTENANCE_MODE=true

# Or update load balancer to show maintenance page
```

#### 3. **Stop Application Servers**
Prevent new requests during migration:

```bash
# Example: Stop Docker containers
docker-compose stop backend

# Or stop systemd service
sudo systemctl stop todo-backend

# Verify no active connections
psql -U postgres -d todo_db -c "SELECT count(*) FROM pg_stat_activity WHERE datname = 'todo_db';"
```

#### 4. **Run Migration**

```bash
cd backend

# Set environment variables
export DATABASE_URL="postgresql://user:pass@host:5432/todo_db"

# Run migration (use virtual environment)
source venv/bin/activate  # or: uv venv activate

python -m alembic upgrade head
```

**Expected output**:
```
INFO  [alembic.runtime.migration] Running upgrade 7153bd9cdab5 -> 999_convert_user_id_to_uuid
Step 1/7: Adding temporary UUID column to users table...
Step 1b/7: Generating UUIDs for existing users...
Step 2/7: Adding temporary UUID columns to referencing tables...
Step 3/7: Copying UUID values to referencing tables...
Step 4/7: Dropping old foreign key constraints...
Step 5/7: Dropping old INTEGER columns...
Step 6/7: Renaming UUID columns to final names...
Step 7/7: Recreating constraints and indexes...
✅ Migration completed successfully!
⚠️  WARNING: All JWT tokens are now invalid - users must re-authenticate
```

**If migration fails**:
```bash
# Check alembic logs for error
cat alembic.log

# Restore from backup
psql -U postgres -d todo_db < backup_YYYYMMDD_HHMMSS.sql

# Investigate error before retrying
```

#### 5. **Post-Migration Verification**

```bash
python scripts/verify_migration_999.py --after
```

**Expected output**:
```
POST-MIGRATION VERIFICATION
================================================================================
✓ users.id column type: uuid
✓ tasks.user_id column type: uuid
✓ tags.user_id column type: uuid
✓ notifications.user_id column type: uuid

✓ Total users after migration: X
✓ Total tasks after migration: Y
✓ Total tags after migration: Z
✓ Total notifications after migration: N
✓ Foreign key constraints recreated successfully

✓ Sample user UUIDs:
  - 123e4567-e89b-12d3-a456-426614174000
  - 987fcdeb-51a2-43f7-8d9c-123456789abc
================================================================================
POST-MIGRATION CHECKS PASSED ✅
```

#### 6. **Verify Application Startup**

```bash
# Start backend services
docker-compose up -d backend

# Or systemctl start
sudo systemctl start todo-backend

# Check logs for UUID-related errors
docker-compose logs -f backend | grep -i uuid
```

#### 7. **Test Authentication Flow**

```bash
# Test registration (should return UUID)
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","name":"Test User"}'

# Expected response:
# {
#   "access_token": "eyJ...",
#   "user": {
#     "id": "123e4567-e89b-12d3-a456-426614174000",  # UUID format
#     "email": "test@example.com"
#   }
# }

# Decode JWT to verify UUID in "sub" claim
echo "eyJ..." | jwt decode -

# Expected payload:
# {
#   "sub": "123e4567-e89b-12d3-a456-426614174000",  # UUID string
#   "email": "test@example.com"
# }
```

#### 8. **Disable Maintenance Mode**

```bash
# Remove maintenance flag
unset MAINTENANCE_MODE

# Or update load balancer to resume traffic
```

---

## 🔄 Rollback Procedure (EMERGENCY ONLY)

⚠️ **WARNING**: Rollback is **DESTRUCTIVE** and will:
- Replace all UUIDs with arbitrary sequential integers
- Invalidate ALL JWT tokens again
- Break any systems updated to use UUIDs

**Only use if migration causes critical production issues**

```bash
cd backend

# Restore from backup (RECOMMENDED)
psql -U postgres -d todo_db < backup_YYYYMMDD_HHMMSS.sql

# OR use Alembic downgrade (NOT RECOMMENDED - data loss)
python -m alembic downgrade -1

# Verify rollback
python scripts/verify_migration_999.py --before
```

---

## 📊 Testing Strategy

### Local/Staging Testing

1. **Create test database with sample data**:
```bash
createdb todo_db_test
psql -U postgres -d todo_db_test < backend/tests/fixtures/sample_data.sql
```

2. **Run migration on test database**:
```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/todo_db_test"
python -m alembic upgrade head
```

3. **Verify data integrity**:
```bash
python scripts/verify_migration_999.py --after
```

4. **Test application against migrated database**:
```bash
# Run integration tests
pytest backend/tests/integration/ -v

# Test authentication endpoints
pytest backend/tests/integration/test_auth_endpoints.py -v
```

### Performance Testing

```bash
# Time the migration with sample data
time python -m alembic upgrade head

# Benchmark with different data volumes:
# - 100 users, 1000 tasks
# - 1,000 users, 10,000 tasks
# - 10,000 users, 100,000 tasks
```

---

## 🐛 Troubleshooting

### Error: "column user_id_uuid_temp does not exist"

**Cause**: Migration was interrupted mid-execution

**Fix**:
```bash
# Restore from backup
psql -U postgres -d todo_db < backup_YYYYMMDD_HHMMSS.sql

# Clean alembic version table
psql -U postgres -d todo_db -c "DELETE FROM alembic_version WHERE version_num = '999_convert_user_id_to_uuid';"

# Retry migration
python -m alembic upgrade head
```

### Error: "foreign key constraint violation"

**Cause**: Orphaned records exist (tasks/tags without valid user_id)

**Fix**:
```bash
# Find orphaned records BEFORE migration
psql -U postgres -d todo_db <<EOF
SELECT 'tasks' AS table_name, COUNT(*) FROM tasks t
LEFT JOIN users u ON t.user_id = u.id
WHERE u.id IS NULL;

SELECT 'tags' AS table_name, COUNT(*) FROM tags t
LEFT JOIN users u ON t.user_id = u.id
WHERE u.id IS NULL;
EOF

# Delete orphaned records
DELETE FROM tasks WHERE user_id NOT IN (SELECT id FROM users);
DELETE FROM tags WHERE user_id NOT IN (SELECT id FROM users);

# Retry migration
```

### Error: "JWT token validation fails after migration"

**Cause**: Old tokens contain integer user IDs, but database expects UUIDs

**Solution**: This is EXPECTED behavior. Users must re-authenticate.

```bash
# Clear all sessions/tokens server-side (if using Redis)
redis-cli FLUSHDB

# Frontend: Clear localStorage/cookies
# Users will be redirected to login page
```

---

## ✅ Success Criteria

Migration is successful when ALL of these are true:

- [ ] `users.id` is UUID type
- [ ] All `user_id` foreign keys are UUID type
- [ ] Foreign key constraints recreated with CASCADE
- [ ] User count matches pre-migration count
- [ ] Task/Tag/Notification counts match pre-migration
- [ ] New user registration returns UUID in response
- [ ] JWT tokens contain UUID in `sub` claim
- [ ] Existing users can log in and receive new UUID-based tokens
- [ ] Application integration tests pass

---

## 📞 Support

If you encounter issues:

1. **Check logs**: `docker-compose logs -f backend`
2. **Review verification output**: `python scripts/verify_migration_999.py --after`
3. **Restore from backup** if data integrity is compromised
4. **Document the error** with:
   - Alembic output
   - Database logs
   - Application error messages

---

**Last Updated**: 2025-12-30
**Migration Version**: 999_convert_user_id_to_uuid
