# -*- coding: utf-8 -*-

from odoo import models, fields


class ResBank(models.Model):
    _inherit = 'res.bank'

    default_statement_note_id = fields.Many2one(
        'bank.statement.note',
        string='Nota Predeterminada de Extracto',
        help='Nota que se aplicará por defecto a los movimientos de extractos '
             'de este banco. Puede ser modificada en cada movimiento individual.'
    )

    # Campo para documentación
    notes_for_statements = fields.Text(
        string='Notas para Extractos Bancarios',
        help='Información adicional sobre las notas utilizadas en extractos '
             'de este banco'
    )
