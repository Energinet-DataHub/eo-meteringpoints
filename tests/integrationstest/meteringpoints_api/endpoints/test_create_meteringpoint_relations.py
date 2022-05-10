# Standard Library
import json

# Third party
import requests_mock
from flask.testing import FlaskClient

# First party
from meteringpoints_shared.config import (
    DATASYNC_BASE_URL,
)
from origin.models.meteringpoints import (
    MeteringPoint,
)

# Dummy data
METERINGPOINTS = [
    MeteringPoint(gsrn='GSRN#1'),
    MeteringPoint(gsrn='GSRN#2'),
    MeteringPoint(gsrn='GSRN#3'),
]

# Dummy data in json format
METERINGPOINTS_JSON = [{'gsrn': mp.gsrn} for mp in METERINGPOINTS]


class TestCreateMeteringPointRelations:
    """Tests specifically for OIDC login endpoint."""

    def test__given_correct_tin__return_success_true(
            self,
            internal_token_encoded: str,
            request_mocker: requests_mock,
            client: FlaskClient,
    ):
        """Return correct result when given valid input."""

        # -- Arrange ---------------------------------------------------------
        tin = "test"

        request_mocker.get(
            f'{DATASYNC_BASE_URL}/MeteringPoint/GetByTin/{tin}',
            json=METERINGPOINTS_JSON,
            status_code=200,
        )

        # -- Act -------------------------------------------------------------
        body = {
            "tin": tin
        }

        res = client.post(
            path='/createrelations',
            headers={
                'Authorization': 'Bearer: ' + internal_token_encoded
            },
            data=json.dumps(body)
        )

        # -- Assert ----------------------------------------------------------
        assert res.json == {'success': True}
        assert res.status_code == 200
