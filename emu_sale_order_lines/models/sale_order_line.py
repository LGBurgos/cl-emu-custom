from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    release = fields.Integer(string='Release')

    @api.onchange('scheduled_date', 'customer_lead')
    def calcular_plazo_entrega(self):
        for rec in self:
            if rec.scheduled_date and rec.order_id.date_order:
                rec.customer_lead = (rec.scheduled_date - rec.order_id.date_order).days


