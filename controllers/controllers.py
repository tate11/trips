# -*- coding: utf-8 -*-
from odoo import http

# class SavorFleet(http.Controller):
#     @http.route('/savor_fleet/savor_fleet/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/savor_fleet/savor_fleet/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('savor_fleet.listing', {
#             'root': '/savor_fleet/savor_fleet',
#             'objects': http.request.env['savor_fleet.savor_fleet'].search([]),
#         })

#     @http.route('/savor_fleet/savor_fleet/objects/<model("savor_fleet.savor_fleet"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('savor_fleet.object', {
#             'object': obj
#         })