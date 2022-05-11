# Standard Library
from dataclasses import dataclass
from typing import List, TypeVar

# Third party
import requests
from requests import Response

# First party
from origin.models.meteringpoints import (
    MeteringPoint,
)
from origin.serialize import simple_serializer

from meteringpoints_shared.generic_httpclient import GenericHttpClient


@dataclass
class CreateMeteringpointRelationshipResults:
    """Result when creating a meteringpoint relationship."""

    failed_relationships: List[str]
    successful_relationships: List[str]


class DataSyncHttpClient(GenericHttpClient):
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

    def get_meteringpoints_by_tin(self, tin: str) -> List[MeteringPoint]:
        """Return meteringpoints with relations to given tin."""

        uri = f'{self.base_url}/MeteringPoint/GetByTin/{tin}'

        response = requests.get(uri, headers=self._getHeaders())

        self._raiseHttpErrorIf(response, 404, "User with tin not found.")
        self._raiseHttpErrorIfNot(
            response, 200, "Failed to fetch meteringpoints by tin.")

        meteringpoints = self._decode_list_response(
            response=response,
            schema=MeteringPoint,
        )

        return meteringpoints

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

        response = requests.post(
            url=uri,
            headers=self._getHeaders(),
            data={
                "name_id": name_id,
                "meteringpoint_ids": meteringpoint_ids,
            }
        )

        self._raiseHttpErrorIfNot(
            response, 200, "Failed to create meteringpoint relationship.")

        mapped = self._map_create_meteringpoint_relationships(response)

        return mapped

    # ------------------ private methods ------------------

    def _map_create_meteringpoint_relationships(self, response: Response) -> CreateMeteringpointRelationshipResults:
        """
        Maps the datasync response to own custom response.

        :param response: requests Http response
        :type response: Response
        :return: Returns new function response
        :rtype: CreateMeteringpointRelationshipResults
        """

        @dataclass
        class CreateMeteringpointRelationshipResult:
            """Result when creating a meteringpoint relationship."""

            meteringpointId: str
            relationshipCreated: bool

        created_relationships = self._decode_list_response(
            response=response,
            schema=CreateMeteringpointRelationshipResult,
        )

        create_mp_relationship_results = CreateMeteringpointRelationshipResults(  # noqa E501
            successful_relationships=[],
            failed_relationships=[],
        )

        for meteringpoint_relation_result in created_relationships:
            gsrn = meteringpoint_relation_result.meteringpointId
            if meteringpoint_relation_result.relationshipCreated:
                create_mp_relationship_results.successful_relationships.append(
                    gsrn)
            else:
                create_mp_relationship_results.failed_relationships.append(
                    gsrn)

        return create_mp_relationship_results
