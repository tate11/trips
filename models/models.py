# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

from datetime import datetime, date, timedelta

class Employee(models.Model):
    _inherit = 'hr.employee'

    private_address_textual = fields.Text(_('Address'))

    employee_number = fields.Char(_('Employee Number'))

    employment_start = fields.Date(_('Employed since'), required=True)
    employment_end = fields.Date(_('Employed until'))

    @api.multi
    def _trips_count(self):
        for each in self:
            trip_ids = self.env['trips.trip'].search([('driver', '=', each.id)])
            each.trips_count = len(trip_ids)

    @api.multi
    def trips_view(self):
        self.ensure_one()
        domain = [
            ('driver', '=', self.id)]
        return {
            'name': _('Trips'),
            'domain': domain,
            'res_model': 'trips.trip',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form,calendar,pivot',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create New Trip
                        </p>'''),
            'limit': 80,
            'context': "{'default_driver': %d}" % self.id
        }

    trips_count = fields.Integer(compute='_trips_count', string=_('Trips Count'))

class Vehicle(models.Model):
    _inherit = 'fleet.vehicle'

    def name_get(self, context={}):
        res = []
        for record in self:
            name = record.license_plate
            res.append((record.id, name))

        return res

    @api.multi
    def _trips_count(self):
        for each in self:
            trip_ids = self.env['trips.trip'].search([('vehicle', '=', each.id)])
            each.trips_count = len(trip_ids)

    @api.multi
    def trips_view(self):
        self.ensure_one()
        domain = [
            ('vehicle', '=', self.id)]
        return {
            'name': _('Trips'),
            'domain': domain,
            'res_model': 'trips.trip',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form,calendar,pivot',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create New Trip
                        </p>'''),
            'limit': 80,
            'context': "{'default_vehicle': %d}" % self.id
        }

    trips_count = fields.Integer(compute='_trips_count', string=_('Trips Count'))


class Trip(models.Model):
    _name = 'trips.trip'
    _inherit = 'mail.thread'
    _description = "Trip Details"
    
    day_start = fields.Date(_('Date'), required=True)
    driver = fields.Many2one('hr.employee', _('Driver'), required=True)
    employee_number = fields.Char(related='driver.employee_number', store=True)
    vehicle = fields.Many2one('fleet.vehicle', _('Vehicle'), required=False)
    compensation_rate = fields.Float(_('Comp. Rate'), compute='_compensation_rate')
    compensation_correction = fields.Float(_('Comp. Correction'), store=True, default=0.0)
    compensation = fields.Float(_('Compensation'), store=True, sum='Total Compensation', compute='_compensation')

    special_instruction = fields.Char(_('Special Instruction'))
    done = fields.Boolean(_('Done'))

    short_name = fields.Char(_('Trip'), store=True, compute='_custom_name_get')
    #notes = fields.Text(_('Notes'))

    @api.multi
    @api.depends('driver', 'day_start', 'vehicle')
    def _compensation_rate(self):
        for record in self:
            emp = record.driver
            vehicle = record.vehicle
            if not emp or not vehicle:
                record.compensation_rate = 0.0
                continue
            if not emp.employment_start:
                record.compensation_rate = 0.0
                continue
            if not self.day_start:
                record.compensation_rate = 0.0
                continue
            estart = fields.Date.from_string(emp.employment_start)
            eend = fields.Date.from_string(emp.employment_end)
            emax = estart + timedelta(days = 730)
            date_now = fields.Date.from_string(self.day_start)
            if eend:
                if date_now > eend:
                    record.compensation_rate = 0.0
                    continue
            if date_now >= emax:
                record.compensation_rate = 61.00
                continue
            if date_now < estart:
                record.compensation_rate = 0.0
                continue
            emax = estart + timedelta(days = 90)
            if date_now >= emax:
                record.compensation_rate = 59.00
                continue
            record.compensation_rate = 54.00

    @api.multi
    @api.depends('compensation_rate', 'compensation_correction')
    def _compensation(self):
        for record in self:
            record.compensation = record.compensation_rate + record.compensation_correction

    @api.multi
    @api.depends('driver', 'vehicle', 'special_instruction')
    def _custom_name_get(self):
        res = []
        for record in self:
            if record.vehicle:
                n = "[%s]" % record.vehicle.license_plate, record.driver.name
            else:
                n = "[%s]" % _('VACATION')

            n += " %s" % record.driver.name
            
            if record.special_instruction:
                n += " *%s*" % record.special_instruction
            record.short_name = n

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, record.short_name))
        return res

class TripWizard(models.TransientModel):
    _name = 'trips.trip_wizard'
    _description = "Trip Creation wizard"
    
    day_start = fields.Date(_('Start Date'), required=True)
    day_end = fields.Date(_('End Date'), required=True)
    driver = fields.Many2one('hr.employee', _('Driver'), required=True)
    vehicle = fields.Many2one('fleet.vehicle', _('Vehicle'), required=False)
    compensation_correction = fields.Float(_('Comp. Correction'), default=0.0, required=True)

    special_instruction_first = fields.Char(_('Spec. Instruction for First Trip'))
    special_instruction_last = fields.Char(_('Spec. Instruction for Last Trip'))

    @api.multi
    def create_trips(self):
        ids = []
        for record in self:
            start = fields.Date.from_string(record.day_start)
            end = fields.Date.from_string(record.day_end)
            current = start
            driver = record.driver.id
            vehicle = record.vehicle.id
            comp = record.compensation_correction
            while current <= end:
                if current == start:
                    instr = record.special_instruction_first
                elif current == end:
                    instr = record.special_instruction_last
                else:
                    instr = ''
                id_created = record.env['trips.trip'].create({'day_start': current, 'driver': driver, 'vehicle': vehicle, 'compensation_correction': comp, 'special_instruction': instr})
                ids.append(id_created.id)
                current = current + timedelta(days=1)
            record.env.cr.commit()
        return {
            'name': _('Trips'),
            'res_model': 'trips.trip',
            'domain': [('id', 'in', ids)],
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form,calendar,pivot',
            'target': 'main',
            'context': "{'default_driver': %d, 'default_vehicle': %d}" % (driver, vehicle)
        }
