from unittest import mock
from unittest.mock import MagicMock
from urllib.request import Request
import pytest
from typing import List
from itertools import product

from origin.models.common import Order
from origin.models.meteringpoints import (
    MeteringPoint,
    MeteringPointType,
)
from meteringpoints_shared.datasync_httpclient import DataSyncHttpClient

from meteringpoints_shared.db import db
from meteringpoints_shared.models import (
    DbMeteringPoint,
    DbMeteringPointAddress,
    DbMeteringPointTechnology,
    DbMeteringPointDelegate,
    DbTechnology,
    MeteringPointFilters,
    MeteringPointOrdering,
    MeteringPointOrderingKeys,
)
from meteringpoints_shared.queries import (
    MeteringPointQuery,
    MeteringPointAddressQuery,
    MeteringPointTechnologyQuery,
    DelegateQuery,
    TechnologyQuery,
)

METERINGPOINTS = [
    MeteringPoint(gsrn='GSRN#1'),
    MeteringPoint(gsrn='GSRN#2'),
    MeteringPoint(gsrn='GSRN#3'),
]

def mocked_requests_get_success(*args, **kwargs):

    class CustomResponse:
        status_code = 200

        def json():
            array = [{'gsrn': mp.gsrn} for mp in METERINGPOINTS]
            return array

    return CustomResponse

def mocked_requests_get_404(*args, **kwargs):
    class CustomResponse:
        status_code = 404

        def json():
            return []

    return CustomResponse

class TestDataSyncHttpClient:
    """Tests TestDatasyncHttpClient."""

    @mock.patch('requests.get', side_effect=mocked_requests_get_success)
    def test__get_meteringpoints_by_tin__should_return_correct_meteringpoints(
            self,
            mocked_request_get
    ):
        # -- Arrange ---------------------------------------------------------

        uut = DataSyncHttpClient("http://foo.com", "very token")

        # -- Act -------------------------------------------------------------

        meteringpoints = uut.get_meteringpoints_by_tin('test')

        # -- Assert ----------------------------------------------------------

        assert all(mp in METERINGPOINTS for mp in meteringpoints)

    @mock.patch('requests.get', side_effect=mocked_requests_get_404)
    def test__get_meteringpoints_by_tin__gets_404__should_raise_httperror(
            self,
            mocked_request_get
    ):
        # -- Arrange ---------------------------------------------------------

        uut = DataSyncHttpClient("http://foo.com", "very token")

        # -- Act -------------------------------------------------------------
        with pytest.raises(DataSyncHttpClient.HttpError) as error:
            meteringpoints = uut.get_meteringpoints_by_tin('test')
            assert error.status_code == 404

        # -- Assert ----------------------------------------------------------


