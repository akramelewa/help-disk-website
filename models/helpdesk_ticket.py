# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging


_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _description = 'Helpdesk Ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'name'
    _order = 'create_date desc'


    name = fields.Char('Subject', required=True, tracking=True)
    ticket_number = fields.Char('Number', readonly=True, copy=False, default='New')
    description = fields.Html('Description')
    partner_id = fields.Many2one('res.partner', 'Customer', required=True, tracking=True)
    partner_email = fields.Char(related='partner_id.email', store=True)
    partner_phone = fields.Char(related='partner_id.phone', store=True)
    team_id = fields.Many2one('helpdesk.team', 'Team', required=True, tracking=True)
    stage_id = fields.Many2one('helpdesk.stage', 'Stage', required=True, group_expand='_expand_stages', tracking=True)
    user_id = fields.Many2one('res.users', 'Assigned To', tracking=True)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], default='1', tracking=True)
    close_date = fields.Datetime('Closed On', readonly=True)
    is_closed = fields.Boolean(compute='_compute_is_closed', store=True)
    
    # Analytics Fields (NEW)
    response_time = fields.Float('Response Time (Hours)', compute='_compute_response_time', store=True, help='Time between ticket creation and assignment')
    resolution_time = fields.Float('Resolution Time (Hours)', compute='_compute_resolution_time', store=True, help='Time between ticket creation and closure')
    customer_rating = fields.Selection([
        ('1', '⭐ Poor'),
        ('2', '⭐⭐ Fair'),
        ('3', '⭐⭐⭐ Good'),
        ('4', '⭐⭐⭐⭐ Very Good'),
        ('5', '⭐⭐⭐⭐⭐ Excellent'),
    ], string='Customer Rating', tracking=True)
    
    access_token = fields.Char('Access Token', copy=False)
    color = fields.Integer('Color')
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready'),
        ('blocked', 'Blocked'),
    ], default='normal', tracking=True)


    def _compute_access_url(self):
        for ticket in self:
            ticket.access_url = f'/my/ticket/{ticket.id}'


    @api.model
    def _expand_stages(self, stages, domain, order):
        return stages.search([], order=order)


    @api.depends('stage_id.is_closed')
    def _compute_is_closed(self):
        for ticket in self:
            ticket.is_closed = ticket.stage_id.is_closed if ticket.stage_id else False


    @api.depends('create_date', 'user_id', 'write_date')
    def _compute_response_time(self):
        """Calculate time between ticket creation and assignment to user"""
        for ticket in self:
            if ticket.user_id and ticket.create_date:
                # Find when the user was assigned (from tracking)
                assignment_date = ticket.write_date or fields.Datetime.now()
                delta = assignment_date - ticket.create_date
                ticket.response_time = round(delta.total_seconds() / 3600, 2)  # Hours with 2 decimals
            else:
                ticket.response_time = 0.0


    @api.depends('create_date', 'close_date')
    def _compute_resolution_time(self):
        """Calculate time between ticket creation and closure"""
        for ticket in self:
            if ticket.close_date and ticket.create_date:
                delta = ticket.close_date - ticket.create_date
                ticket.resolution_time = round(delta.total_seconds() / 3600, 2)  # Hours with 2 decimals
            else:
                ticket.resolution_time = 0.0


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('ticket_number', 'New') == 'New':
                vals['ticket_number'] = self.env['ir.sequence'].next_by_code('helpdesk.ticket') or 'New'
            if not vals.get('access_token'):
                import secrets
                vals['access_token'] = secrets.token_urlsafe(16)
            if not vals.get('stage_id'):
                stage = self.env['helpdesk.stage'].search([], order='sequence', limit=1)
                if stage:
                    vals['stage_id'] = stage.id
            if not vals.get('team_id'):
                team = self.env['helpdesk.team'].search([], limit=1)
                if team:
                    vals['team_id'] = team.id


        tickets = super().create(vals_list)


        for ticket in tickets:
            _logger.info(f'🎫 Ticket created: {ticket.ticket_number}')
            try:
                ticket._send_stage_email('created')
            except Exception as e:
                _logger.warning(f'⚠️  Email not sent (check SMTP): {e}')


        return tickets


    def write(self, vals):
        old_stage = self.stage_id
        old_user = self.user_id
        result = super().write(vals)


        if 'stage_id' in vals and vals['stage_id'] != old_stage.id:
            new_stage = self.env['helpdesk.stage'].browse(vals['stage_id'])


            if new_stage.is_closed and not self.close_date:
                self.close_date = fields.Datetime.now()
                self._send_stage_email('closed')
            elif new_stage.sequence == 5:
                self._send_stage_email('in_progress')
            elif new_stage.sequence == 10:
                self._send_stage_email('solved')


        # Send assignment email only if user changed (not on creation)
        if 'user_id' in vals and vals['user_id'] and vals['user_id'] != old_user.id:
            self._send_stage_email('assigned')


        return result


    def _send_stage_email(self, stage_type):
        """Send email based on stage type"""
        self.ensure_one()


        template_mapping = {
            'created': 'mail_template_ticket_created',
            'assigned': 'mail_template_ticket_assigned',
            'in_progress': 'mail_template_ticket_in_progress',
            'solved': 'mail_template_ticket_solved',
            'closed': 'mail_template_ticket_closed',
        }


        template_xml_id = template_mapping.get(stage_type)
        if template_xml_id:
            try:
                template = self.env.ref(f'tamkeen_helpdesk_pro.{template_xml_id}')
                if template:
                    template.send_mail(self.id, force_send=False)  # Use queue
                    _logger.info(f'📧 Email queued: {stage_type} for {self.ticket_number}')
            except Exception as e:
                _logger.warning(f'⚠️  Could not send email {stage_type}: {e}')