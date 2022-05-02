from origin.api import Application, ScopedGuard

from meteringpoints_shared.config import INTERNAL_TOKEN_SECRET

from .endpoints import GetMeteringPointDetails
from .fake_data import FakeGetMeteringPointList


def create_app() -> Application:
    """Create a new instance of the application."""

    app = Application.create(
        name='MeteringPoints API',
        secret=INTERNAL_TOKEN_SECRET,
        health_check_path='/health',
    )

    # guards=[ScopedGuard('meteringpoints.read')], has been remove due to
    # test of endpoint when the meteringpoints does not have a scope.
    app.add_endpoint(
        method='GET',
        path='/list',
        endpoint=FakeGetMeteringPointList(),
    )

    app.add_endpoint(
        method='GET',
        path='/details',
        endpoint=GetMeteringPointDetails(),
        guards=[ScopedGuard('meteringpoints.read')],
    )

    return app
