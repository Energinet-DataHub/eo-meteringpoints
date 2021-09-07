# from typing import List, Optional
# from dataclasses import dataclass, field
#
# from energytt_platform.api import Endpoint, Context
# from energytt_platform.bus import messages as m, topics as t
# from energytt_platform.models.meteringpoints import MeteringPoint
#
# from meteringpoints_shared.db import db
# from meteringpoints_shared.bus import broker
# from meteringpoints_shared.queries import MeteringPointQuery
# from meteringpoints_shared.models import \
#     MeteringPointFilters, MeteringPointOrdering
#
#
# class GetMeteringPointList(Endpoint):
#     """
#     Looks up many Measurements, optionally filtered and ordered.
#     """
#
#     @dataclass
#     class Request:
#         offset: int
#         limit: int
#         filters: Optional[MeteringPointFilters] = field(default=None)
#         ordering: Optional[MeteringPointOrdering] = field(default=None)
#
#     @dataclass
#     class Response:
#         success: bool
#         total: int
#         meteringpoints: List[MeteringPoint]
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
#         subject = context.get_subject(required=True)
#
#         query = MeteringPointQuery(session) \
#             .is_accessible_by(subject)
#
#         if request.filters:
#             query = query.apply_filters(request.filters)
#
#         if request.ordering:
#             results = query.apply_ordering(request.ordering)
#         else:
#             results = query
#
#         results = results \
#             .offset(request.offset) \
#             .limit(request.limit)
#
#         # if request.ordering:
#         #     results = results.apply_ordering(request.ordering)
#
#         return self.Response(
#             success=True,
#             total=query.count(),
#             meteringpoints=results.all(),
#         )
#
#
# class GetMeteringPointDetails(Endpoint):
#     """
#     Returns details about a single MeteringPoint.
#     """
#
#     @dataclass
#     class Request:
#         gsrn: str
#
#     @dataclass
#     class Response:
#         success: bool
#         meteringpoint: Optional[MeteringPoint]
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
#         meteringpoint = MeteringPointQuery(session) \
#             .is_accessible_by(context.token.subject) \
#             .has_gsrn(request.gsrn) \
#             .one_or_none()
#         # meteringpoint = MeteringPointQuery(session) \
#         #     .has_gsrn(request.gsrn) \
#         #     .one_or_none()
#
#         return self.Response(
#             success=meteringpoint is not None,
#             meteringpoint=meteringpoint,
#         )
#
#
# class OnboardMeteringPoints(Endpoint):
#     """
#     Request system to onboard one or more MeteringPoints.
#     """
#
#     @dataclass
#     class Request:
#         """
#         TODO Validate client only provides AT LEAST one of the following inputs:
#         TODO Validate client only provides EXACTLY one of the following inputs:
#         """
#         gsrn: Optional[str] = field(default=None)
#         cpr: Optional[str] = field(default=None)
#         cvr: Optional[str] = field(default=None)
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
#         params = {}
#
#         if request.gsrn:
#             params[m.ImportMeteringPoints.GSRN] = request.gsrn
#         elif request.cpr:
#             params[m.ImportMeteringPoints.CPR] = request.cpr
#         elif request.cvr:
#             params[m.ImportMeteringPoints.CVR] = request.cvr
#         else:
#             raise RuntimeError('TODO')
#
#         broker.publish(
#             topic=t.METERINGPOINTS_COMMANDS,
#             msg=m.ImportMeteringPoints(
#                 subject=context.token.subject,
#                 params=params,
#             )
#         )
#
#         return self.Response(
#             success=True,
#         )
