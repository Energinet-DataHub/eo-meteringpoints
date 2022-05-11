# Standard Library
from datetime import datetime, timedelta, timezone

# Third party
import pytest
from flask.testing import FlaskClient

# First party
from meteringpoints_api.app import create_app
from meteringpoints_shared.config import (
    INTERNAL_TOKEN_SECRET,
)
from origin.models.auth import InternalToken
from origin.tokens import TokenEncoder


@pytest.fixture(scope='function')
def client() -> FlaskClient:
    """Return API test client."""

    return create_app().test_client


@pytest.fixture(scope='function')
def internal_token_encoder() -> TokenEncoder[InternalToken]:
    """Return InternalToken encoder with correct secret embedded."""

    return TokenEncoder(
        schema=InternalToken,
        secret=INTERNAL_TOKEN_SECRET,
    )


@pytest.fixture(scope='function')
def token_tin() -> str:
    """Identity Provider's tin number (used in mocked tokens)."""
    return '39315041'


@pytest.fixture(scope='function')
def id_token() -> str:
    """Return a dummy identity provider id_token."""

    return 'id-token'


@pytest.fixture(scope='function')
def subject() -> str:
    """Return the subject."""

    return 'subject'


@pytest.fixture(scope='function')
def actor() -> str:
    """Return an actor name."""
    return 'actor'


@pytest.fixture(scope='function')
def issued_datetime() -> datetime:
    """Datetime that indicates when a token has been issued."""

    return datetime.now(tz=timezone.utc)


@pytest.fixture(scope='function')
def expires_datetime() -> datetime:
    """Datetime that indicates when an token will expire."""
    return datetime.now(tz=timezone.utc) + timedelta(days=1)


@pytest.fixture(scope='function')
def internal_token(
    subject: str,
    expires_datetime: datetime,
    issued_datetime: datetime,
    actor: str,
) -> InternalToken:
    """Return the internal token used within the system itself."""
    return InternalToken(
        issued=issued_datetime,
        expires=expires_datetime,
        actor=actor,
        subject=subject,
        scope=['meteringpoints.read', 'scope2'],
    )


@pytest.fixture(scope='function')
def internal_token_encoded(
    internal_token: InternalToken,
    internal_token_encoder: TokenEncoder[InternalToken],
) -> str:
    """Return the internal token in encoded string format."""

    return internal_token_encoder \
        .encode(internal_token)
