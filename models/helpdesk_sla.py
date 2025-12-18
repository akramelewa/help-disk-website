# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)


class HelpdeskSLA(models.Model):
    _name = 'helpdesk.sla'
    _description = 'Helpdesk SLA Policy'
    _order = 'sequence, id'

    name = fields.Char('SLA Name', required=True)
    sequence = fields.Integer('Sequence', default=10)
    team_id = fields.Many2one('helpdesk.team', 'Team', required=True)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string='Priority', required=True)
    
    # Time limits (in hours)
    response_time = fields.Float('Response Time (Hours)', required=True, default=24.0,
                                  help='Maximum time to first response')
    resolution_time = fields.Float('Resolution Time (Hours)', required=True, default=72.0,
                                    help='Maximum time to resolve ticket')
    
    # Warning thresholds (percentage)
    warning_threshold = fields.Float('Warning Threshold (%)', default=75.0,
                                      help='Show warning when time reaches this percentage')
    
    active = fields.Boolean('Active', default=True)
    
    _sql_constraints = [
        ('unique_team_priority', 'unique(team_id, priority)', 'SLA policy already exists for this team and priority!')
    ]


class HelpdeskTicketSLA(models.Model):
    _inherit = 'helpdesk.ticket'
    
    sla_id = fields.Many2one('helpdesk.sla', 'SLA Policy', compute='_compute_sla', store=True)
    sla_status = fields.Selection([
        ('met', 'Met'),
        ('warning', 'Warning'),
        ('failed', 'Failed'),
        ('paused', 'Paused')
    ], string='SLA Status', compute='_compute_sla_status', store=True)
    
    sla_response_deadline = fields.Datetime('Response Deadline', compute='_compute_sla_deadlines', store=True)
    sla_resolution_deadline = fields.Datetime('Resolution Deadline', compute='_compute_sla_deadlines', store=True)
    
    sla_response_remaining = fields.Float('Response Time Remaining (Hours)', compute='_compute_sla_remaining')
    sla_resolution_remaining = fields.Float('Resolution Time Remaining (Hours)', compute='_compute_sla_remaining')
    
    @api.depends('team_id', 'priority')
    def _compute_sla(self):
        for ticket in self:
            if ticket.team_id and ticket.priority:
                sla = self.env['helpdesk.sla'].search([
                    ('team_id', '=', ticket.team_id.id),
                    ('priority', '=', ticket.priority),
                    ('active', '=', True)
                ], limit=1)
                ticket.sla_id = sla.id if sla else False
            else:
                ticket.sla_id = False
    
    @api.depends('sla_id', 'create_date')
    def _compute_sla_deadlines(self):
        for ticket in self:
            if ticket.sla_id and ticket.create_date:
                ticket.sla_response_deadline = ticket.create_date + timedelta(hours=ticket.sla_id.response_time)
                ticket.sla_resolution_deadline = ticket.create_date + timedelta(hours=ticket.sla_id.resolution_time)
            else:
                ticket.sla_response_deadline = False
                ticket.sla_resolution_deadline = False
    
    @api.depends('sla_response_deadline', 'sla_resolution_deadline', 'is_closed')
    def _compute_sla_remaining(self):
        now = fields.Datetime.now()
        for ticket in self:
            if ticket.sla_response_deadline and not ticket.user_id:
                delta = ticket.sla_response_deadline - now
                ticket.sla_response_remaining = delta.total_seconds() / 3600
            else:
                ticket.sla_response_remaining = 0
            
            if ticket.sla_resolution_deadline and not ticket.is_closed:
                delta = ticket.sla_resolution_deadline - now
                ticket.sla_resolution_remaining = delta.total_seconds() / 3600
            else:
                ticket.sla_resolution_remaining = 0
    
    @api.depends('sla_response_remaining', 'sla_resolution_remaining', 'sla_id')
    def _compute_sla_status(self):
        for ticket in self:
            if not ticket.sla_id:
                ticket.sla_status = 'paused'
                continue
            
            if ticket.is_closed:
                if ticket.resolution_time <= ticket.sla_id.resolution_time:
                    ticket.sla_status = 'met'
                else:
                    ticket.sla_status = 'failed'
            else:
                remaining = ticket.sla_resolution_remaining
                total = ticket.sla_id.resolution_time
                
                if remaining < 0:
                    ticket.sla_status = 'failed'
                elif (remaining / total * 100) < (100 - ticket.sla_id.warning_threshold):
                    ticket.sla_status = 'warning'
                else:
                    ticket.sla_status = 'met'
