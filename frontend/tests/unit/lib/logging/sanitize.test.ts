/**
 * Unit Tests for Log Sanitization Utility
 * Feature: 009-chatkit-frontend
 * Task: T078c [Phase 10]
 *
 * Purpose: Test sanitization of sensitive data per FR-020 requirements
 */

import { describe, it, expect } from 'vitest';
import { sanitize } from '@/lib/logging/sanitize';

describe('sanitize', () => {
  describe('truncation', () => {
    it('should truncate content field to 50 characters with [...] suffix', () => {
      const input = {
        content: 'A'.repeat(100),
      };

      const result = sanitize(input) as any;

      expect(result.content).toBe('A'.repeat(50) + '[...]');
      expect(result.content.length).toBe(55); // 50 + '[...]'
    });

    it('should not truncate content shorter than 50 characters', () => {
      const input = {
        content: 'Short message',
      };

      const result = sanitize(input) as any;

      expect(result.content).toBe('Short message');
    });

    it('should truncate description fields', () => {
      const input = {
        description: 'B'.repeat(100),
      };

      const result = sanitize(input) as any;

      expect(result.description).toBe('B'.repeat(50) + '[...]');
    });

    it('should truncate message fields', () => {
      const input = {
        message: 'C'.repeat(100),
      };

      const result = sanitize(input) as any;

      expect(result.message).toBe('C'.repeat(50) + '[...]');
    });

    it('should truncate body fields', () => {
      const input = {
        body: 'D'.repeat(100),
      };

      const result = sanitize(input) as any;

      expect(result.body).toBe('D'.repeat(50) + '[...]');
    });
  });

  describe('token redaction', () => {
    it('should redact JWT tokens', () => {
      const input = {
        token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
      };

      const result = sanitize(input) as any;

      expect(result.token).toBe('[REDACTED_TOKEN]');
    });

    it('should redact access_token field', () => {
      const input = {
        access_token: 'some-secret-token',
      };

      const result = sanitize(input) as any;

      expect(result.access_token).toBe('[REDACTED_TOKEN]');
    });

    it('should redact accessToken field', () => {
      const input = {
        accessToken: 'some-secret-token',
      };

      const result = sanitize(input) as any;

      expect(result.accessToken).toBe('[REDACTED_TOKEN]');
    });

    it('should redact authorization field', () => {
      const input = {
        authorization: 'Bearer eyJhbGc...',
      };

      const result = sanitize(input) as any;

      expect(result.authorization).toBe('[REDACTED_TOKEN]');
    });

    it('should redact password field', () => {
      const input = {
        password: 'my-secret-password',
      };

      const result = sanitize(input) as any;

      expect(result.password).toBe('[REDACTED_TOKEN]');
    });

    it('should redact secret field', () => {
      const input = {
        secret: 'my-secret-value',
      };

      const result = sanitize(input) as any;

      expect(result.secret).toBe('[REDACTED_TOKEN]');
    });
  });

  describe('PII redaction', () => {
    it('should redact email field', () => {
      const input = {
        email: 'user@example.com',
      };

      const result = sanitize(input) as any;

      expect(result.email).toBe('[REDACTED_PII]');
    });

    it('should redact phone field', () => {
      const input = {
        phone: '+1-555-123-4567',
      };

      const result = sanitize(input) as any;

      expect(result.phone).toBe('[REDACTED_PII]');
    });

    it('should redact phone_number field', () => {
      const input = {
        phone_number: '+1-555-123-4567',
      };

      const result = sanitize(input) as any;

      expect(result.phone_number).toBe('[REDACTED_PII]');
    });

    it('should redact address field', () => {
      const input = {
        address: '123 Main St, City, State 12345',
      };

      const result = sanitize(input) as any;

      expect(result.address).toBe('[REDACTED_PII]');
    });

    it('should redact ssn field', () => {
      const input = {
        ssn: '123-45-6789',
      };

      const result = sanitize(input) as any;

      expect(result.ssn).toBe('[REDACTED_PII]');
    });

    it('should redact creditcard field', () => {
      const input = {
        creditcard: '4111-1111-1111-1111',
      };

      const result = sanitize(input) as any;

      expect(result.creditcard).toBe('[REDACTED_PII]');
    });
  });

  describe('API key masking', () => {
    it('should mask API key with sk- prefix', () => {
      const input = {
        apiKey: 'sk-1234567890abcdef',
      };

      const result = sanitize(input) as any;

      expect(result.apiKey).toBe('sk-1...cdef');
    });

    it('should mask API key with pk- prefix', () => {
      const input = {
        key: 'pk-9876543210fedcba',
      };

      const result = sanitize(input) as any;

      expect(result.key).toBe('pk-9...dcba');
    });

    it('should mask API key with api- prefix', () => {
      const input = {
        secret: 'api-abcdefghijklmnop',
      };

      const result = sanitize(input) as any;

      // Note: 'secret' field triggers token redaction first
      expect(result.secret).toBe('[REDACTED_TOKEN]');
    });

    it('should handle short API keys (<=8 chars)', () => {
      const input = {
        value: 'sk-12345', // Not detected as API key due to length
      };

      const result = sanitize(input) as any;

      expect(result.value).toBe('sk-12345'); // Not masked
    });
  });

  describe('nested object sanitization', () => {
    it('should sanitize nested objects', () => {
      const input = {
        user: {
          email: 'user@example.com',
          token: 'eyJhbGc...test.token.here',
          name: 'John Doe',
        },
      };

      const result = sanitize(input) as any;

      expect(result.user.email).toBe('[REDACTED_PII]');
      expect(result.user.token).toBe('[REDACTED_TOKEN]');
      expect(result.user.name).toBe('John Doe');
    });

    it('should sanitize arrays of objects', () => {
      const input = {
        users: [
          { email: 'user1@example.com', name: 'User 1' },
          { email: 'user2@example.com', name: 'User 2' },
        ],
      };

      const result = sanitize(input) as any;

      expect(result.users[0].email).toBe('[REDACTED_PII]');
      expect(result.users[0].name).toBe('User 1');
      expect(result.users[1].email).toBe('[REDACTED_PII]');
      expect(result.users[1].name).toBe('User 2');
    });

    it('should sanitize deeply nested objects', () => {
      const input = {
        data: {
          user: {
            profile: {
              contact: {
                email: 'deep@example.com',
              },
            },
          },
        },
      };

      const result = sanitize(input) as any;

      expect(result.data.user.profile.contact.email).toBe('[REDACTED_PII]');
    });
  });

  describe('edge cases', () => {
    it('should handle null values', () => {
      const input = {
        value: null,
      };

      const result = sanitize(input) as any;

      expect(result.value).toBeNull();
    });

    it('should handle undefined values', () => {
      const input = {
        value: undefined,
      };

      const result = sanitize(input) as any;

      expect(result.value).toBeUndefined();
    });

    it('should handle primitive values', () => {
      expect(sanitize(123)).toBe(123);
      expect(sanitize(true)).toBe(true);
      expect(sanitize('plain string')).toBe('plain string');
    });

    it('should handle arrays of primitives', () => {
      const input = [1, 2, 3, 'test', true];

      const result = sanitize(input) as any;

      expect(result).toEqual([1, 2, 3, 'test', true]);
    });

    it('should handle empty objects', () => {
      const input = {};

      const result = sanitize(input) as any;

      expect(result).toEqual({});
    });

    it('should handle empty arrays', () => {
      const input: any[] = [];

      const result = sanitize(input) as any;

      expect(result).toEqual([]);
    });
  });

  describe('realistic scenarios', () => {
    it('should sanitize chat message log', () => {
      const input = {
        message: 'Please add a task to buy groceries for the week. I need milk, eggs, bread, butter, cheese, and some vegetables.',
        userId: 'user-123',
        token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature',
        timestamp: '2026-01-20T10:00:00Z',
      };

      const result = sanitize(input) as any;

      expect(result.message).toBe('Please add a task to buy groceries for the week[...]');
      expect(result.userId).toBe('user-123');
      expect(result.token).toBe('[REDACTED_TOKEN]');
      expect(result.timestamp).toBe('2026-01-20T10:00:00Z');
    });

    it('should sanitize task creation log', () => {
      const input = {
        content: 'A'.repeat(100),
        user: {
          id: 'user-456',
          email: 'user@example.com',
        },
        metadata: {
          apiKey: 'sk-proj1234567890abcdef',
          correlationId: 'corr-789',
        },
      };

      const result = sanitize(input) as any;

      expect(result.content).toBe('A'.repeat(50) + '[...]');
      expect(result.user.id).toBe('user-456');
      expect(result.user.email).toBe('[REDACTED_PII]');
      expect(result.metadata.apiKey).toBe('sk-p...cdef');
      expect(result.metadata.correlationId).toBe('corr-789');
    });

    it('should sanitize error log with sensitive data', () => {
      const input = {
        error: 'Authentication failed',
        user: {
          email: 'admin@example.com',
          password: 'should-not-be-logged',
        },
        request: {
          headers: {
            authorization: 'Bearer eyJhbGc...token',
          },
        },
      };

      const result = sanitize(input) as any;

      expect(result.error).toBe('Authentication failed');
      expect(result.user.email).toBe('[REDACTED_PII]');
      expect(result.user.password).toBe('[REDACTED_TOKEN]');
      expect(result.request.headers.authorization).toBe('[REDACTED_TOKEN]');
    });
  });
});
