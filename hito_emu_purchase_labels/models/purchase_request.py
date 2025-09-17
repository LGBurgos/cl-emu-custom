from odoo import models, fields

class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    requisition_purchase_label_id = fields.Many2one('requisition.purchase.label', string='Etiqueta de Requisición')
