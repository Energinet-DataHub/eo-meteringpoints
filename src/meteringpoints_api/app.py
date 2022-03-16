

from meteringpoints_api.dependencies import token
from .endpoints import GetMeteringPointList, GetMeteringPointDetails
from fastapi import Depends, FastAPI

def create_app() -> FastAPI:
    """Create a new instance of the application."""

    app = FastAPI(
        title='MeteringPoints API',
    )

    app.add_api_route(
        path='/list',
        endpoint=GetMeteringPointList.handle_request,
        # guards=[ScopedGuard('meteringpoints.read')],
        response_model=GetMeteringPointList.Response,
        dependencies=[Depends(token('meteringpoints.read'))]
    )

    # app.add_api_route(
    #     path='/details',
    #     method='GET',
    #     endpoint=GetMeteringPointDetails.handle_request,
    #     # guards=[ScopedGuard('meteringpoints.read')],
    #     response_model=GetMeteringPointDetails.Response
    # )

    return app
