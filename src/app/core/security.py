"""
Security utilities for Supabase JWT token verification.
"""

from typing import Any, Optional

import jwt
from supabase import Client, create_client

from app.config import settings

# Supabase client (admin with service role key)
_supabase_admin: Optional[Client] = None


def get_supabase_admin() -> Client:
    """Get Supabase admin client with service role key."""
    global _supabase_admin
    if _supabase_admin is None:
        _supabase_admin = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key,
        )
    return _supabase_admin


def verify_supabase_token(token: str) -> Optional[dict[str, Any]]:
    """
    Verify a Supabase JWT token.

    Args:
        token: The JWT token from Authorization header

    Returns:
        Decoded token payload if valid, None if invalid
    """
    try:
        # Supabase uses HS256 with the JWT secret
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract the Supabase user ID (sub) from a JWT token.

    Args:
        token: The JWT token

    Returns:
        User ID string if valid, None if invalid
    """
    payload = verify_supabase_token(token)
    if payload is None:
        return None
    return payload.get("sub")
