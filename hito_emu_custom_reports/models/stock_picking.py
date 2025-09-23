from odoo import models, fields ,api

class AccountMove(models.Model):
    _inherit = "stock.picking"

    payment_terms = fields.Many2one('account.payment.term')
    orden_compra = fields.Char(string="O.compra", related="sale_id.client_order_ref", readonly=1)
    transporte = fields.Many2one('transporte')
    despachado_por = fields.Text(string="Despachado por:")
    control = fields.Text(string="Control")
    kg = fields.Float(string='Kg')


    @api.model
    def create(self, vals):
        if 'partner_id' in vals and 'payment_terms' not in vals:
            partner = self.env['res.partner'].browse(vals['partner_id'])
            if partner.property_payment_term_id:
                vals['payment_terms'] = partner.property_payment_term_id.id

        picking = super().create(vals)

        return picking