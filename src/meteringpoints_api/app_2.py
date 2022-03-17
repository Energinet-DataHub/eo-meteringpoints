from dataclasses import dataclass

from origin.api.endpoint import Endpoint
from .dependencies import RequiresScope
from fastapi import Depends, FastAPI
from origin.tokens import TokenEncoder
from origin.models.auth import InternalToken


class TestEndpoint(Endpoint):
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


# token_encoder = TokenEncoder(
#     schema=InternalToken,
#     secret='123',
# )


async def get_token_encoder() -> TokenEncoder[InternalToken]:
    return TokenEncoder(
        schema=InternalToken,
        secret='123',
    )


def create_app() -> FastAPI:
    """Create a new instance of the application."""

    app = FastAPI(
        title='MeteringPoints API',
        dependencies=[
            Depends(get_token_encoder),
        ],
    )

    app.add_api_route(
        path='/query-checker/',
        endpoint=TestEndpoint().handle_request,
        methods=['GET'],
        dependencies=[
            Depends(RequiresScope(scope='meteringpoints.read')),
        ],
    )

    return app


myapp = create_app()
