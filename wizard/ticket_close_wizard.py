# -*- coding: utf-8 -*-
from odoo import models, fields

class TicketCloseWizard(models.TransientModel):
    _name = 'helpdesk.ticket.close.wizard'
    _description = 'Close Ticket Wizard'

    ticket_id = fields.Many2one('helpdesk.ticket', required=True)
    resolution_note = fields.Html('Resolution Note', required=True)

    def action_close_ticket(self):
        self.ticket_id.message_post(body=self.resolution_note)
        closed_stage = self.env['helpdesk.stage'].search([('is_closed', '=', True)], limit=1)
        if closed_stage:
            self.ticket_id.stage_id = closed_stage.id
        return {'type': 'ir.actions.act_window_close'}
