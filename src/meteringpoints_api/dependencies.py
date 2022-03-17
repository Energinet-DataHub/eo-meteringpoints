from datetime import datetime, timedelta, timezone
from typing import Optional
from origin.tokens import TokenEncoder
from origin.models.auth import InternalToken
from fastapi import Depends, HTTPException, Query
from origin.auth import TOKEN_COOKIE_NAME


# token = InternalToken(
#     issued=datetime.now(tz=timezone.utc),
#     expires=datetime.now(timezone.utc) + timedelta(hours=24),
#     actor='foo',
#     subject='bar',
#     scope=['meteringpoints.read'],
# )


# opaque_token = token_encoder.encode(token)
# print(opaque_token)

token_encoder = TokenEncoder(
    schema=InternalToken,
    secret='123',
)

class InternalTokenProviderFactory:
    def __init__(self, token_encoder: TokenEncoder[InternalToken]) -> None:
        self.token_encoder = token_encoder

    def get_internal_token_provider(self):
        async def internal_token_provider(token: str) -> InternalToken:
            """Decompose token into an OpaqueToken."""
            try:
                internal_token = self.token_encoder.decode(token)
            except self.token_encoder.DecodeError:
                raise HTTPException(status_code=500)

            if not internal_token.is_valid:
                raise HTTPException(status_code=403, detail="invalid token")

            return internal_token

async def opaque_token_provider(token: str = Query(None, alias=TOKEN_COOKIE_NAME)) -> Optional[str]:
    """
    Extract value for the opaque token provided by the client in a cookie.

    :returns: Opaque token or None
    """
    return token


class RequiresScope:
    """Only Allows requests with specific scopes granted."""
    def __init__(self, scope: str):
        self.scope = scope

    def __call__(self, token: InternalToken = Depends(internal_token_provider)) -> InternalToken:
        if self.scope not in token.scope:
            raise HTTPException(status_code=404, detail="Item not found")