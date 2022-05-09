from unittest import mock
import pytest
import requests_mock

from origin.models.meteringpoints import (
    MeteringPoint,
)
from meteringpoints_shared.datasync_httpclient import DataSyncHttpClient


METERINGPOINTS = [
    MeteringPoint(gsrn='GSRN#1'),
    MeteringPoint(gsrn='GSRN#2'),
    MeteringPoint(gsrn='GSRN#3'),
]

METERINGPOINTS_JSON = [{'gsrn': mp.gsrn} for mp in METERINGPOINTS]


# -- Requests ---------------------------------------------------------------


@pytest.fixture(scope='function')
def request_mocker() -> requests_mock:
    """
    Provide a request mocker.

    Can be used to mock requests responses made to eg.
    OpenID Connect api endpoints.
    """

    with requests_mock.Mocker() as mock:
        yield mock


class TestDataSyncHttpClient:
    """Tests TestDatasyncHttpClient."""

    def test__get_meteringpoints_by_tin__should_return_correct_meteringpoints(
            self,
            request_mocker: requests_mock,
    ):
        # -- Arrange ---------------------------------------------------------
        base_url = "http://foo.com"
        tin = "test"

        uut = DataSyncHttpClient(base_url, "very token")

        request_mocker.get(
            f'{base_url}/MeteringPoint/GetByTin/{tin}',
            json=METERINGPOINTS_JSON,
            status_code=200,
        )

        uut = DataSyncHttpClient(base_url, "very token")

        # -- Act -------------------------------------------------------------

        meteringpoints = uut.get_meteringpoints_by_tin(tin)

        # -- Assert ----------------------------------------------------------

        assert all(mp in METERINGPOINTS for mp in meteringpoints)

    def test__get_meteringpoints_by_tin__return_404_should_return_correct_status_code(
            self,
            request_mocker: requests_mock,
    ):
        # -- Arrange ---------------------------------------------------------
        base_url = "http://foo.com"
        tin = "test"

        uut = DataSyncHttpClient(base_url, "very token")

        request_mocker.get(
            f'{base_url}/MeteringPoint/GetByTin/{tin}',
            json={},
            status_code=404,
        )

        # -- Assert/Act ------------------------------------------------------

        with pytest.raises(DataSyncHttpClient.HttpError) as error:
            uut.get_meteringpoints_by_tin(tin)
            assert error.status_code == 404

    def test__get_meteringpoints_by_tin__return_500_should_return_correct_status_code(
            self,
            request_mocker: requests_mock,
    ):
        # -- Arrange ---------------------------------------------------------
        base_url = "http://foo.com"
        tin = "test"
        status_code = 500

        uut = DataSyncHttpClient(base_url, "very token")

        request_mocker.get(
            f'{base_url}/MeteringPoint/GetByTin/{tin}',
            json={},
            status_code=status_code,
        )

        # -- Assert/Act ------------------------------------------------------
        with pytest.raises(
            DataSyncHttpClient.HttpError,
            match="Failed to fetch meteringpoints by tin."
        ) as error:
            uut.get_meteringpoints_by_tin(tin)
            assert error.status_code == status_code

    def test__get_meteringpoints_by_tin__invalid_json__should_return_correct_status_code(
            self,
            request_mocker: requests_mock,
    ):
        # -- Arrange ---------------------------------------------------------
        base_url = "http://foo.com"
        tin = "test"
        status_code = 200

        uut = DataSyncHttpClient(base_url, "very token")

        request_mocker.get(
            f'{base_url}/MeteringPoint/GetByTin/{tin}',
            json=[{'INVALID_GSRN_ID': mp.gsrn} for mp in METERINGPOINTS],
            status_code=status_code,
        )

        # -- Assert/Act ------------------------------------------------------
        with pytest.raises(
            DataSyncHttpClient.DecodeError,
            match="Failed to decode meteringpoints."
        ) as error:
            uut.get_meteringpoints_by_tin(tin)
            assert error.status_code == status_code
