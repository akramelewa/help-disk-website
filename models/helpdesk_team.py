# -*- coding: utf-8 -*-
from odoo import models, fields, api

class HelpdeskTeam(models.Model):
    _name = 'helpdesk.team'
    _description = 'Helpdesk Team'

    name = fields.Char('Team Name', required=True)
    active = fields.Boolean(default=True)
    member_ids = fields.Many2many('res.users', string='Members')
    ticket_count = fields.Integer(compute='_compute_ticket_count')
    show_in_portal = fields.Boolean('Show in Portal', default=True)

    @api.depends('member_ids')
    def _compute_ticket_count(self):
        for team in self:
            team.ticket_count = self.env['helpdesk.ticket'].search_count([('team_id', '=', team.id)])
