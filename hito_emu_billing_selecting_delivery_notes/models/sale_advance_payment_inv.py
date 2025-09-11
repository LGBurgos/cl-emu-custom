from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    select_pickings = fields.Many2many('stock.picking')

    sale_order_id = fields.Many2one("sale.order", string="Sale Order")

    advance_payment_method = fields.Selection(
        selection_add=[
            ("facturar_pickings_seleccionados", "Facturar remitos seleccionados"),
        ],
        ondelete={"facturar_pickings_seleccionados": "cascade"},
    )

    def default_get(self, fields_list):
        """Cargar la venta activa al abrir el wizard"""
        res = super().default_get(fields_list)
        active_id = self.env.context.get("active_id")
        if active_id and self.env.context.get("active_model") == "sale.order":
            res["sale_order_id"] = active_id
        return res


    def create_invoices(self):
        self._check_amount_is_positive()

        if self.advance_payment_method == "facturar_pickings_seleccionados" and self.select_pickings:

            move_lines = self.select_pickings.mapped("move_ids")

            # pincking_ids = self.select_pickings.facturado = 'facturado'


            invoices = self.sale_order_ids.with_context(
                invoice_from_pickings=True,
                invoice_from_pickings_move_ids=move_lines
            )._create_invoices(self.sale_order_ids)

            # Vincular factura con los pickings seleccionados
            invoices.write({
                'picking_ids': [(6, 0, self.select_pickings.ids)]
            })

        else:
            invoices = self._create_invoices(self.sale_order_ids)

        return self.sale_order_ids.action_view_invoice(invoices=invoices)