from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    select_pickings = fields.Many2many('stock.picking')

    sale_order_id = fields.Many2one("sale.order", string="Sale Order")

    partner_id = fields.Many2one("res.partner", string="Partner")

    advance_payment_method = fields.Selection(
        selection_add=[
            ("facturar_pickings_seleccionados", "Facturar remitos seleccionados"),
        ],
        ondelete={"facturar_pickings_seleccionados": "cascade"},
    )

    def default_get(self, fields_list):
        """Cargar la venta activa al abrir el wizard"""
        res = super().default_get(fields_list)

        if 'active_id' in self.env.context:
            active_id = self.env.context.get("active_id")

            if active_id and self.env.context.get("active_model") == "sale.order":
                venta = self.env['sale.order'].sudo().search([('id','=',active_id)])
                partner_id = venta.partner_id
                # res["sale_order_id"] = active_id
                res["partner_id"] = partner_id.id

        else:
            active_ids = self.env.context.get("active_ids")

            if active_ids and self.env.context.get("active_model") == "sale.order":
                venta = self.env['sale.order'].sudo().search([('id', 'in', active_ids)])
                partners = venta.mapped("partner_id")

                if len(set(partners.ids)) == 1:
                    partner = partners[0]
                else:
                    raise UserError("Las ventas seleccionadas pertenecen a diferentes clientes.")

                res["partner_id"] = partner.id

        return res



    def create_invoices(self):
        self._check_amount_is_positive()

        if self.advance_payment_method == "facturar_pickings_seleccionados" and self.select_pickings:
            move_lines = self.select_pickings.mapped("move_ids")

            invoices = self.sale_order_ids._create_invoices()

            for inv in invoices:

                inv.invoice_line_ids.unlink()

                invoice_lines = []
                for move in move_lines:
                    qty = sum(move.mapped("move_line_ids.qty_done"))
                    if qty <= 0:
                        continue

                    sale_line = move.sale_line_id

                    vals = {
                        "product_id": move.product_id.id,
                        "quantity": qty,
                        "price_unit": sale_line.price_unit if sale_line else move.product_id.lst_price,
                        "name": sale_line.name if sale_line else move.product_id.display_name,
                        "tax_ids": [(6, 0, sale_line.tax_id.ids)] if sale_line else False,
                        "sale_line_ids": [(6, 0, [sale_line.id])] if sale_line else False,
                        "remito": move.picking_id.vouchers if move.picking_id.vouchers else False,
                    }
                    invoice_lines.append((0, 0, vals))

                inv.write({"invoice_line_ids": invoice_lines})


                inv.write({
                    "picking_ids": [(6, 0, self.select_pickings.ids)]
                })

        else:
            invoices = self._create_invoices(self.sale_order_ids)

        return self.sale_order_ids.action_view_invoice(invoices=invoices)