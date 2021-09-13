from energytt_platform.api import Application, ScopedGuard
from energytt_platform.api.endpoints import HealthCheck

from meteringpoints_shared.config import TOKEN_SECRET

from .endpoints import (
    GetMeteringPointList,
    GetMeteringPointDetails,
    # OnboardMeteringPointsFromWebAccessCode,
    # OnboardMeteringPointsFromCPR,
    # OnboardMeteringPointsFromCVR,
)


def create_app() -> Application:
    """
    Creates a new instance of the application.
    """
    app = Application(
        name='MeteringPoints API',
        secret=TOKEN_SECRET
    )

    app.add_endpoint(
        method='POST',
        path='/list',
        endpoint=GetMeteringPointList(),
        guards=[ScopedGuard('meteringpoints.read')]
    )

    app.add_endpoint(
        method='GET',
        path='/details',
        endpoint=GetMeteringPointDetails(),
        guards=[ScopedGuard('meteringpoints.read')]
    )

    app.add_endpoint(
        method='GET',
        path='/health',
        endpoint=HealthCheck(),
    )

    # app.add_endpoint(
    #     method='POST',
    #     path='/onboard/web-access-code',
    #     endpoint=OnboardMeteringPointsFromWebAccessCode(),
    # )

    # app.add_endpoint(
    #     method='POST',
    #     path='/onboard/cpr',
    #     endpoint=OnboardMeteringPointsFromWebAccessCode(),
    # )

    # app.add_endpoint(
    #     method='POST',
    #     path='/onboard/cpr',
    #     endpoint=OnboardMeteringPointsFromCPR(),
    # )

    # app.add_endpoint(
    #     method='POST',
    #     path='/onboard/cvr',
    #     endpoint=OnboardMeteringPointsFromCVR(),
    # )

    return app
