"""
conftest.py according to pytest docs:.
https://docs.pytest.org/en/2.7.3/plugins.html?highlight=re#conftest-py-plugins
"""
# Standard Library
import os
import sys
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

# Third party
import pytest
import requests_mock
from flask.testing import FlaskClient
from testcontainers.postgres import (
    PostgresContainer,
)

# First party
from origin.models.auth import InternalToken
from origin.tokens import TokenEncoder

# Adds the src folder to the local path
test_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(test_dir, '..', 'src')
sys.path.append(src_dir)


# First party
from meteringpoints_api.app import (  # noqa: E402
    create_app,
)
from meteringpoints_shared.config import (  # noqa: E402
    INTERNAL_TOKEN_SECRET,
)
from meteringpoints_shared.db import (  # noqa: E402
    db,
)


@pytest.fixture(scope='function')
def session():
    """TODO."""

    with PostgresContainer('postgres:13.4') as psql:
        with patch('meteringpoints_shared.db.db.uri', new=psql.get_connection_url()):  # noqa: E501

            # Apply migrations
            db.ModelBase.metadata.create_all(db.engine)

            # Create session
            with db.session_class() as session:
                yield session


@pytest.fixture(scope='module')
def client() -> FlaskClient:
    """TODO."""

    yield create_app().test_client


@pytest.fixture(scope='module')
def token_encoder() -> TokenEncoder[InternalToken]:
    """Return InternalToken encoder with correct secret embedded."""
    return TokenEncoder(
        schema=InternalToken,
        secret=INTERNAL_TOKEN_SECRET,
    )


@pytest.fixture(scope='function')
def token_subject() -> str:
    """TODO."""

    yield 'bar'


@pytest.fixture(scope='function')
def valid_token(
        token_subject: str,
) -> InternalToken:
    """TODO."""

    return InternalToken(
        issued=datetime.now(tz=timezone.utc),
        expires=datetime.now(tz=timezone.utc) + timedelta(days=1),
        actor='foo',
        subject=token_subject,
        scope=['meteringpoints.read'],
    )


@pytest.fixture(scope='function')
def valid_token_encoded(
        valid_token: InternalToken,
        token_encoder: TokenEncoder[InternalToken],
) -> str:
    """TODO."""

    yield token_encoder.encode(valid_token)


@pytest.fixture(scope='function')
def request_mocker() -> requests_mock:
    """
    Provide a request mocker.

    Can be used to mock requests responses made to eg.
    OpenID Connect api endpoints.
    """

    with requests_mock.Mocker() as mock:
        yield mock
