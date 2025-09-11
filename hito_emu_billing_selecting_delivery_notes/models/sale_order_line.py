from odoo import models, api

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # def _prepare_invoice_line(self, qty=None, **kwargs):
    #     # qty será la cantidad a facturar
    #     res = super()._prepare_invoice_line(qty=qty, **kwargs)
    #
    #     if self.env.context.get("invoice_from_pickings"):
    #         move_lines = self.env.context.get("invoice_from_pickings_move_ids")
    #         qty_to_invoice = move_lines.filtered(lambda m: m.sale_line_id == self).mapped("quantity_done")
    #         if qty_to_invoice:
    #             res['quantity'] = sum(qty_to_invoice)
    #
    #     return res

    def _prepare_invoice_line(self, qty=None, **kwargs):
        res = super()._prepare_invoice_line(qty=qty, **kwargs)

        if self.env.context.get("invoice_from_pickings"):
            move_lines = self.env.context.get("invoice_from_pickings_move_ids")
            if move_lines:
                # Filtrar movimientos de esta línea de venta
                relevant_move_lines = move_lines.filtered(lambda m: m.sale_line_id == self)

                # Sumar qty_done de todas las move_line_ids
                total_qty = sum(relevant_move_lines.mapped("move_line_ids.qty_done"))

                if total_qty > 0:
                    res['quantity'] = total_qty  # ⚡ CORRECCIÓN: usar product_uom_qty
                else:
                    return None  # no crear línea si qty=0

        return res