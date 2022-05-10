# Standard Library
from dataclasses import dataclass
from typing import List

# Third party
import requests

# First party
from origin.models.meteringpoints import (
    MeteringPoint,
)
from origin.serialize import simple_serializer


@dataclass
class CreateMeteringpointRelationshipResults:
    """Result when creating a meteringpoint relationship."""

    failed_relationships: List[str]
    successful_relationships: List[str]


class DataSyncHttpClient:
    """
    A httpclient for communicating with the data-sync service.

    Each HttpClient should use the internal_token provided by the
    individual user.

    :param base_url: base url of the datasync class.
        :type base_url: str
        :param internal_token: The bearer internal_token used
               for authentication.
        :type internal_token: str
    """

    class HttpError(Exception):
        """Raised when http requests fails."""

        def __init__(self, status_code: int, message: str) -> None:
            self.message = message
            self.status_code = status_code

            super().__init__(self.message)

    class DecodeError(Exception):
        """Raised when http requests fails."""

        pass

    def __init__(self, base_url: str, internal_token: str):
        self.base_url = base_url
        self.internal_token = internal_token

    def get_meteringpoints_by_tin(self, tin: str) -> List[MeteringPoint]:
        """Return meteringpoints with relations to given tin."""

        uri = f'{self.base_url}/MeteringPoint/GetByTin/{tin}'

        response = requests.get(uri, headers=self._getHeaders())

        if response.status_code == 404:
            raise DataSyncHttpClient.HttpError(
                status_code=response.status_code,
                message="User with tin not found."
            )
        elif response.status_code != 200:
            raise DataSyncHttpClient.HttpError(
                status_code=response.status_code,
                message="Failed to fetch meteringpoints by tin."
            )

        data = response.json()

        @dataclass
        class ExpectedResponse:
            """Expected result from http request."""

            meteringpoints: List[MeteringPoint]

        try:
            decoded = simple_serializer.deserialize(
                {"meteringpoints": data},
                ExpectedResponse,
                True,
            )
        except:   # noqa: E722
            raise DataSyncHttpClient.DecodeError(
                "Failed to decode meteringpoints."
            )

        return decoded.meteringpoints

    def create_meteringpoint_relationships(
        self,
        name_id: str,
        meteringpoint_ids: List[str]
    ) -> CreateMeteringpointRelationshipResults:
        """
        Create relationship between name_id and list of meteringpoints.

        :param name_id: Either a tin or ssn
        :type name_id: str
        :param meteringpoint_ids: List of meteringpoint ids / GSRN
        :type meteringpoint_ids: List[str]
        :raises DataSyncHttpClient.HttpError: Raised when faced http error
        :raises DataSyncHttpClient.DecodeError: Raised when failing to
            deserialize responsebody
        :return: Returns an object with lists of relationships
            which failed and succeeded
        :rtype: CreateMeteringpointRelationshipResults
        """
        # TODO: CHECK CORRECT PATH
        uri = f'{self.base_url}/MeteringPoint/createRelation'

        @dataclass
        class CreateMeteringpointRelationshipResult:
            """Result when creating a meteringpoint relationship."""

            meteringpointId: str
            relationshipCreated: bool

        @dataclass
        class ExpectedResponse:
            """Expected result from http request."""

            result: List[CreateMeteringpointRelationshipResult]

        response = requests.post(
            url=uri,
            headers=self._getHeaders(),
            data={
                "name_id": name_id,
                "meteringpoint_ids": meteringpoint_ids,
            }
        )

        if response.status_code != 200:
            raise DataSyncHttpClient.HttpError(
                status_code=response.status_code,
                message="Failed to create meteringpoint relationship."
            )

        data = response.json()

        try:
            decoded: ExpectedResponse = simple_serializer.deserialize(
                {"result": data},
                ExpectedResponse,
                True,
            )
        except:   # noqa: E722
            raise DataSyncHttpClient.DecodeError(
                "Failed to decode response body."
            )

        create_mp_relationship_results = CreateMeteringpointRelationshipResults(  # noqa E501
            successful_relationships=[],
            failed_relationships=[],
        )

        for meteringpoint_relation_result in decoded.result:
            gsrn = meteringpoint_relation_result.meteringpointId
            if meteringpoint_relation_result.relationshipCreated:
                create_mp_relationship_results.successful_relationships.append(
                    gsrn)
            else:
                create_mp_relationship_results.failed_relationships.append(
                    gsrn)

        return create_mp_relationship_results

    def _getHeaders(self):
        headers = {
            "Authorization": f'Bearer: {self.internal_token}'
        }

        return headers
