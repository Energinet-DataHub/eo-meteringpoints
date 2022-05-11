from typing import List, Optional
from dataclasses import dataclass

from origin.api import Endpoint, Context
from origin.models.meteringpoints import MeteringPoint
from meteringpoints_shared.config import DATASYNC_BASE_URL
from meteringpoints_shared.datasync_httpclient import DataSyncHttpClient


class CreateMeteringPointRelations(Endpoint):
    """Returns details about a single MeteringPoint."""

    @dataclass
    class Request:
        """TODO."""

        tin: Optional[str]
        ssn: Optional[str] = None

    @dataclass
    class Response:
        """TODO."""

        success: bool

    def handle_request(
            self,
            request: Request,
            context: Context,
    ) -> Response:
        """Handle HTTP request."""

        http_client = DataSyncHttpClient(
            base_url=DATASYNC_BASE_URL,
            internal_token=context.internal_token_encoded,
        )

        try:
            meteringpoint_ids = get_meteringpoint_ids(
                datasync_http_client=http_client,
                request=request,
            )

            create_meteringpoint_relationships(
                datasync_http_client=http_client,
                request=request,
                meteringpoint_ids=meteringpoint_ids,
            )

        except Exception as error:
            print(f'failed to create relationship: {error}')
            return self.Response(
                success=False,
            )

        return self.Response(
            success=True,
        )

# --- Helper functions -------------------------------------


def get_meteringpoint_ids(
    datasync_http_client: DataSyncHttpClient,
    request: CreateMeteringPointRelations.Request
) -> List[str]:
    """
    Return list of meteringpoint ids, belonging to user.


    :param datasync_http_client: Datasync http client
    :type datasync_http_client: DataSyncHttpClient
    :param request: Request object
    :type request: CreateMeteringPointRelations.Request
    :raises Exception: Raises exception on any kind of error
    :return: List of meteringpoint ids
    :rtype: List[str]
    """
    meteringpoints: List[str] = []

    if request.tin:
        meteringpoints = datasync_http_client.get_meteringpoints_by_tin(
            request.tin
        )
    elif request.ssn:
        # IMPLEMENT THIS
        print("httpClient.get_meteringpoints_by_ssn() not implemented")
        pass
    else:
        raise Exception(
            "Either request.tin or request.ssn needs to be defined"
        )

    meteringpoint_ids = [MeteringPoint(gsrn=mp) for mp in meteringpoints]

    if not meteringpoint_ids:
        raise Exception("No meteringpoints found for user")

    return meteringpoint_ids


def create_meteringpoint_relationships(
    datasync_http_client: DataSyncHttpClient,
    request: CreateMeteringPointRelations.Request,
    meteringpoint_ids: List[str]
) -> bool:
    """
    Create relationships between user and provided meteringpoint.

    Calls datasync service to create relationships between meterinpoints
    and user.

    :param datasync_http_client: DataSync http client
    :type datasync_http_client: DataSyncHttpClient
    :param request: Request object
    :type request: CreateMeteringPointRelations.Request
    :param meteringpoint_ids: Meteringpoint ids(gsrn)
    :type meteringpoint_ids: List[str]
    :raises Exception: Raised on any error
    :return: True if successful False on error
    :rtype: bool
    """
    if request.tin:
        name_id = request.tin
    elif request.ssn:
        name_id = request.ssn
    else:
        raise Exception(
            "Either request.tin or request.ssn needs to be defined"
        )

    meteringpoint_relationship_results = datasync_http_client.\
        create_meteringpoint_relationships(
            name_id=name_id,
            meteringpoint_ids=meteringpoint_ids,
        )

    if len(meteringpoint_relationship_results.failed_relationships) != 0:
        fail_count = len(
            meteringpoint_relationship_results.failed_relationships
        )
        mp_count = len(meteringpoint_ids)

        raise Exception(
            f'Failed to create {fail_count}/{mp_count} relationships'
        )

    return True
