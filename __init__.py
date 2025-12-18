# -*- coding: utf-8 -*-
from . import models
from . import controllers
from . import wizard

from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)

def post_init_hook(cr, registry):
    """
    Post-installation hook to automatically configure Helpdesk module.
    This runs once after module installation.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    _logger.info('='*70)
    _logger.info('🚀 TAMKEEN HELPDESK PRO - POST INIT HOOK STARTED')
    _logger.info('='*70)

    try:
        # 1. Add Admin to Helpdesk Manager
        _logger.info('Step 1: Adding Admin to Helpdesk Manager...')
        admin_user = env.ref('base.user_admin', raise_if_not_found=False)
        manager_group = env.ref('tamkeen_helpdesk_pro.group_helpdesk_manager', raise_if_not_found=False)

        if admin_user and manager_group:
            if manager_group.id not in admin_user.groups_id.ids:
                admin_user.write({'groups_id': [(4, manager_group.id)]})
                _logger.info('   ✅ Admin added to Helpdesk Manager group')
            else:
                _logger.info('   ℹ️  Admin already in Helpdesk Manager group')
        else:
            _logger.warning('   ⚠️  Could not find admin user or manager group')

        # 2. Add Internal Users to Helpdesk User
        _logger.info('Step 2: Adding Internal Users to Helpdesk User...')
        user_group = env.ref('tamkeen_helpdesk_pro.group_helpdesk_user', raise_if_not_found=False)

        if user_group:
            internal_users = env['res.users'].search([
                ('share', '=', False),
                ('id', '!=', admin_user.id if admin_user else False)
            ])

            added_count = 0
            for user in internal_users:
                if user_group.id not in user.groups_id.ids:
                    user.write({'groups_id': [(4, user_group.id)]})
                    added_count += 1

            _logger.info(f'   ✅ {added_count} internal users added to Helpdesk User group')

        # 3. Verify Dashboard Menu
        _logger.info('Step 3: Verifying Dashboard menu...')
        dashboard_menu = env.ref('tamkeen_helpdesk_pro.menu_helpdesk_dashboard', raise_if_not_found=False)
        if dashboard_menu:
            _logger.info('   ✅ Dashboard menu is ready')
        else:
            _logger.warning('   ⚠️  Dashboard menu not found')

        # 4. Clean old conflicting records
        _logger.info('Step 4: Cleaning old conflicting records...')
        old_data = env['ir.model.data'].search([
            ('module', '=', 'tamkeen_helpdesk_pro'),
            ('name', '=', 'action_helpdesk_dashboard'),
            ('model', '=', 'ir.actions.client')
        ])
        if old_data:
            old_data.unlink()
            _logger.info('   ✅ Cleaned old dashboard action')
        else:
            _logger.info('   ℹ️  No old records to clean')

        # 5. Activate Email Queue Cron Job
        _logger.info('Step 5: Activating Email Queue...')
        email_cron = env.ref('mail.ir_cron_mail_scheduler_action', raise_if_not_found=False)
        if email_cron:
            if not email_cron.active:
                email_cron.write({'active': True})
                _logger.info('   ✅ Email queue cron job activated')
            else:
                _logger.info('   ℹ️  Email queue already active')

        # 6. Check SMTP Configuration
        _logger.info('Step 6: Checking SMTP configuration...')
        smtp_servers = env['ir.mail_server'].search([], limit=1)
        if smtp_servers:
            _logger.info(f'   ✅ SMTP configured: {smtp_servers[0].name}')
        else:
            _logger.warning('   ⚠️  No SMTP server configured - emails will not be sent!')
            _logger.warning('   💡 Configure SMTP: Settings → Technical → Outgoing Mail Servers')

        # Commit all changes
        env.cr.commit()

        _logger.info('='*70)
        _logger.info('✅ TAMKEEN HELPDESK PRO - POST INIT HOOK COMPLETED')
        _logger.info('='*70)
        _logger.info('📝 Summary:')
        _logger.info(f'   • Admin: Added to Manager group')
        _logger.info(f'   • Users: {added_count if user_group else 0} added to User group')
        _logger.info(f'   • Dashboard: Ready')
        _logger.info(f'   • Email Queue: Active')
        _logger.info(f'   • SMTP: {"Configured" if smtp_servers else "Not configured"}')
        _logger.info('='*70)

    except Exception as e:
        _logger.error('='*70)
        _logger.error('❌ TAMKEEN HELPDESK PRO - POST INIT HOOK FAILED')
        _logger.error(f'Error: {str(e)}')
        _logger.error('='*70)
        import traceback
        _logger.error(traceback.format_exc())
        # Don't raise to avoid blocking installation
