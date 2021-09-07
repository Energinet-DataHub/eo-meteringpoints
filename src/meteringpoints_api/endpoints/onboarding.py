from dataclasses import dataclass

from energytt_platform.api import Endpoint, Context
from energytt_platform.bus import messages as m, topics as t

from meteringpoints_shared.db import db
from meteringpoints_shared.bus import broker


# class OnboardMeteringPointsFromWebAccessCode(Endpoint):
#     """
#     TODO
#     """
#
#     @dataclass
#     class Request:
#         gsrn: str
#         web_access_code: str
#
#     @dataclass
#     class Response:
#         success: bool
#
#     @db.session()
#     def handle_request(
#             self,
#             request: Request,
#             context: Context,
#             session: db.Session,
#     ) -> Response:
#         """
#         Handle HTTP request.
#         """
#         broker.publish(
#             topic=t.METERINGPOINTS_COMMANDS,
#             msg=m.ImportMeteringPoints(
#                 subject=context.token.subject,
#                 params={
#                     m.ImportMeteringPoints.GSRN: request.gsrn,
#                     m.ImportMeteringPoints.WEB_ACCESS_CODE: request.web_access_code,
#                 },
#             ),
#         )
#
#         return self.Response(
#             success=True,
#         )


class OnboardMeteringPointsFromCPR(Endpoint):
    """
    TODO
    """

    @dataclass
    class Request:
        cpr: str

    @dataclass
    class Response:
        success: bool

    @db.session()
    def handle_request(
            self,
            request: Request,
            context: Context,
            session: db.Session,
    ) -> Response:
        """
        Handle HTTP request.
        """
        if context.is_authorized:
            pass

        broker.publish(
            topic=t.METERINGPOINTS_COMMANDS,
            msg=m.ImportMeteringPoints(
                subject=context.token.subject,
                params={
                    m.ImportMeteringPoints.CPR: request.cpr,
                },
            ),
        )

        return self.Response(
            success=True,
        )


class OnboardMeteringPointsFromCVR(Endpoint):
    """
    TODO
    """

    @dataclass
    class Request:
        cvr: str

    @dataclass
    class Response:
        success: bool

    @db.session()
    def handle_request(
            self,
            request: Request,
            context: Context,
            session: db.Session,
    ) -> Response:
        """
        Handle HTTP request.
        """
        broker.publish(
            topic=t.METERINGPOINTS_COMMANDS,
            msg=m.ImportMeteringPoints(
                subject=context.token.subject,
                params={
                    m.ImportMeteringPoints.CVR: request.cvr,
                },
            ),
        )

        return self.Response(
            success=True,
        )
