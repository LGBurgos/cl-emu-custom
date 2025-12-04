from odoo import fields, models, api

class AccountMove(models.Model):
    _inherit = 'account.move'


    def action_post(self):
        res = super().action_post()

        for move in self:
            if move.move_type not in ['out_invoice', 'out_refund']:
                continue
            if move.state != 'posted':
                continue

            # 1. Buscar pickings por remito explícito en líneas
            picking_names = move.invoice_line_ids.mapped('remito')
            pickings = self.env['stock.picking'].browse([])

            if picking_names:
                pickings |= self.env['stock.picking'].search([
                    ('vouchers', 'in', picking_names)
                ])

            # Actualizar cada picking encontrado
            for picking in pickings:
                picking.facturado = 'facturado'

        return res