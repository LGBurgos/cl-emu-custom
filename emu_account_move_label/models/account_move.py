from odoo import models, fields

class AccountMove(models.Model):
    _inherit = "account.move"

    etiqueta_id = fields.Many2one("emu.move.label", string="Etiqueta")
