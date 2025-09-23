from odoo import models, fields ,api

class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_code = fields.Char(string='Código para la factura')
