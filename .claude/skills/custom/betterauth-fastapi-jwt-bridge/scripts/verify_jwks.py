#!/usr/bin/env python3
"""
Verify JWKS endpoint availability and structure.

Usage:
    python verify_jwks.py <jwks-url>
    python verify_jwks.py http://localhost:3000/api/auth/jwks
"""

import sys
import json
import httpx
from typing import Dict, Any


def verify_jwks(jwks_url: str) -> Dict[str, Any]:
    """
    Fetch and verify JWKS endpoint.

    Args:
        jwks_url: URL to Better Auth JWKS endpoint

    Returns:
        JWKS data if successful

    Raises:
        Exception if JWKS endpoint is not accessible or invalid
    """
    print(f"🔍 Fetching JWKS from: {jwks_url}")

    try:
        response = httpx.get(jwks_url, timeout=5.0)
        response.raise_for_status()

        jwks_data = response.json()

        # Verify JWKS structure
        if "keys" not in jwks_data:
            raise ValueError("JWKS response missing 'keys' field")

        keys = jwks_data["keys"]
        if not isinstance(keys, list):
            raise ValueError("JWKS 'keys' field must be a list")

        if len(keys) == 0:
            raise ValueError("JWKS 'keys' list is empty")

        print(f"✅ JWKS endpoint is accessible")
        print(f"✅ Found {len(keys)} public key(s)")

        # Display each key
        for i, key in enumerate(keys, 1):
            print(f"\n📋 Public Key {i}:")
            print(f"   - Key ID (kid): {key.get('kid', 'N/A')}")
            print(f"   - Key Type (kty): {key.get('kty', 'N/A')}")
            print(f"   - Curve (crv): {key.get('crv', 'N/A')}")
            print(f"   - Public Key (x): {key.get('x', 'N/A')[:20]}...")

            # Verify required fields
            required_fields = ["kid", "kty", "crv", "x"]
            missing = [f for f in required_fields if f not in key]
            if missing:
                print(f"   ⚠️  Missing fields: {', '.join(missing)}")

        print(f"\n✅ JWKS structure is valid")
        return jwks_data

    except httpx.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"   Make sure Better Auth is running and JWT plugin is enabled")
        raise
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON response: {e}")
        raise
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        raise


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_jwks.py <jwks-url>")
        print("Example: python verify_jwks.py http://localhost:3000/api/auth/jwks")
        sys.exit(1)

    jwks_url = sys.argv[1]

    try:
        jwks_data = verify_jwks(jwks_url)
        print("\n" + "="*60)
        print("✅ JWKS Verification Complete!")
        print("="*60)
        print("\nNext steps:")
        print("1. Copy asset templates to your FastAPI project")
        print("2. Configure BETTER_AUTH_URL in backend .env")
        print("3. Test JWT verification with test_jwt_verification.py")

    except Exception:
        print("\n" + "="*60)
        print("❌ JWKS Verification Failed")
        print("="*60)
        sys.exit(1)


if __name__ == "__main__":
    main()
