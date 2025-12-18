# -*- coding: utf-8 -*-
from odoo import models, fields

class HelpdeskStage(models.Model):
    _name = 'helpdesk.stage'
    _description = 'Helpdesk Stage'
    _order = 'sequence'

    name = fields.Char('Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10)
    fold = fields.Boolean('Folded')
    is_closed = fields.Boolean('Closed Stage')
