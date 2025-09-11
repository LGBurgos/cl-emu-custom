from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = "stock.picking"

    facturado = fields.Selection([('facturado', 'Facturado'), ('no_facturado', 'No Facturado')], default='no_facturado', store=True, compute="compute_state")

    @api.depends('invoice_count')
    def compute_state(self):
        for rec in self:
            if rec.invoice_count > 0:
                rec.facturado = 'facturado'
            else:
                rec.facturado = 'no_facturado'
