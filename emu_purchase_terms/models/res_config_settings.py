from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    purchase_terms = fields.Html(
        related="company_id.purchase_terms", readonly=False
    )
