# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    statement_note_id = fields.Many2one(
        'bank.statement.note',
        string='Nota del Extracto',
        help='Selecciona una nota predefinida para este movimiento',
        domain="[('company_id', '=', company_id), ('active', '=', True)]"
    )

    # Campo heredado que se mantiene para notas adicionales
    note = fields.Text(
        string='Notas Adicionales',
        help='Campo de texto libre para notas adicionales o comentarios'
    )
