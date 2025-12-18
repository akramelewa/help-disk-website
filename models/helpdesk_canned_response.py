# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HelpdeskCannedResponse(models.Model):
    _name = 'helpdesk.canned.response'
    _description = 'Canned Response Template'
    _order = 'sequence, name'

    name = fields.Char('Title', required=True)
    shortcut = fields.Char('Shortcut', help='Type this shortcut to quickly insert response')
    sequence = fields.Integer('Sequence', default=10)
    team_id = fields.Many2one('helpdesk.team', 'Team', help='Leave empty for all teams')
    body = fields.Html('Response Body', required=True)
    active = fields.Boolean('Active', default=True)
    
    _sql_constraints = [
        ('unique_shortcut', 'unique(shortcut)', 'Shortcut must be unique!')
    ]