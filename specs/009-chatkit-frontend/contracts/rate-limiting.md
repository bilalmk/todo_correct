# Rate Limiting Contract

## Ownership

**Backend Responsibility**: Rate limiting enforcement (20 requests/minute per user)

**Frontend Responsibility**: Handle 429 responses gracefully

## Backend Implementation

- Backend MUST track request count per user_id
- Backend MUST return 429 status code when limit exceeded
- Backend MUST include `Retry-After` header (seconds until next allowed request)

**Response Format**:
```json
{
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT_EXCEEDED",
  "status": 429,
  "retry_after": 45,
  "message": "Too many requests. Please wait 45 seconds before trying again."
}
```

## Frontend Implementation

- Frontend MUST detect 429 status code
- Frontend MUST display user-facing message: "Too many requests. Please wait before sending more messages."
- Frontend MUST disable message input during rate limit period
- Frontend MUST show countdown timer (extract from `retry_after` field or `Retry-After` header)
- Frontend MUST automatically re-enable input after countdown completes

## Testing

- Backend: Test 429 response after 20 requests in 1 minute (T000c)
- Frontend: Test 429 handling with countdown timer (T072)

## Example Flow

1. User sends 21st request within 1 minute
2. Backend returns 429 with `retry_after: 45`
3. Frontend displays: "Too many requests. Please wait before sending more messages. (45s)"
4. Frontend disables message input field
5. Countdown decrements every second: "44s", "43s", ..., "1s"
6. After countdown reaches 0, input re-enabled automatically
7. User can send messages again
