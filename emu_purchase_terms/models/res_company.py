from odoo import models, fields

class ResCompany(models.Model):
    _inherit = "res.company"
    purchase_terms = fields.Html("Términos y condiciones de compras")
