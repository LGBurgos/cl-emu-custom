# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BankRecWidgetLine(models.Model):
    _inherit = 'bank.rec.widget.line'


    statement_note_id = fields.Many2one(
        comodel_name='bank.statement.note',
        string='Nota de extracto',
        compute='_compute_statement_note_id',
        store=True,
        readonly=False,
    )

    @api.depends('source_aml_id', 'wizard_id.st_line_id.statement_note_id')
    def _compute_statement_note_id(self):
        for line in self:
            if line.flag == 'liquidity':
                line.statement_note_id = line.wizard_id.st_line_id.statement_note_id
            else:
                line.statement_note_id = line.statement_note_id


class BankRecWidget(models.Model):
    _inherit = 'bank.rec.widget'

    def _line_value_changed_statement_note_id(self, line):
        """Called when statement_note_id changes on a line."""
        pass