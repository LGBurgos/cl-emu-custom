# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    statement_note_id = fields.Many2one(
        'bank.statement.note',
        string='Nota de Extracto',
        help='Nota predefinida para este movimiento de extracto bancario'
    )
