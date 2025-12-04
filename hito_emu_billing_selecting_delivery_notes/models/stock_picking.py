from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = "stock.picking"

    facturado = fields.Selection([('facturado', 'Facturado'), ('no_facturado', 'No Facturado')], default='no_facturado',
                                 store=True, compute="compute_state")

    @api.depends(
        'move_ids.invoice_line_ids',
        'move_ids.invoice_line_ids.move_id.state',
    )
    def compute_state(self):
        for rec in self:
            invoices = rec.move_ids.invoice_line_ids.mapped('move_id')
            invoices = invoices.filtered(lambda inv: inv.state == 'posted')

            rec.facturado = 'facturado' if invoices else 'no_facturado'


