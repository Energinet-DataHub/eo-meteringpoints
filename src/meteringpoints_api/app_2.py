from dataclasses import dataclass
from .dependencies import ScopedGuard, TokenContext
from fastapi import Depends, FastAPI, Request
from origin.api import Endpoint
from origin.models.auth import InternalToken
from origin.tokens import TokenEncoder
from datetime import datetime, timezone, timedelta
import uvicorn

token_encoder = TokenEncoder(
    schema=InternalToken,
    secret='123',
)

token = InternalToken(
    issued=datetime.now(tz=timezone.utc),
    expires=datetime.now(timezone.utc) + timedelta(hours=24),
    actor='foo',
    subject='bar',
    scope=['meteringpoints.read'],
)


opaque_token = token_encoder.encode(token)
# print(opaque_token)


def auth_required(handler):
    async def wrapper(request: Request, *args, **kwargs):
        print('teeeeeeeeeeeeeeeeeest', request.headers)
        return await handler(*args, **kwargs)

    # Fix signature of wrapper
    import inspect
    wrapper.__signature__ = inspect.Signature(
        parameters = [
            # Use all parameters from handler
            *inspect.signature(handler).parameters.values(),

            # Skip *args and **kwargs from wrapper parameters:
            *filter(
                lambda p: p.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD),
                inspect.signature(wrapper).parameters.values()
            )
        ],
        return_annotation = inspect.signature(handler).return_annotation,
    )

    return wrapper


class TestEndpoint(Endpoint):
    """Look up many Measurements, optionally filtered and ordered."""

    @dataclass
    class Response:
        """TODO."""

        success: bool

    @auth_required
    async def handle_request(
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
        endpoint=TestEndpoint.handle_request,
        methods=['GET'],
        dependencies=[
            Depends(ScopedGuard(scopes=['meteringpoints.read'])),
        ]
    )
    return app


myapp = create_app()
uvicorn.run(myapp, host='0.0.0.0', port=8000)