# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    statement_note_id = fields.Many2one(
        'bank.statement.note',
        string='Nota de Extracto',
        help='Nota predefinida para este movimiento de extracto bancario'
    )

    @api.onchange('statement_note_id')
    def _onchange_statement_note_id(self):
        """Copiar el contenido de la nota al campo narration."""
        if self.statement_note_id and self.statement_note_id.name:
            self.narration = self.statement_note_id.name

    def write(self, vals):
        """Sincronizar narration cuando se cambia statement_note_id."""
        # Si se cambia statement_note_id, actualizar narration automáticamente
        if 'statement_note_id' in vals and vals['statement_note_id']:
            note = self.env['bank.statement.note'].browse(vals['statement_note_id'])
            if note and note.name:
                # Actualizar narration en el move asociado
                for record in self:
                    if record.move_id:
                        record.move_id.narration = note.name

        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        """Sincronizar narration al crear registros."""
        records = super().create(vals_list)

        for record in records:
            if record.statement_note_id and record.statement_note_id.name and record.move_id:
                record.move_id.narration = record.statement_note_id.name

        return records