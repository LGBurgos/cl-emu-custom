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

            if move.move_type == 'out_refund':
                picking_names = move.invoice_line_ids.mapped('remito')
                pickings = self.env['stock.picking'].browse([])

                if picking_names:
                    pickings |= self.env['stock.picking'].search([
                        ('vouchers', 'in', picking_names)
                    ])

                for picking in pickings:
                    picking.facturado = 'no_facturado'
            else:
                picking_names = move.invoice_line_ids.mapped('remito')
                pickings = self.env['stock.picking'].browse([])

                if picking_names:
                    pickings |= self.env['stock.picking'].search([
                        ('vouchers', 'in', picking_names)
                    ])

                for picking in pickings:
                    picking.facturado = 'facturado'

        return res