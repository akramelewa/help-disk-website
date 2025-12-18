# -*- coding: utf-8 -*-
{
    'name': 'Tamkeen Helpdesk Pro',
    'version': '16.0.6.0.0',
    'category': 'Services/Helpdesk',
    'summary': 'Professional Helpdesk & Support Ticket Management System with SLA, Survey, Auto-Assignment',
    'description': """
        Tamkeen Helpdesk Pro - Advanced Support System
        ==============================================
        * Multi-team support
        * Email automation (5 templates)
        * Portal & Website access
        * Advanced dashboard with analytics
        * SLA Management
        * Customer Satisfaction Survey
        * Canned Responses
        * Auto-Assignment Rules
        * Response & Resolution Time tracking
        * Customer Rating system
    """,
    'author': 'Akram',
    'website': 'https://www..com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'portal',
        'website',
        'web'
    ],
    'data': [
        # Security
        'security/helpdesk_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/helpdesk_data.xml',
        'data/mail_templates.xml',
        'data/email_queue_data.xml',
        #'data/survey_mail_template.xml',
        
        # Views
        'views/helpdesk_ticket_views.xml',
        'views/helpdesk_team_views.xml',
        'views/helpdesk_stage_views.xml',
        'views/helpdesk_dashboard_views.xml',
        'views/helpdesk_sla_views.xml',
        'views/helpdesk_canned_response_views.xml',
        'views/helpdesk_assignment_rule_views.xml',
        'views/helpdesk_menus.xml',
        
        # Portal & Website
        'views/portal_templates.xml',
        'views/website_templates.xml',
        #'views/survey_templates.xml',
        
        # Wizard & Report
        'wizard/ticket_close_wizard_views.xml',
        'report/ticket_reports.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}
