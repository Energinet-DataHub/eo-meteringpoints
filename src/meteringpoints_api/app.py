from origin.api import Application, ScopedGuard

from meteringpoints_shared.config import INTERNAL_TOKEN_SECRET

from .endpoints import GetMeteringPointDetails, GetMeteringPointList


def create_app() -> Application:
    """Create a new instance of the application."""

    app = Application.create(
        name='MeteringPoints API',
        secret=INTERNAL_TOKEN_SECRET,
        health_check_path='/health',
    )

    app.add_endpoint(
        method='GET',
        path='/list',
        endpoint=GetMeteringPointList(),
        guards=[ScopedGuard('meteringpoints.read')]
    )

    app.add_endpoint(
        method='GET',
        path='/details',
        endpoint=GetMeteringPointDetails(),
        guards=[ScopedGuard('meteringpoints.read')],
    )

    return app
