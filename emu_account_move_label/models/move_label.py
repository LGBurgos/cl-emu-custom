from odoo import models, fields

class EmuMoveLabel(models.Model):
    _name = "emu.move.label"
    _description = "Etiqueta de Asiento"

    name = fields.Char(required=True, index=True)
    active = fields.Boolean(default=True)
