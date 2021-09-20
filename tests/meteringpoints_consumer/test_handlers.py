from datetime import datetime, timedelta, timezone

from typing import List

import pytest

from unittest.mock import patch
from flask.testing import FlaskClient


from energytt_platform.bus.messages.delegates \
    import MeteringPointDelegateGranted
from energytt_platform.models.delegates import MeteringPointDelegate


from energytt_platform.models.auth import InternalToken
from energytt_platform.tokens import TokenEncoder

from energytt_platform.bus.messages.meteringpoints import MeteringPointUpdate
from energytt_platform.bus import messages as m
from meteringpoints_consumer.handlers import dispatcher

from energytt_platform.models.tech import Technology, TechnologyType
from energytt_platform.models.common import EnergyDirection
from energytt_platform.models.meteringpoints import MeteringPoint

from meteringpoints_shared.db import db
from meteringpoints_shared.models import DbMeteringPoint, DbTechnology
from meteringpoints_shared.queries import MeteringPointQuery


'''
    TODO:
        - Test for single point added
            - single_point_added_with_technology
            - single_point_added_with_address
            - single_point_added_with_sector
            - single_point_added_with_all_properties

        - Test for single point updated
            - single_point_technology_updated
            - single_point_address_updated
            - single_point_sector_updated
            - single_point_all_properties_updated

        - Test for multiple points added
            - single_point_added_with technology
            - single_point_added_with_address
            - single_point_added_with_sector
            - single_point_added_with_all_properties


        ### /list requests
        - Test scope
            - using_correct_scope__point_fetched
            - using_incorrect_scope__no_point_fetched

        - Test filters parameter
            - Valid filters
                - filter_by_single_gsrn__single_point_fetched
                - filter_by_multiple_gsrn__muliple_points_fetched

                - filter_by_single_type__single_point_fetched
                - filter_by_multiple_types__multiple_points_fetched

                - filter_by_single_sector__single_point_fetched
                - filter_by_multiple_sectors__multiple_points_fetched

                - filter_by_gsrn_type__points_fetched
                - filter_by_gsrn_sector__points_fetched
                - filter_by_gsrn_type_sector__points_fetched

            - Invalid filters
                - filter_by_invalid_gsrn__expected_error
                - filter_by_invalid_sector__expected_error
                - filter_by_invalid_type__expected_error

        - Test offset parameter
            - valid_offset__points_fetched_with_offset
            - no_offset_provided__points_fetched
            - invalid_offset_type__error_expected
            - invalid_negative_offset__error_expected

        - Test limit parameter
            - valid_limit__points_limited
            - invalid_negative_limit__error_expected
            - invliad_limit_type__error_expected
            - no_limit_provided__default_limit_used

        - Test bearer token
            - no_token__expected_error
            - expired_token__expected_error
            - invalid_token__expected_error
            - invalid_scope__expected_error
            - unknown_subject__expected_error
            - invalid_signed_token__expected_error

            - using_matched_subject__points_fetched
            - using_no_matched_subject__no_points_fetched
            - using_partial_matched_subject__partial_points_fetched
            - using_without_subject__no_points_fetched

'''


GSRN_ARR = [
    "GSRN1",
    "GSRN2",
    "GSRN3",
    "GSRN4",
    "GSRN5",
    "GSRN6",
    "GSRN7",
]

SECTOR_ARR = ["DK1", "DK2", "DK3", "DK4", "DK5", "DK6", "DK7"]

METERPING_POINT_TYPES = [
    EnergyDirection.consumption,
    EnergyDirection.production,
]

TECH_CODES = ["100", "200", "300", "400", "500", "600", "700"]
FUEL_CODES = ["101", "201", "301", "401", "501", "601", "701"]

TECHNOLOGY_TYPES = [
    TechnologyType.coal,
    TechnologyType.nuclear,
    TechnologyType.solar,
    TechnologyType.wind,
]


technology = Technology(
    type=TechnologyType.coal,
    tech_code='123',
    fuel_code='456',
)


metering_point1 = MeteringPoint(
    gsrn='GSRN1',
    sector='DK1',
    type=EnergyDirection.consumption,
)


def get_technology(number: int) -> Technology:
    """
    Returns a new technology
    """
    technology_types_count = len(TECHNOLOGY_TYPES)
    tech_codes_count = len(TECH_CODES)
    fuel_codes_count = len(FUEL_CODES)

    return Technology(
        type=TECHNOLOGY_TYPES[number % technology_types_count],
        tech_code=TECH_CODES[number % tech_codes_count],
        fuel_code=fuel_codes_count[number % FUEL_CODES],
    )


def get_metering_point(number: int) -> List[MeteringPoint]:
    """
    Returns a new metering_point
    """
    gsrn_arr_count = len(GSRN_ARR)
    sector_arr_count = len(SECTOR_ARR)
    technology_types_count = len(TECHNOLOGY_TYPES)

    technology = get_technology(number)

    if number > gsrn_arr_count:
        raise RuntimeError("Do not have enough unique gsrn")

    return MeteringPoint(
        gsrn=GSRN_ARR[number % gsrn_arr_count],
        sector=TECH_CODES[number % sector_arr_count],
        type=TECHNOLOGY_TYPES[number % technology_types_count],
        technology=technology(number)
    )


class TestMeteringPointUpdate:

    def test__metering_point_update__single_metering_point_added(
            self,
            session: db.Session,
            client: FlaskClient,
            token_encoder: TokenEncoder,
    ):
        """
        TODO Describe test...
        """

        # -- Arrange ---------------------------------------------------------

        subject = "foo"

        token = token_encoder.encode(InternalToken(
            issued=datetime.now(timezone.utc),
            expires=datetime.now(timezone.utc) + timedelta(hours=5),
            actor="foo",
            subject=subject,
            scope=[
                "meteringpoints.read",
            ]
        ))

        client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer: ' + token

        # -- Act -------------------------------------------------------------

        dispatcher(MeteringPointUpdate(
            meteringpoint=metering_point1
        ))

        dispatcher(MeteringPointDelegateGranted(
            delegate=MeteringPointDelegate(
                subject=subject,
                gsrn=metering_point1.gsrn,
            )
        ))

        response = client.post('/list', json={
            'offset': 0,
            'limit': 10,
            'filters':
                {
                    'gsrn': [metering_point1.gsrn],
                },
        })

        response_json = response.get_json()

        # -- Assert ----------------------------------------------------------

        assert response.status_code == 200
        assert len(response_json['meteringpoints']) == 1

        meterpoint_point = response_json['meteringpoints'][0]

        assert meterpoint_point["type"] == metering_point1.type.value
        assert meterpoint_point["sector"] == metering_point1.sector
        assert meterpoint_point["technology"] == metering_point1.technology
        assert meterpoint_point["address"] == metering_point1.address
