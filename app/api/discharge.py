#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author:Tao Yimin
# Time  :2019/10/22 19:23
from flask_restful import marshal_with, Resource, fields, reqparse

from app.api import api
from app.model import auth
from app.model.discharge import Discharge
from app.model.enter import Enter
from app.model.monitor import Monitor
from app.model.report import Report
from app.util.common import metric

discharge_detail_fields = {
    'dischargeId': fields.String,
    'enterId': fields.String,
    'dischargeName': fields.String,
    'dischargeShortName': fields.String,
    'dischargeAddress': fields.String,
    'dischargeNumber': fields.String,
    'dischargeTypeStr': fields.String,
    'denoterInstallTypeStr': fields.String,
    'dischargeRuleStr': fields.String,
    'outletTypeStr': fields.String,
    'longitude': fields.String,
    'latitude': fields.String
}

discharge_item_fields = {
    'dischargeId': fields.String,
    'dischargeName': fields.String,
    'dischargeShortName': fields.String,
    'dischargeAddress': fields.String
}

discharge_list_fields = {
    'total': fields.Integer(attribute=lambda p: p.total),
    'currentPage': fields.Integer(attribute=lambda p: p.page),
    'pageSize': fields.Integer(attribute=lambda p: p.per_page),
    'hasNext': fields.Boolean(attribute=lambda p: p.has_next),
    'list': fields.List(fields.Nested(discharge_item_fields), attribute=lambda p: p.items)
}


class DischargeResource(Resource):
    decorators = [auth.login_required]

    @metric
    @marshal_with(discharge_detail_fields)
    def get(self, discharge_id=None, monitor_id=None, report_id=None):
        if discharge_id:
            return Discharge.query.get_or_abort(discharge_id)
        elif monitor_id:
            return Monitor.query.get_or_abort(monitor_id).discharge
        elif report_id:
            return Report.query.get_or_abort(report_id).discharge


class DischargeCollectionResource(Resource):
    decorators = [auth.login_required]

    @metric
    @marshal_with(discharge_list_fields)
    def get(self, enter_id=None):
        parser = reqparse.RequestParser()
        parser.add_argument('currentPage', type=int, default=1)
        parser.add_argument('pageSize', type=int, default=20)
        args = parser.parse_args()
        current_page = args.pop('currentPage')
        page_size = args.pop('pageSize')
        if enter_id:
            query = Enter.query.get_or_abort(enter_id).discharges
        else:
            query = Discharge.query.filter_by_user()
        return query.order_by(Discharge.dischargeId) \
            .filter_by_args(args) \
            .paginate(current_page, page_size, False)


api.add_resource(DischargeResource, '/discharges/<int:discharge_id>', '/monitors/<int:monitor_id>/discharge',
                 '/reports/<int:report_id>/discharge')
api.add_resource(DischargeCollectionResource, '/discharges', '/enters/<int:enter_id>/discharges')
