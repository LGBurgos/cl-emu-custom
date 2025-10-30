# -*- coding: utf-8 -*-

from odoo import models, fields


class BankStatementNote(models.Model):
    _name = 'bank.statement.note'
    _description = 'Nota de Extracto Bancario'
    _order = 'name'

    name = fields.Char(
        string='Descripción de la Nota',
        required=True,
        help='Descripción de la nota para los movimientos bancarios'
    )
    
    code = fields.Char(
        string='Código',
        help='Código único para identificar la nota'
    )
    
    active = fields.Boolean(
        default=True,
        help='Activar o desactivar esta nota'
    )
    
    color = fields.Integer(
        string='Color',
        default=0,
        help='Color para identificar visualmente la nota'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        required=True,
        default=lambda self: self.env.company
    )

    _sql_constraints = [
        ('code_company_unique', 'unique(code, company_id)', 
         'El código de la nota debe ser único por empresa'),
    ]
