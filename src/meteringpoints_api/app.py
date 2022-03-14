

from .endpoints import GetMeteringPointList, GetMeteringPointDetails
from fastapi import FastAPI

def create_app() -> FastAPI:
    """Create a new instance of the application."""

    app = FastAPI(
        title='MeteringPoints API',
    )

    app.add_api_route(
        path='/list',
        method='POST',
        endpoint=GetMeteringPointList.handle_request,
        # guards=[ScopedGuard('meteringpoints.read')],
        response_model=GetMeteringPointList.Response
    )

    app.add_api_route(
        path='/details',
        method='GET',
        endpoint=GetMeteringPointDetails.handle_request,
        # guards=[ScopedGuard('meteringpoints.read')],
        response_model=GetMeteringPointDetails.Response
    )

    return app
