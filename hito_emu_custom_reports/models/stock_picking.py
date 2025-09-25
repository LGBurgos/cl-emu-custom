from odoo import models, fields ,api

class StockPicking(models.Model):
    _inherit = "stock.picking"

    payment_terms = fields.Many2one('account.payment.term')
    orden_compra = fields.Char(string="O.compra", related="sale_id.client_order_ref", readonly=1)
    transporte = fields.Many2one('transporte')
    despachado_por = fields.Text(string="Despachado por:")
    control = fields.Text(string="Control")
    kg = fields.Float(string='Kg')


    @api.model
    def create(self, vals):
        picking = super().create(vals)
        sale_order = self.env['sale.order'].sudo().search([('name','=',picking.origin)])
        if sale_order:
            picking.payment_terms = sale_order.payment_term_id
        return picking