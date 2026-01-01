#!/usr/bin/env python3
"""
Test JWT token verification using JWKS.

Usage:
    python test_jwt_verification.py --jwks-url <url> --token <jwt-token>

Example:
    python test_jwt_verification.py \
      --jwks-url http://localhost:3000/api/auth/jwks \
      --token "eyJhbGci..."
"""

import argparse
import json
import httpx
from jose import jwt, jwk, JWTError
from typing import Dict, Any


def get_jwks(jwks_url: str) -> Dict[str, Any]:
    """Fetch JWKS from Better Auth endpoint."""
    try:
        response = httpx.get(jwks_url, timeout=5.0)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        print(f"❌ Failed to fetch JWKS: {e}")
        raise


def get_signing_key(token: str, jwks_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract the public key from JWKS that matches the token's kid."""
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            raise ValueError("Token missing key ID (kid)")

        print(f"🔑 Token Key ID (kid): {kid}")

        for key in jwks_data.get("keys", []):
            if key.get("kid") == kid:
                print(f"✅ Found matching public key in JWKS")
                return key

        raise ValueError(f"No matching key found for kid: {kid}")

    except JWTError as e:
        print(f"❌ Error extracting key from token: {e}")
        raise


def verify_token(token: str, jwks_url: str, audience: str = None, issuer: str = None) -> Dict[str, Any]:
    """
    Verify JWT token using JWKS.

    Args:
        token: JWT token string
        jwks_url: URL to JWKS endpoint
        audience: Expected audience (optional)
        issuer: Expected issuer (optional)

    Returns:
        Decoded token payload
    """
    print(f"🔍 Verifying JWT token...")
    print(f"📍 JWKS URL: {jwks_url}")

    # Fetch JWKS
    jwks_data = get_jwks(jwks_url)
    print(f"✅ JWKS fetched successfully")

    # Get signing key
    signing_key = get_signing_key(token, jwks_data)

    # Verify token
    try:
        options = {
            "verify_signature": True,
            "verify_exp": True,
            "verify_aud": bool(audience),
            "verify_iss": bool(issuer),
        }

        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["EdDSA"],
            audience=audience,
            issuer=issuer,
            options=options
        )

        print(f"✅ Token signature verified")
        print(f"✅ Token is valid")

        return payload

    except jwt.ExpiredSignatureError:
        print(f"❌ Token has expired")
        raise
    except jwt.JWTClaimsError as e:
        print(f"❌ Invalid token claims: {e}")
        raise
    except JWTError as e:
        print(f"❌ JWT verification failed: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(description="Test JWT token verification with JWKS")
    parser.add_argument("--jwks-url", required=True, help="JWKS endpoint URL")
    parser.add_argument("--token", required=True, help="JWT token to verify")
    parser.add_argument("--audience", help="Expected audience (optional)")
    parser.add_argument("--issuer", help="Expected issuer (optional)")

    args = parser.parse_args()

    try:
        payload = verify_token(
            token=args.token,
            jwks_url=args.jwks_url,
            audience=args.audience,
            issuer=args.issuer
        )

        print("\n" + "="*60)
        print("✅ JWT Verification Successful!")
        print("="*60)

        print("\n📋 Token Payload:")
        print(json.dumps(payload, indent=2))

        print("\n🔐 User Information:")
        print(f"   - User ID (sub): {payload.get('sub')}")
        print(f"   - Email: {payload.get('email')}")
        print(f"   - Name: {payload.get('name')}")
        print(f"   - Issued At (iat): {payload.get('iat')}")
        print(f"   - Expires At (exp): {payload.get('exp')}")

    except Exception as e:
        print("\n" + "="*60)
        print("❌ JWT Verification Failed")
        print("="*60)
        print(f"\nError: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
