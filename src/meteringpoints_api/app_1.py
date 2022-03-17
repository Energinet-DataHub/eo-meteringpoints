from dataclasses import dataclass
from .dependencies import ScopedGuard, TokenContext
from fastapi import Depends, FastAPI, Request
from origin.api import Endpoint
from origin.models.auth import InternalToken
from origin.tokens import TokenEncoder
from datetime import datetime, timezone, timedelta
import inspect
import uvicorn
from functools import wraps

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


def fastapi_request_wrapper(handler):
    async def wrapper(fastapi_request: Request, *args, **kwargs):
        print('fastapi_request_wrapper')

        # add fastapi_request object to request if handler requires it
        if 'fastapi_request' in inspect.getfullargspec(handler)[0]:
            kwargs['fastapi_request'] = fastapi_request

        result = await handler(*args, **kwargs)

        return result

    # Fix signature of wrapper

    # Get original function signature
    signature = inspect.signature(handler)

    # Get the function parameters
    parameters = signature.parameters

    # Parameters from the handler
    handler_params = inspect.signature(handler).parameters.values()

    # Parameters from wrapper with *args and **kwargs removed
    wrapper_parms = filter(
        lambda p: p.kind not in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD
        ),
        inspect.signature(wrapper).parameters.values()
    )

    all_params = [
        *handler_params,
    ]

    # if the handler does not require fast
    if 'fastapi_request' not in parameters.keys():
        all_params += wrapper_parms

    wrapper.__signature__ = inspect.Signature(
        parameters=all_params,
        return_annotation=inspect.signature(handler).return_annotation,
    )

    return wrapper


def requires_token(handler):

    async def wrapper(fastapi_request: Request, *args, **kwargs):
        print('token_required_wrapper', token)

        return await handler(*args, **kwargs)

    return wrapper


class TestEndpoint(Endpoint):
    """Look up many Measurements, optionally filtered and ordered."""

    @dataclass
    class Response:
        """TODO."""

        success: bool

    # @requires_token
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
            # Depends(ScopedGuard(scopes=['meteringpoints.read'])),
        ]
    )
    return app


myapp = create_app()
# uvicorn.run(myapp, host='0.0.0.0', port=8000)
