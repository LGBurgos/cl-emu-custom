from odoo import models, fields

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    purchase_label_id = fields.Many2one('purchase.label', string='Etiqueta de Compras')

    fecha_inicial_prometida = fields.Date('Fecha inicial prometida')

