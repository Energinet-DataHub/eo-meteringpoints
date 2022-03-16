from functools import cached_property
from typing import List, Optional
from origin.tokens import TokenEncoder
from origin.models.auth import InternalToken
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.security.http import HTTPBearer
from origin.auth import TOKEN_COOKIE_NAME

class TokenContext:
    def __init__(self, request: Request, token: Optional[str] = None):
        self.token_encoder = TokenEncoder(
            schema=InternalToken,
            secret='123',
        )
        self.internal_token_encoded_2 = token
        self.request = request

    @property
    def opaque_token(self) -> Optional[str]:
        """
        Extract value for the opaque token provided by the client in a cookie.

        :returns: Opaque token or None
        """

        return self.request.cookies.get(TOKEN_COOKIE_NAME)

    @property
    def token(self) -> Optional[InternalToken]:
        """Decompose token into an OpaqueToken."""

        if self.internal_token_encoded_2 is None:
            return None

        try:
            internal_token = self.token_encoder.decode(
                self.internal_token_encoded_2,
            )
        except self.token_encoder.DecodeError:
            # TODO Raise exception if in debug mode?
            return None

        if not internal_token.is_valid:
            # TODO Raise exception if in debug mode?
            return None

        return internal_token

    @property
    def is_authorized(self) -> bool:
        """Check whether or not the client provided a valid token."""
        return self.token is not None

    def has_scope(self, scope: str) -> bool:
        """Extract the scope from the token."""

        if self.token:
            print('token:', self.token)
            return scope in self.token.scope
        return False

    def get_token(self) -> Optional[InternalToken]:
        """Check if token exists."""

        if self.token:
            return self.token

        return None

    def get_subject(self) -> Optional[str]:
        """Extract subject name from the token."""

        if self.token:
            return self.token.subject

        return None


class ScopedGuard:
    """Only Allows requests with specific scopes granted."""

    def __init__(self, scopes: List[str]):
        self.scopes = scopes

    def __call__(self, token_context: TokenContext = Depends(TokenContext)) -> bool:
        print(token_context.opaque_token)
        if not token_context.is_authorized:
            return HTTPException(status_code=403)


        for scope in self.scopes:
            if scope not in token_context.token.scope:
                # TODO Write proper message
                return HTTPException(status_code=403)


        return True
