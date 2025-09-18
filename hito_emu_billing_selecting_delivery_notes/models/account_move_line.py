from odoo import models, fields ,api

class AaccountMoveLine(models.Model):
    _inherit = "account.move.line"

    qty = fields.Float('') # ESTE CAMPO SE AGREGA PARA ARREGLAR UN ERROR GENERADO AL CREAR LAS LINEAS DE LA FACTURA
    remito = fields.Char(string='Remito')