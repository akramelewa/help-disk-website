# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class HelpdeskSurveyController(http.Controller):
    
    @http.route('/helpdesk/survey/<int:ticket_id>', type='http', auth='public', website=True)
    def survey_page(self, ticket_id, token=None, **kw):
        """Display survey page"""
        
        Ticket = request.env['helpdesk.ticket'].sudo()
        ticket = Ticket.browse(ticket_id)
        
        if not ticket.exists():
            return request.render('website.404')
        
        # Verify token
        if ticket.survey_token != token:
            return request.render('website.403')
        
        # Check if already submitted
        if ticket.customer_rating:
            return request.render('tamkeen_helpdesk_pro.survey_already_submitted', {
                'ticket': ticket
            })
        
        return request.render('tamkeen_helpdesk_pro.survey_form', {
            'ticket': ticket,
            'token': token
        })
    
    @http.route('/helpdesk/survey/submit', type='http', auth='public', website=True, csrf=True, methods=['POST'])
    def survey_submit(self, ticket_id, token, rating, comment='', **kw):
        """Submit survey"""
        
        Ticket = request.env['helpdesk.ticket'].sudo()
        ticket = Ticket.browse(int(ticket_id))
        
        if not ticket.exists() or ticket.survey_token != token:
            return request.render('website.403')
        
        # Submit rating
        ticket.action_submit_rating(rating, comment)
        
        return request.render('tamkeen_helpdesk_pro.survey_thanks', {
            'ticket': ticket,
            'rating': rating
        })