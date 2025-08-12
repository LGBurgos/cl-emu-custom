from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    rubro = fields.Many2one('x_rubro', string='Rubro')


