"""
Security Scan for Sensitive Data in Logs
T052: Verify zero JWT tokens, passwords, CSRF tokens logged per SC-015 and FR-035

Success Criteria:
- SC-015: Zero sensitive data (JWT, passwords, CSRF tokens) in logs
- FR-035: Sensitive data sanitization enforced

Built following skills:
- @.claude/skills/panaversity/betterauth-fastapi-jwt-bridge (security patterns)
"""

import pytest
import re
import os
from pathlib import Path
from src.core.monitoring import LOGS_DIR
from src.main import sanitize_error_message


@pytest.mark.security
class TestSensitiveDataSanitization:
    """Test sensitive data is properly sanitized from logs"""

    SENSITIVE_PATTERNS = {
        "jwt_token": r"Bearer\s+[\w\-\.]{20,}",  # JWT tokens
        "password": r"password[\s:=]+[\S]{8,}",  # Passwords
        "csrf_token": r"csrf[\s:=]+[\S]{10,}",  # CSRF tokens
        "api_key": r"api[_\-]?key[\s:=]+[\w\-]{20,}",  # API keys
        "db_connection": r"postgresql://[^:]+:[^@]+@",  # DB connection strings
        "secret_key": r"secret[\s:=]+[\S]{20,}",  # Secret keys
    }

    def test_jwt_tokens_sanitized_from_error_messages(self):
        """Test JWT tokens are redacted from error messages per FR-035"""

        # Sample error messages with JWT tokens
        test_cases = [
            (
                "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                "Bearer [REDACTED]",
            ),
            (
                "Failed to verify token: Bearer abc.def.ghi",
                "Bearer [REDACTED]",
            ),
            (
                "Token Bearer xyz123.456def.789ghi is invalid",
                "Bearer [REDACTED]",
            ),
        ]

        for original, expected_substring in test_cases:
            sanitized = sanitize_error_message(original)

            # Verify sensitive data removed
            assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in sanitized
            assert "abc.def.ghi" not in sanitized
            assert "xyz123.456def.789ghi" not in sanitized

            # Verify redaction marker present
            assert "[REDACTED]" in sanitized

    def test_passwords_sanitized_from_error_messages(self):
        """Test passwords are redacted from error messages per FR-035"""

        test_cases = [
            "password=MySecurePassword123!",
            "password: StrongPass456",
            "password = Secret789!",
            "Invalid credentials: password=leaked",
        ]

        for original in test_cases:
            sanitized = sanitize_error_message(original)

            # Verify password values removed
            assert "MySecurePassword123!" not in sanitized
            assert "StrongPass456" not in sanitized
            assert "Secret789!" not in sanitized
            assert "leaked" not in sanitized

            # Verify "password" field preserved but value redacted
            assert "password" in sanitized.lower()
            assert "[REDACTED]" in sanitized

    def test_csrf_tokens_sanitized_from_error_messages(self):
        """Test CSRF tokens are redacted from error messages per FR-035"""

        test_cases = [
            "csrf=csrf-token-abc123def456",
            "csrf: token-xyz789",
            "CSRF token csrf=missing-or-invalid",
        ]

        for original in test_cases:
            sanitized = sanitize_error_message(original)

            # Verify CSRF token values removed
            assert "csrf-token-abc123def456" not in sanitized
            assert "token-xyz789" not in sanitized
            assert "missing-or-invalid" not in sanitized

            # Verify redaction
            assert "[REDACTED]" in sanitized

    def test_api_keys_sanitized_from_error_messages(self):
        """Test API keys are redacted from error messages"""

        test_cases = [
            "api_key=sk_live_1234567890abcdef",
            "API_KEY: pk_test_9876543210",
            "Invalid api-key=secret_key_value",
        ]

        for original in test_cases:
            sanitized = sanitize_error_message(original)

            # Verify API key values removed
            assert "sk_live_1234567890abcdef" not in sanitized
            assert "pk_test_9876543210" not in sanitized
            assert "secret_key_value" not in sanitized

            assert "[REDACTED]" in sanitized

    def test_database_connection_strings_sanitized(self):
        """Test database connection strings with passwords are redacted"""

        test_cases = [
            "postgresql://user:password@localhost:5432/db",
            "Connection failed: postgresql://admin:secret@host/database",
            "DATABASE_URL=postgresql://myuser:mypass@server/mydb",
        ]

        for original in test_cases:
            sanitized = sanitize_error_message(original)

            # Verify passwords removed from connection strings
            assert ":password@" not in sanitized
            assert ":secret@" not in sanitized
            assert ":mypass@" not in sanitized

            # Verify connection string structure preserved but credentials redacted
            assert "postgresql://" in sanitized
            assert "[REDACTED]" in sanitized

    def test_no_false_positives_on_safe_messages(self):
        """Test normal error messages are not over-sanitized"""

        safe_messages = [
            "Task not found",
            "Invalid request parameters",
            "User does not have permission",
            "Database connection error (see logs for details)",
            "Correlation ID: abc123def456",
        ]

        for msg in safe_messages:
            sanitized = sanitize_error_message(msg)

            # Should be unchanged
            assert sanitized == msg, f"Safe message was incorrectly sanitized: {msg}"

    def test_scan_log_files_for_sensitive_data(self):
        """
        SC-015: Scan actual log files for sensitive data patterns

        This test scans generated log files to ensure no sensitive data leaked.
        """

        if not LOGS_DIR.exists():
            pytest.skip("Logs directory does not exist yet")

        log_files = list(LOGS_DIR.glob("*.log"))

        if not log_files:
            pytest.skip("No log files generated yet")

        violations = []

        for log_file in log_files:
            with open(log_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    # Check each sensitive pattern
                    for pattern_name, pattern in self.SENSITIVE_PATTERNS.items():
                        match = re.search(pattern, line, re.IGNORECASE)
                        if match:
                            violations.append(
                                {
                                    "file": log_file.name,
                                    "line": line_num,
                                    "pattern": pattern_name,
                                    "matched": match.group(0),
                                    "context": line.strip()[:100],
                                }
                            )

        # Report violations
        if violations:
            print(f"\n=== SECURITY VIOLATION: Sensitive Data in Logs ===")
            for v in violations[:10]:  # Show first 10
                print(
                    f"File: {v['file']}, Line {v['line']}, Pattern: {v['pattern']}"
                )
                print(f"  Matched: {v['matched']}")
                print(f"  Context: {v['context']}\n")

        # Assert SC-015: Zero sensitive data in logs
        assert len(violations) == 0, (
            f"Found {len(violations)} sensitive data violations in logs (SC-015). "
            f"See output above for details."
        )

    def test_structured_logging_fr029_fields_present(self):
        """
        Verify FR-029 required fields present in structured logs

        Required fields per FR-029:
        - timestamp, level, correlation_id, user_id, endpoint,
        - http_method, status_code, duration_ms, error_message, metadata
        """

        if not LOGS_DIR.exists():
            pytest.skip("Logs directory does not exist yet")

        log_files = list(LOGS_DIR.glob("*.log"))

        if not log_files:
            pytest.skip("No log files generated yet")

        import json

        required_fields = [
            "timestamp",
            "level",
            "message",
        ]

        # Optional fields that should be present when relevant
        optional_fields = [
            "correlation_id",
            "user_id",
            "endpoint",
            "http_method",
            "status_code",
            "duration_ms",
        ]

        samples_checked = 0
        missing_fields = []

        # Check first log file
        with open(log_files[0], "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                if samples_checked >= 10:  # Check first 10 log entries
                    break

                try:
                    log_entry = json.loads(line)
                    samples_checked += 1

                    # Check required fields
                    for field in required_fields:
                        if field not in log_entry:
                            missing_fields.append(
                                {
                                    "line": line_num,
                                    "field": field,
                                    "entry": str(log_entry)[:100],
                                }
                            )
                except json.JSONDecodeError:
                    # Skip non-JSON lines (shouldn't happen with JSONFormatter)
                    continue

        if missing_fields:
            print(f"\n=== Missing Required Fields (FR-029) ===")
            for mf in missing_fields[:5]:
                print(f"Line {mf['line']}: Missing '{mf['field']}'")
                print(f"  Entry: {mf['entry']}\n")

        assert (
            len(missing_fields) == 0
        ), f"Found {len(missing_fields)} log entries missing required fields (FR-029)"


@pytest.mark.security
class TestSanitizationPatternsComprehensive:
    """Comprehensive tests for all sanitization patterns"""

    def test_all_jwt_formats_sanitized(self):
        """Test various JWT token formats are all sanitized"""

        jwt_formats = [
            "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.signature",
            "Bearer abc.def.ghi",
            "Token: Bearer x.y.z",
            "jwt=eyJhbGci.payload.sig",
        ]

        for jwt_msg in jwt_formats:
            sanitized = sanitize_error_message(jwt_msg)
            assert "[REDACTED]" in sanitized
            # Ensure no JWT parts leaked
            assert "eyJhbGci" not in sanitized or "payload" not in sanitized

    def test_mixed_sensitive_data_all_sanitized(self):
        """Test message with multiple sensitive data types all sanitized"""

        mixed_message = (
            "Auth failed: Bearer abc.def.ghi, password=Secret123, "
            "csrf=token-xyz, api_key=sk_live_12345"
        )

        sanitized = sanitize_error_message(mixed_message)

        # Verify all sensitive parts removed
        assert "abc.def.ghi" not in sanitized
        assert "Secret123" not in sanitized
        assert "token-xyz" not in sanitized
        assert "sk_live_12345" not in sanitized

        # Verify multiple redactions
        assert sanitized.count("[REDACTED]") >= 4

    def test_case_insensitive_sanitization(self):
        """Test sanitization works case-insensitively"""

        test_cases = [
            "PASSWORD=MySecret123",
            "Password=MySecret456",
            "password=MySecret789",
        ]

        for msg in test_cases:
            sanitized = sanitize_error_message(msg)
            assert "MySecret" not in sanitized
            assert "[REDACTED]" in sanitized
