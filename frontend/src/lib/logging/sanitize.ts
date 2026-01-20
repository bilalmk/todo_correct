/**
 * Log Sanitization Utility
 * Feature: 009-chatkit-frontend
 * Task: T078b [Phase 10]
 *
 * Purpose: Sanitize sensitive data before logging per FR-020 requirements
 * - Truncate task content to first 50 characters with "[...]" suffix
 * - Redact JWT tokens (replace with "[REDACTED_TOKEN]")
 * - Redact PII fields (email, phone, address with "[REDACTED_PII]")
 * - Mask API keys (show only first 4 and last 4 characters like "sk-ab...xyz")
 * - Handle nested objects and arrays recursively
 *
 * Usage:
 * ```typescript
 * import { sanitize } from '@/lib/logging/sanitize';
 * console.log('[ChatInterface] Message sent:', sanitize({ content, userId, token }));
 * ```
 */

/**
 * Redacted placeholders
 */
const REDACTED_TOKEN = '[REDACTED_TOKEN]';
const REDACTED_PII = '[REDACTED_PII]';

/**
 * PII field names to redact (case-insensitive)
 */
const PII_FIELDS = new Set([
  'email',
  'phone',
  'phonenumber',
  'phone_number',
  'address',
  'streetaddress',
  'street_address',
  'ssn',
  'socialsecuritynumber',
  'social_security_number',
  'creditcard',
  'credit_card',
  'passport',
  'driverlicense',
  'driver_license',
]);

/**
 * Token field names to redact (case-insensitive)
 */
const TOKEN_FIELDS = new Set([
  'token',
  'jwt',
  'accesstoken',
  'access_token',
  'refreshtoken',
  'refresh_token',
  'bearer',
  'authorization',
  'apikey',
  'api_key',
  'secret',
  'password',
  'passwd',
  'pwd',
]);

/**
 * Truncate string to max length with "[...]" suffix
 */
function truncateString(str: string, maxLength: number): string {
  if (str.length <= maxLength) {
    return str;
  }
  return str.substring(0, maxLength) + '[...]';
}

/**
 * Check if value looks like a JWT token
 * JWT format: header.payload.signature (base64url encoded)
 */
function isJWTToken(value: string): boolean {
  if (typeof value !== 'string') return false;

  // JWT has exactly 2 dots separating 3 parts
  const parts = value.split('.');
  if (parts.length !== 3) return false;

  // Each part should be base64url encoded (alphanumeric + - _)
  const base64UrlPattern = /^[A-Za-z0-9_-]+$/;
  return parts.every((part) => base64UrlPattern.test(part));
}

/**
 * Check if value looks like an API key
 * Common patterns: sk-..., pk-..., api_..., etc.
 */
function isAPIKey(value: string): boolean {
  if (typeof value !== 'string') return false;

  // Match common API key prefixes
  const apiKeyPattern = /^(sk|pk|api|key|secret)[-_][a-zA-Z0-9]{8,}$/i;
  return apiKeyPattern.test(value);
}

/**
 * Mask API key - show first 4 and last 4 characters
 * Example: "sk-1234567890abcdef" -> "sk-1...cdef"
 */
function maskAPIKey(value: string): string {
  if (value.length <= 8) {
    return '****';
  }

  const first4 = value.substring(0, 4);
  const last4 = value.substring(value.length - 4);
  return `${first4}...${last4}`;
}

/**
 * Check if field name is a PII field
 */
function isPIIField(fieldName: string): boolean {
  return PII_FIELDS.has(fieldName.toLowerCase().replace(/\s+/g, ''));
}

/**
 * Check if field name is a token field
 */
function isTokenField(fieldName: string): boolean {
  return TOKEN_FIELDS.has(fieldName.toLowerCase().replace(/\s+/g, ''));
}

/**
 * Sanitize a single value
 */
function sanitizeValue(value: unknown, fieldName?: string): unknown {
  // Handle null/undefined
  if (value === null || value === undefined) {
    return value;
  }

  // Handle strings
  if (typeof value === 'string') {
    // Check if field name indicates sensitive data
    if (fieldName) {
      if (isTokenField(fieldName)) {
        return REDACTED_TOKEN;
      }
      if (isPIIField(fieldName)) {
        return REDACTED_PII;
      }
    }

    // Check if value looks like a JWT token
    if (isJWTToken(value)) {
      return REDACTED_TOKEN;
    }

    // Check if value looks like an API key
    if (isAPIKey(value)) {
      return maskAPIKey(value);
    }

    // Truncate long strings (e.g., task content)
    // Only truncate if field name suggests it's content
    if (fieldName && (
      fieldName.toLowerCase().includes('content') ||
      fieldName.toLowerCase().includes('description') ||
      fieldName.toLowerCase().includes('body') ||
      fieldName.toLowerCase().includes('message')
    )) {
      return truncateString(value, 50);
    }

    return value;
  }

  // Handle arrays
  if (Array.isArray(value)) {
    return value.map((item) => sanitizeValue(item));
  }

  // Handle objects
  if (typeof value === 'object') {
    const sanitized: Record<string, unknown> = {};
    for (const [key, val] of Object.entries(value)) {
      sanitized[key] = sanitizeValue(val, key);
    }
    return sanitized;
  }

  // Handle primitives (number, boolean, etc.)
  return value;
}

/**
 * Sanitize any value for safe logging
 *
 * @param obj - Any value to sanitize (object, array, string, etc.)
 * @returns Sanitized value safe for logging
 *
 * @example
 * ```typescript
 * // Truncate long content
 * sanitize({ content: 'A'.repeat(100) })
 * // -> { content: 'AAAA...[...]' }
 *
 * // Redact JWT tokens
 * sanitize({ token: 'eyJhbGc...' })
 * // -> { token: '[REDACTED_TOKEN]' }
 *
 * // Redact PII
 * sanitize({ email: 'user@example.com' })
 * // -> { email: '[REDACTED_PII]' }
 *
 * // Mask API keys
 * sanitize({ apiKey: 'sk-1234567890abcdef' })
 * // -> { apiKey: 'sk-1...cdef' }
 *
 * // Handle nested objects
 * sanitize({ user: { email: 'user@example.com', token: 'eyJ...' } })
 * // -> { user: { email: '[REDACTED_PII]', token: '[REDACTED_TOKEN]' } }
 * ```
 */
export function sanitize(obj: unknown): unknown {
  return sanitizeValue(obj);
}
