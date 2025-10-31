# -*- coding: utf-8 -*-

from odoo import models, fields, api


class BankRecWidgetLine(models.Model):
    _inherit = 'bank.rec.widget.line'

    statement_note_id = fields.Many2one(
        comodel_name='bank.statement.note',
        string='Nota de extracto',
        compute='_compute_statement_note_id',
        store=False,
        readonly=False,
    )

    @api.depends('wizard_id.st_line_id.statement_note_id')
    def _compute_statement_note_id(self):
        """Sincronizar desde statement line hacia el widget."""
        for line in self:
            if line.flag == 'liquidity' and line.wizard_id.st_line_id:
                line.statement_note_id = line.wizard_id.st_line_id.statement_note_id
            else:
                line.statement_note_id = False


class BankRecWidget(models.Model):
    _inherit = 'bank.rec.widget'

    def _line_value_changed_statement_note_id(self, line):
        """Sincronizar statement_note_id y narration desde el widget."""
        import logging
        _logger = logging.getLogger(__name__)

        if line.flag == 'liquidity' and self.st_line_id:
            _logger.info(f"Actualizando statement_note_id para st_line {self.st_line_id.id}")

            # Obtener el texto de la nota
            narration_value = None
            if line.statement_note_id and line.statement_note_id.name:
                narration_value = line.statement_note_id.name

            # Guardar statement_note_id en account_bank_statement_line
            self.env.cr.execute("""
                UPDATE account_bank_statement_line 
                SET statement_note_id = %s,
                    write_date = NOW() AT TIME ZONE 'UTC',
                    write_uid = %s
                WHERE id = %s
            """, (
                line.statement_note_id.id if line.statement_note_id else None,
                self.env.uid,
                self.st_line_id.id
            ))

            # Actualizar narration en el move asociado (si existe)
            if self.st_line_id.move_id:
                self.env.cr.execute("""
                    UPDATE account_move 
                    SET narration = %s,
                        write_date = NOW() AT TIME ZONE 'UTC',
                        write_uid = %s
                    WHERE id = %s
                """, (
                    narration_value,
                    self.env.uid,
                    self.st_line_id.move_id.id
                ))

                # Invalidar el cache del move
                self.st_line_id.move_id.invalidate_recordset(['narration', 'write_date', 'write_uid'])

            # Invalidar el cache del statement line
            self.st_line_id.invalidate_recordset(['statement_note_id', 'narration', 'write_date', 'write_uid'])

            # También actualizar el campo narration en la línea del widget
            if narration_value:
                line.narration = narration_value

            _logger.info(f"statement_note_id y narration actualizados exitosamente")

    def button_validate(self):
        """Asegurar que se guarde antes de validar."""
        for line in self.line_ids.filtered(lambda l: l.flag == 'liquidity'):
            if line.statement_note_id != self.st_line_id.statement_note_id:
                self.st_line_id.statement_note_id = line.statement_note_id
                if line.statement_note_id and line.statement_note_id.name:
                    # Actualizar en el move asociado
                    if self.st_line_id.move_id:
                        self.st_line_id.move_id.narration = line.statement_note_id.name

        return super().button_validate()