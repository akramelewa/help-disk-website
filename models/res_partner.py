# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    ticket_count = fields.Integer(compute='_compute_ticket_count')

    def _compute_ticket_count(self):
        for partner in self:
            partner.ticket_count = self.env['helpdesk.ticket'].search_count([('partner_id', '=', partner.id)])

    def action_view_tickets(self):
        return {
            'name': _('Tickets'),
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.ticket',
            'view_mode': 'kanban,tree,form',
            'domain': [('partner_id', '=', self.id)],
        }
