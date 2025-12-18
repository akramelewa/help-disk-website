# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class HelpdeskController(http.Controller):

    @http.route(['/helpdesk'], type='http', auth='public', website=True, sitemap=True)
    def helpdesk_page(self, **kw):
        teams = request.env['helpdesk.team'].sudo().search([('show_in_portal', '=', True)])
        return request.render('tamkeen_helpdesk_pro.website_helpdesk_page', {
            'teams': teams,
        })

    @http.route(['/helpdesk/submit'], type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def submit_ticket(self, **post):
        try:
            _logger.info(f'📥 Form received: {post.get("subject", "No subject")}')

            required_fields = ['name', 'email', 'subject', 'description']
            missing = [f for f in required_fields if not post.get(f)]

            if missing:
                return request.render('tamkeen_helpdesk_pro.website_helpdesk_error', {
                    'error': f'Missing required fields: {", ".join(missing)}'
                })

            partner = request.env['res.partner'].sudo().search([
                ('email', '=', post.get('email'))
            ], limit=1)

            if not partner:
                partner = request.env['res.partner'].sudo().create({
                    'name': post.get('name'),
                    'email': post.get('email'),
                    'phone': post.get('phone', ''),
                })

            ticket = request.env['helpdesk.ticket'].sudo().create({
                'name': post.get('subject'),
                'description': post.get('description'),
                'partner_id': partner.id,
            })

            _logger.info(f'✅ Ticket created: {ticket.ticket_number}')

            return request.render('tamkeen_helpdesk_pro.website_helpdesk_thanks', {
                'ticket': ticket,
            })

        except Exception as e:
            _logger.error(f'❌ Error: {str(e)}', exc_info=True)
            return request.render('tamkeen_helpdesk_pro.website_helpdesk_error', {
                'error': 'An error occurred. Please try again.'
            })
