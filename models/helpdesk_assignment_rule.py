# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import random


class HelpdeskAssignmentRule(models.Model):
    _name = 'helpdesk.assignment.rule'
    _description = 'Ticket Auto-Assignment Rule'
    _order = 'sequence, id'

    name = fields.Char('Rule Name', required=True)
    sequence = fields.Integer('Sequence', default=10)
    team_id = fields.Many2one('helpdesk.team', 'Team', required=True)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent')
    ], string='Priority')
    
    assignment_method = fields.Selection([
        ('round_robin', 'Round Robin (توزيع متوازن)'),
        ('random', 'Random (عشوائي)'),
        ('least_busy', 'Least Busy (الأقل انشغالاً)'),
    ], string='Assignment Method', required=True, default='round_robin')
    
    user_ids = fields.Many2many('res.users', string='Assign To Users',
                                 help='Users to assign tickets to. Leave empty to use all team members.')
    
    active = fields.Boolean('Active', default=True)


class HelpdeskTicketAutoAssign(models.Model):
    _inherit = 'helpdesk.ticket'
    
    @api.model_create_multi
    def create(self, vals_list):
        tickets = super().create(vals_list)
        
        for ticket in tickets:
            if not ticket.user_id:
                ticket._auto_assign()
        
        return tickets
    
    def _auto_assign(self):
        """Auto-assign ticket based on rules"""
        self.ensure_one()
        
        # Find matching rule
        rule = self.env['helpdesk.assignment.rule'].search([
            ('team_id', '=', self.team_id.id),
            ('priority', 'in', [False, self.priority]),
            ('active', '=', True)
        ], order='sequence', limit=1)
        
        if not rule:
            return
        
        # Get available users
        users = rule.user_ids if rule.user_ids else self.team_id.member_ids
        
        if not users:
            return
        
        # Apply assignment method
        if rule.assignment_method == 'round_robin':
            assigned_user = self._round_robin_assign(users)
        elif rule.assignment_method == 'random':
            assigned_user = random.choice(users)
        elif rule.assignment_method == 'least_busy':
            assigned_user = self._least_busy_assign(users)
        else:
            assigned_user = users[0]
        
        if assigned_user:
            self.user_id = assigned_user.id
    
    def _round_robin_assign(self, users):
        """Round robin assignment"""
        # Get last assigned user
        last_ticket = self.search([
            ('team_id', '=', self.team_id.id),
            ('user_id', 'in', users.ids),
            ('id', '!=', self.id)
        ], order='id desc', limit=1)
        
        if not last_ticket:
            return users[0]
        
        # Get next user
        user_list = list(users)
        try:
            last_index = user_list.index(last_ticket.user_id)
            next_index = (last_index + 1) % len(user_list)
            return user_list[next_index]
        except ValueError:
            return users[0]
    
    def _least_busy_assign(self, users):
        """Assign to user with least open tickets"""
        user_tickets = {}
        for user in users:
            count = self.search_count([
                ('user_id', '=', user.id),
                ('is_closed', '=', False)
            ])
            user_tickets[user] = count
        
        return min(user_tickets, key=user_tickets.get)