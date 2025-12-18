# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

class HelpdeskPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'ticket_count' in counters:
            partner = request.env.user.partner_id
            Ticket = request.env['helpdesk.ticket']
            values['ticket_count'] = Ticket.search_count([
                ('partner_id', 'child_of', [partner.commercial_partner_id.id])
            ]) if Ticket.check_access_rights('read', raise_exception=False) else 0
        return values

    @http.route(['/my/tickets', '/my/tickets/page/<int:page>'], type='http', auth='user', website=True)
    def my_tickets(self, page=1, **kw):
        partner = request.env.user.partner_id
        Ticket = request.env['helpdesk.ticket']

        domain = [('partner_id', 'child_of', [partner.commercial_partner_id.id])]
        tickets_count = Ticket.search_count(domain)

        pager = portal_pager(
            url='/my/tickets',
            total=tickets_count,
            page=page,
            step=10,
        )

        tickets = Ticket.sudo().search(domain, limit=10, offset=pager['offset'], order='create_date desc')

        return request.render('tamkeen_helpdesk_pro.portal_my_tickets', {
            'tickets': tickets,
            'pager': pager,
            'page_name': 'ticket',
        })

    @http.route(['/my/ticket/<int:ticket_id>'], type='http', auth='public', website=True)
    def my_ticket(self, ticket_id, access_token=None, **kw):
        try:
            ticket = request.env['helpdesk.ticket'].sudo().browse(ticket_id)

            if not ticket.exists():
                return request.redirect('/my/tickets')

            partner = request.env.user.partner_id
            if ticket.partner_id.commercial_partner_id.id != partner.commercial_partner_id.id:
                if not access_token or ticket.access_token != access_token:
                    return request.redirect('/my/tickets')

            return request.render('tamkeen_helpdesk_pro.portal_ticket_page', {
                'ticket': ticket,
                'page_name': 'ticket',
            })
        except:
            return request.redirect('/my/tickets')
