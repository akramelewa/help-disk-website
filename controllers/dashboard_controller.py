# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
from datetime import datetime, timedelta


class HelpdeskDashboardController(http.Controller):
    
    @http.route('/helpdesk/dashboard/data', type='json', auth='user')
    def get_dashboard_data(self):
        """Get all dashboard statistics"""
        
        # Get ticket counts
        Ticket = request.env['helpdesk.ticket']
        
        total_tickets = Ticket.search_count([])
        open_tickets = Ticket.search_count([('is_closed', '=', False)])
        closed_tickets = Ticket.search_count([('is_closed', '=', True)])
        
        # Get last month data for comparison
        last_month = datetime.now() - timedelta(days=30)
        last_month_total = Ticket.search_count([('create_date', '>=', last_month)])
        
        # Calculate trends
        if last_month_total > 0:
            trend_percentage = round(((total_tickets - last_month_total) / last_month_total) * 100, 1)
        else:
            trend_percentage = 0
        
        # Get average rating
        ratings = Ticket.search([('customer_rating', '!=', False)])
        avg_rating = 0
        if ratings:
            total_rating = sum(int(r.customer_rating) for r in ratings)
            avg_rating = round(total_rating / len(ratings), 1)
        
        # Get last 7 days data for chart
        weekly_data = []
        for i in range(6, -1, -1):
            date = datetime.now() - timedelta(days=i)
            date_start = date.replace(hour=0, minute=0, second=0)
            date_end = date.replace(hour=23, minute=59, second=59)
            
            new_tickets = Ticket.search_count([
                ('create_date', '>=', date_start),
                ('create_date', '<=', date_end)
            ])
            
            closed_today = Ticket.search_count([
                ('close_date', '>=', date_start),
                ('close_date', '<=', date_end)
            ])
            
            weekly_data.append({
                'date': date.strftime('%A'),
                'new': new_tickets,
                'closed': closed_today
            })
        
        # Get status distribution
        stages = request.env['helpdesk.stage'].search([])
        status_data = []
        for stage in stages:
            count = Ticket.search_count([('stage_id', '=', stage.id)])
            if count > 0:
                status_data.append({
                    'name': stage.name,
                    'count': count
                })
        
        # Get recent tickets
        recent_tickets = Ticket.search([], order='create_date desc', limit=5)
        tickets_data = []
        for ticket in recent_tickets:
            tickets_data.append({
                'id': ticket.id,
                'number': ticket.ticket_number,
                'customer': ticket.partner_id.name,
                'subject': ticket.name,
                'date': ticket.create_date.strftime('%d %B %Y'),
                'priority': ticket.priority,
                'stage': ticket.stage_id.name,
                'is_closed': ticket.is_closed
            })
        
        return {
            'kpis': {
                'total': total_tickets,
                'open': open_tickets,
                'closed': closed_tickets,
                'rating': avg_rating,
                'trend': trend_percentage
            },
            'weekly': weekly_data,
            'status': status_data,
            'recent': tickets_data
        }