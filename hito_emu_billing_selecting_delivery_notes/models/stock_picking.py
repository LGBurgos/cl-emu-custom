from odoo import models, fields, api
from odoo.tools import float_compare


class StockPicking(models.Model):
    _inherit = "stock.picking"

    facturado = fields.Selection([('facturado', 'Facturado'), ('no_facturado', 'No Facturado')], default='no_facturado',
                                 store=True, compute="compute_state")

    @api.depends(
        'move_ids.invoice_line_ids',
        'move_ids.invoice_line_ids.move_id.state',
        'vouchers',
    )
    def compute_state(self):
        for rec in self:
            # Camino 1: relación directa stock.move → account.move.line
            invoices = rec.move_ids.invoice_line_ids.mapped('move_id')
            invoices = invoices.filtered(lambda inv: inv.state == 'posted')

            # Camino 2: si no hay relación directa, buscar por campo vouchers/remito
            if not invoices and rec.vouchers:
                invoices = self.env['account.move'].search([
                    ('move_type', '=', 'out_invoice'),
                    ('state', '=', 'posted'),
                    ('invoice_line_ids.remito', '=', rec.vouchers),
                ])

            rec.facturado = 'facturado' if invoices else 'no_facturado'

    @api.model
    def cron_marcar_remitos_facturados(self):
        """
        Realiza dos correcciones sobre el campo facturado:

        1. CORREGIR FALSOS FACTURADOS: Remitos marcados como 'facturado'
           pero sin ninguna factura posteada asociada por vouchers.
           → Se revierten a 'no_facturado'.

        2. MARCAR FACTURADOS FALTANTES: Remitos 'no_facturado' que tienen
           una factura posteada con línea coincidente en producto y cantidad.
           → Se marcan como 'facturado'.
        """

        AccountMove = self.env['account.move']

        # --- PASO 1: Corregir falsos facturados ---
        pickings_facturados = self.search([
            ('picking_type_code', '=', 'outgoing'),
            ('vouchers', '!=', False),
            ('facturado', '=', 'facturado'),
        ])

        for picking in pickings_facturados:
            invoices = AccountMove.search([
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('invoice_line_ids.remito', '=', picking.vouchers),
            ])
            if not invoices:
                picking.facturado = 'no_facturado'

        # --- PASO 2: Marcar facturados faltantes ---
        pickings = self.search([
            ('picking_type_code', '=', 'outgoing'),
            ('vouchers', '!=', False),
            ('facturado', '=', 'no_facturado'),
            ('state', '=', 'done'),
        ])

        if not pickings:
            return

        AccountMove = self.env['account.move']

        for picking in pickings:
            # Buscar facturas posteadas que tengan alguna línea con este remito
            invoices = AccountMove.search([
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('invoice_line_ids.remito', '=', picking.vouchers),
            ])

            if not invoices:
                continue

            remito_facturado = False

            for move in invoices:
                for line in move.invoice_line_ids.filtered(
                        lambda l: l.remito == picking.vouchers and l.product_id
                ):
                    # Buscar movimiento del remito con mismo producto
                    move_line = picking.move_ids_without_package.filtered(
                        lambda m: m.product_id == line.product_id
                    )

                    if not move_line:
                        continue

                    # Comparar cantidades (con precisión UoM)
                    if float_compare(
                            line.quantity,
                            sum(move_line.mapped('quantity')),
                            precision_rounding=line.product_uom_id.rounding,
                    ) == 0:
                        remito_facturado = True
                        break

                if remito_facturado:
                    break

            if remito_facturado:
                picking.facturado = 'facturado'