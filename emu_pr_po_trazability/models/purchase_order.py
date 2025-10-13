from odoo import models, fields

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    request_type = fields.Many2one(comodel_name="purchase.request.type")
