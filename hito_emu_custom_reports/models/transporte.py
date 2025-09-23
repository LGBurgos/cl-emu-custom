from odoo import models, fields ,api

class Transporte(models.Model):
    _name = "transporte"

    name = fields.Char(string='Nombre del Transporte')
