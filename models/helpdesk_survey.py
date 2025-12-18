# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class HelpdeskTicketSurvey(models.Model):
    _inherit = 'helpdesk.ticket'
    
    survey_sent = fields.Boolean('Survey Sent', default=False, readonly=True)
    survey_token = fields.Char('Survey Token', copy=False)
    
    def _send_customer_survey(self):
        """Send customer satisfaction survey after ticket is closed"""
        self.ensure_one()
        
        if not self.survey_sent and self.is_closed:
            # Generate unique token
            import secrets
            self.survey_token = secrets.token_urlsafe(16)
            
            # Send survey email
            template = self.env.ref('tamkeen_helpdesk_pro.mail_template_customer_survey', raise_if_not_found=False)
            if template:
                try:
                    template.send_mail(self.id, force_send=False)
                    self.survey_sent = True
                    _logger.info(f'📧 Survey sent for ticket {self.ticket_number}')
                except Exception as e:
                    _logger.warning(f'⚠️ Could not send survey: {e}')
    
    def write(self, vals):
        result = super().write(vals)
        
        # Send survey when ticket is closed
        if 'stage_id' in vals:
            for ticket in self:
                if ticket.is_closed and not ticket.survey_sent:
                    ticket._send_customer_survey()
        
        return result
    
    def action_submit_rating(self, rating, comment=''):
        """Submit customer rating"""
        self.ensure_one()
        self.customer_rating = rating
        
        # Post comment as message
        if comment:
            self.message_post(
                body=_('Customer Feedback: %s') % comment,
                subject=_('Customer Rating: %s stars') % rating,
                message_type='comment'
            )
        
        return True