from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = "stock.picking"

    facturado = fields.Selection([('facturado', 'Facturado'), ('no_facturado', 'No Facturado')], default='no_facturado', store=True, compute="compute_state")

    @api.depends(
        'move_ids.invoice_line_ids',
        'move_ids.invoice_line_ids.move_id',
        'move_ids.invoice_line_ids.move_id.state'
    )
    def compute_state(self):
        for rec in self:
            rec.facturado = 'facturado' if rec.invoice_count > 0 else 'no_facturado'



