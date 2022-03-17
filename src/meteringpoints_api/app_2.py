from dataclasses import dataclass

from meteringpoints_api import endpoints
from .dependencies import RequiresScope
from fastapi import Depends, FastAPI


class TestEndpoint(endpoints):
    """Look up many Measurements, optionally filtered and ordered."""

    @dataclass
    class Response:
        """TODO."""

        success: bool

    async def handle_request(
        self,
        name: str,
    ) -> Response:
        """Handle HTTP request."""

        return TestEndpoint.Response(success=True)


def create_app() -> FastAPI:
    """Create a new instance of the application."""

    app = FastAPI(
        title='MeteringPoints API',
    )

    app.add_api_route(
        path='/query-checker/',
        endpoint=TestEndpoint().handle_request,
        methods=['GET'],
        dependencies=[
            Depends(RequiresScope(scope='meteringpoints.read')),
        ]
    )
    return app


myapp = create_app()
