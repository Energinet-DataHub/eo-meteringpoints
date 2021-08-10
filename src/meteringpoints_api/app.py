from energytt_platform.api import Application

from .endpoints import GetMeasurementList


def create_app() -> Application:
    """
    Creates a new instance of the application.
    """
    return Application.create(
        name='MeteringPoints API',
        health_check_path='/health',
        endpoints=(
            ('GET', '/details', GetMeasurementList()),
            ('POST', '/list', GetMeasurementList()),
        )
    )
