from odoo import models, fields ,api

class ResPartner(models.Model):
    _inherit = "res.partner"

    num_identificacion = fields.Char(string='Num. Identificación')