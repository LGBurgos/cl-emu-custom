from odoo import models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_invoiceable_lines(self, final=False):
        lines = super()._get_invoiceable_lines(final=final)
        if self.env.context.get("invoice_from_pickings"):
            move_lines = self.env.context.get("invoice_from_pickings_move_ids")
            if move_lines:
                lines = lines.filtered(lambda l: l.id in move_lines.mapped("sale_line_id").ids)

        return lines
