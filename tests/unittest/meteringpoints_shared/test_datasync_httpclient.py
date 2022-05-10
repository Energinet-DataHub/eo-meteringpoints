# Third party
import pytest
import requests_mock

# First party
from meteringpoints_shared.datasync_httpclient import (
    DataSyncHttpClient,
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

METERINGPOINT_IDS = [mp.gsrn for mp in METERINGPOINTS]


class TestGetMeteringpointsByTin:
    """Tests get_meteringpoints_by_tin()."""

    def test__should_return_correct_meteringpoints(
            self,
            request_mocker: requests_mock,
    ):
        """
        get_meteringpoints_by_tin() On success, return correct meteringpoints.

        When a http requests is make successfully, return the correct
        meteringpoints.

        :param request_mocker: requests mock used for mocking requests.
        :type request_mocker: requests_mock
        """
        # -- Arrange ---------------------------------------------------------
        base_url = "http://foo.com"
        tin = "test"

        uut = DataSyncHttpClient(base_url, "foo-token")

        request_mocker.get(
            f'{base_url}/MeteringPoint/GetByTin/{tin}',
            json=METERINGPOINTS_JSON,
            status_code=200,
        )

        uut = DataSyncHttpClient(base_url, "foo-token")

        # -- Act -------------------------------------------------------------

        meteringpoints = uut.get_meteringpoints_by_tin(tin)

        # -- Assert ----------------------------------------------------------

        assert all(mp in METERINGPOINTS for mp in meteringpoints)

    def test__return_404_should_return_correct_http_error(
            self,
            request_mocker: requests_mock,
    ):
        """
        get_meteringpoints_by_tin() Raise httpError on 404 error on request.

        When getting a 404 response from api call. Expect uut to return
        correct HttpError.

        :param request_mocker: requests mock used for mocking requests.
        :type request_mocker: requests_mock
        """
        # -- Arrange ---------------------------------------------------------
        base_url = "http://foo.com"
        tin = "test"

        uut = DataSyncHttpClient(base_url, "foo-token")

        request_mocker.get(
            f'{base_url}/MeteringPoint/GetByTin/{tin}',
            json={},
            status_code=404,
        )

        # -- Assert/Act ------------------------------------------------------

        with pytest.raises(DataSyncHttpClient.HttpError) as error:
            uut.get_meteringpoints_by_tin(tin)
            assert error.status_code == 404

    def test__return_500_should_return_correct_error(
            self,
            request_mocker: requests_mock,
    ):
        """
        get_meteringpoints_by_tin() return correct error when API Call fails.

        When the requests to the datasync domain fails, test that the
        error returned is correct.

        :param request_mocker: requests mock used for mocking requests.
        :type request_mocker: requests_mock
        """

        # -- Arrange ---------------------------------------------------------
        base_url = "http://foo.com"
        tin = "test"
        status_code = 500

        uut = DataSyncHttpClient(base_url, "foo-token")

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

    def test__invalid_json__should_raise_decode_error(
            self,
            request_mocker: requests_mock,
    ):
        """
        get_meteringpoints_by_tin() raise decode error when fail to decode.

        Fail when failing to decode the response from the datasync
        api. Expected to raise decode error.

        :param request_mocker: requests mock used for mocking requests.
        :type request_mocker: requests_mock
        """
        # -- Arrange ---------------------------------------------------------
        base_url = "http://foo.com"
        tin = "test"
        status_code = 200

        uut = DataSyncHttpClient(base_url, "foo-token")

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


class TestCreateMeteringpointRelationships:
    """Tests create_meteringpoint_relationships()."""

    def test__meteringpoint_relationships_created_successfully__return_correct_response(  # noqa E501
            self,
            request_mocker: requests_mock,
    ):
        """
        Return correct reponse when function succeeds.

        When the datasync requests succeed,test that the returned
        result is correct.

        :param request_mocker: mock_used to mock datasync api.
        :type request_mocker: requests_mock
        """
        # -- Arrange ---------------------------------------------------------
        base_url = "http://foo.com"
        name_id = "test"

        # The HTTP Body returned by datasync
        data_sync_response = [
            {"meteringpoint_id": mp.gsrn, "relationship_created": True}
            for mp in METERINGPOINTS
        ]

        # Mock datasync HTTP Response
        request_mocker.post(
            f'{base_url}/MeteringPoint/createRelation',
            json=data_sync_response,
            status_code=200,
        )

        uut = DataSyncHttpClient(base_url, "foo-token")

        # -- Act -------------------------------------------------------------

        create_mp_relationship_results = uut.create_meteringpoint_relationships(   # noqa E501
            name_id=name_id,
            meteringpoint_ids=METERINGPOINT_IDS
        )

        # -- Assert ----------------------------------------------------------

        assert len(create_mp_relationship_results.successful_relationships) == len(METERINGPOINT_IDS)   # noqa E501
        assert len(create_mp_relationship_results.failed_relationships) == 0

        assert all(gsrn in METERINGPOINT_IDS for gsrn in create_mp_relationship_results.successful_relationships)   # noqa E501

    def test__some_meteringpoint_relationships_failed__return_correct_response(
            self,
            request_mocker: requests_mock,
    ):
        """
        Return correct reponse when a single relationship fails.

        When the datasync requests fails to create relationship for single
        meteringpoint, test that the returned result is correct.

        :param request_mocker: mock_used to mock datasync api.
        :type request_mocker: requests_mock
        """
        # -- Arrange ---------------------------------------------------------
        base_url = "http://foo.com"
        name_id = "test"

        # The HTTP Body returned by datasync
        data_sync_response = [
            {"meteringpoint_id": mp.gsrn, "relationship_created": True}
            for mp in METERINGPOINTS
        ]

        # Let the first meteringpoint relation fail
        data_sync_response[0]["relationship_created"] = False
        failed_meteringpoint_id = data_sync_response[0]["meteringpoint_id"]

        # Mock datasync HTTP Response
        request_mocker.post(
            f'{base_url}/MeteringPoint/createRelation',
            json=data_sync_response,
            status_code=200,
        )

        uut = DataSyncHttpClient(base_url, "foo-token")

        # -- Act -------------------------------------------------------------

        create_mp_relationship_results = uut.create_meteringpoint_relationships(   # noqa E501
            name_id=name_id,
            meteringpoint_ids=METERINGPOINT_IDS
        )

        # -- Assert ----------------------------------------------------------

        # Expect all but one to be created succesfully
        assert len(create_mp_relationship_results.successful_relationships) == len(METERINGPOINT_IDS) - 1   # noqa E501

        # Expect one to fail
        assert len(create_mp_relationship_results.failed_relationships) == 1

        assert all(gsrn == failed_meteringpoint_id for gsrn in create_mp_relationship_results.failed_relationships)   # noqa E501

    def test__datasync_domain_return_failed_http_status_code__raise_http_error(
            self,
            request_mocker: requests_mock,
    ):
        """
        Raise http error when API request fails.

        When the datasync requests fails with invalid http status_code,
        test that the function raises HTTPError.

        :param request_mocker: mock_used to mock datasync api.
        :type request_mocker: requests_mock
        """
        # -- Arrange ---------------------------------------------------------
        base_url = "http://foo.com"
        name_id = "test"
        status_code = 500

        # Mock datasync HTTP Response
        request_mocker.post(
            f'{base_url}/MeteringPoint/createRelation',
            status_code=status_code,
        )

        uut = DataSyncHttpClient(base_url, "foo-token")

        # -- Act/Assert ------------------------------------------------------

        with pytest.raises(
            DataSyncHttpClient.HttpError,
            match="Failed to create meteringpoint relationship."
        ) as error:
            uut.create_meteringpoint_relationships(
                name_id=name_id,
                meteringpoint_ids=METERINGPOINT_IDS
            )
            assert error.status_code == status_code

    def test__given_invalid_response_body__raise_decode_error(
            self,
            request_mocker: requests_mock,
    ):
        """
        Raise http error when failing to deserialize response body.

        When failing to deserialize response body,
        test that the function raises DecodeError.

        :param request_mocker: mock_used to mock datasync api.
        :type request_mocker: requests_mock
        """
        # -- Arrange ---------------------------------------------------------
        base_url = "http://foo.com"
        name_id = "test"
        status_code = 200

        # Mock datasync HTTP Response that returns a unexpected reponse body
        request_mocker.post(
            f'{base_url}/MeteringPoint/createRelation',
            json={
                "INVALID_KEY": "INVALID_VALUE"
            },
            status_code=status_code,
        )

        uut = DataSyncHttpClient(base_url, "foo-token")

        # -- Act/Assert ------------------------------------------------------

        with pytest.raises(
            DataSyncHttpClient.DecodeError,
            match="Failed to decode response body."
        ) as error:
            uut.create_meteringpoint_relationships(
                name_id=name_id,
                meteringpoint_ids=METERINGPOINT_IDS
            )
            assert error.status_code == status_code
