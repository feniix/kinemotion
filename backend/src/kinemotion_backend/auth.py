"""Supabase authentication utilities for JWT validation.

Supports both RS256 (recommended) and HS256 (legacy) JWT signing.
New Supabase projects use RS256 by default with JWKS endpoint.
Legacy projects may use HS256 with shared JWT secret.

See: https://supabase.com/docs/guides/auth/jwts
"""

import os
import time
from typing import Any

import httpx
import jwt
import structlog
from fastapi import HTTPException, status
from jwt import PyJWKClient

log: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class SupabaseAuth:
    """Handles Supabase JWT token validation.

    Verification strategy (in order of preference):
    1. RS256 via JWKS endpoint (recommended for new projects)
    2. Fallback to Auth server verification (works for all projects)
    """

    def __init__(self) -> None:
        """Initialize Supabase authentication."""
        self.supabase_url = os.getenv("SUPABASE_URL", "")
        # Prefer modern keys, fall back to legacy for compatibility
        self.supabase_anon_key = (
            os.getenv("SUPABASE_PUBLISHABLE_KEY") or os.getenv("SUPABASE_ANON_KEY") or ""
        )

        if not self.supabase_url:
            raise ValueError("SUPABASE_URL must be set")

        # JWKS endpoint for RS256 verification (correct path per Supabase docs)
        self.jwks_url = f"{self.supabase_url}/auth/v1/.well-known/jwks.json"
        self.jwks_client: PyJWKClient | None = None

        # Try to initialize JWKS client (may fail for HS256 projects)
        try:
            self.jwks_client = PyJWKClient(self.jwks_url)
            log.info("jwks_client_initialized", jwks_url=self.jwks_url)
        except Exception as e:
            log.warning(
                "jwks_client_init_failed",
                error=str(e),
                message="Will use Auth server fallback for verification",
            )

    def verify_token(self, token: str) -> dict[str, Any]:
        """Verify Supabase JWT token and return decoded payload.

        Uses JWKS verification for RS256 tokens, falls back to Auth server
        verification for HS256 tokens or if JWKS fails.

        Args:
            token: JWT token from Authorization header

        Returns:
            Decoded token payload containing user information

        Raises:
            HTTPException: If token is invalid or expired
        """
        start_time = time.time()

        # Try JWKS verification first (RS256)
        if self.jwks_client:
            try:
                jwks_start = time.time()
                signing_key = self.jwks_client.get_signing_key_from_jwt(token)
                payload = jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=["RS256"],
                    audience="authenticated",
                    options={"verify_aud": True},
                )
                jwks_duration_ms = (time.time() - jwks_start) * 1000
                total_duration_ms = (time.time() - start_time) * 1000

                log.info(
                    "token_verified_via_jwks",
                    jwks_duration_ms=round(jwks_duration_ms, 2),
                    total_duration_ms=round(total_duration_ms, 2),
                )
                return payload
            except jwt.PyJWKClientError:
                # JWKS might be empty for HS256 projects, try fallback
                log.debug("jwks_verification_failed_trying_fallback")
            except jwt.ExpiredSignatureError as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                ) from e
            except jwt.InvalidTokenError as e:
                # Check if this is an algorithm mismatch (HS256 token with RS256 check)
                if "alg" in str(e).lower():
                    log.debug("algorithm_mismatch_trying_fallback", error=str(e))
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Invalid token: {str(e)}",
                    ) from e

        # Fallback: Verify via Supabase Auth server (works for all projects)
        return self._verify_via_auth_server(token, start_time)

    def _verify_via_auth_server(self, token: str, overall_start_time: float) -> dict[str, Any]:
        """Verify token by calling Supabase Auth server.

        This is the recommended fallback for HS256 tokens per Supabase docs.

        Args:
            token: JWT token to verify
            overall_start_time: Start time of overall verification (for total duration)

        Returns:
            Decoded token payload containing user information
        """
        try:
            server_start = time.time()

            headers = {"Authorization": f"Bearer {token}"}
            if self.supabase_anon_key:
                headers["apikey"] = self.supabase_anon_key

            with httpx.Client() as client:
                response = client.get(
                    f"{self.supabase_url}/auth/v1/user",
                    headers=headers,
                    timeout=10.0,
                )

            server_duration_ms = (time.time() - server_start) * 1000
            total_duration_ms = (time.time() - overall_start_time) * 1000

            if response.status_code == 200:
                user_data = response.json()
                # Return payload-like structure from user data
                log.info(
                    "token_verified_via_auth_server",
                    server_duration_ms=round(server_duration_ms, 2),
                    total_duration_ms=round(total_duration_ms, 2),
                )
                return {
                    "sub": user_data.get("id"),
                    "email": user_data.get("email"),
                    "role": user_data.get("role", "authenticated"),
                    "aud": "authenticated",
                }
            else:
                log.warning(
                    "auth_server_verification_failed",
                    status_code=response.status_code,
                    server_duration_ms=round(server_duration_ms, 2),
                    total_duration_ms=round(total_duration_ms, 2),
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token verification failed",
                )
        except httpx.RequestError as e:
            request_duration_ms = (time.time() - overall_start_time) * 1000
            log.error(
                "auth_server_request_failed",
                error=str(e),
                duration_ms=round(request_duration_ms, 2),
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication error: {str(e)}",
            ) from e

    def get_user_id(self, token: str) -> str:
        """Extract user ID from JWT token.

        Args:
            token: JWT token from Authorization header

        Returns:
            User ID from token

        Raises:
            HTTPException: If token is invalid or user ID not found
        """
        payload = self.verify_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token",
            )

        return user_id

    def get_user_email(self, token: str) -> str:
        """Extract user email from JWT token.

        Args:
            token: JWT token from Authorization header

        Returns:
            User email from token

        Raises:
            HTTPException: If token is invalid or email not found
        """
        payload = self.verify_token(token)
        email = payload.get("email")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email not found in token",
            )

        return email
