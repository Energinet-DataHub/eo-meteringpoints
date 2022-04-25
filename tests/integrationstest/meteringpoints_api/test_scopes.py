from datetime import datetime, timezone, timedelta

import pytest
from origin.models.auth import InternalToken
from flask.testing import FlaskClient
from typing import List, Dict, Any, Tuple, Optional

from origin.tokens import TokenEncoder

from meteringpoints_shared.db import db


TEndpoint = Tuple[str, str, List[str], Optional[Dict[str, Any]]]


@pytest.fixture(params=[
    #"('GET', '/list', ['meteringpoints.read'], None),
    ('GET', '/details', ['meteringpoints.read'], {'gsrn': '12345'}),
])
def endpoint(request) -> TEndpoint:
    """Return (method, path, required scopes, query string)."""

    return request.param


class TestScopes:
    """TODO."""

    def test__token_has_required_scope__should_return_status_200(
            self,
            endpoint: TEndpoint,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):
        """TODO."""

        # -- Arrange ---------------------------------------------------------

        method, path, scopes, query = endpoint

        token = InternalToken(
            issued=datetime.now(tz=timezone.utc),
            expires=datetime.now(timezone.utc) + timedelta(hours=1),
            actor='foo',
            subject='bar',
            scope=scopes,
        )

        token_encoded = token_encoder.encode(token)

        # -- Act -------------------------------------------------------------

        if method == 'GET':
            func = client.get
        elif method == 'POST':
            func = client.post
        else:
            raise RuntimeError('Should not have happened!')

        res = func(
            path=path,
            query_string=query,
            headers={'Authorization': f'Bearer: {token_encoded}'},
        )

        # -- Assert ----------------------------------------------------------

        assert res.status_code == 200
