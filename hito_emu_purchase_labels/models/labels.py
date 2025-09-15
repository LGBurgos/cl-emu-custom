from odoo import models, fields

class PurchaseLabel(models.Model):
    _name = "purchase.label"

    name = fields.Char(string='Nombre')


class RequisitionPurchaseLabel(models.Model):
    _name = "requisition.purchase.label"

    name = fields.Char(string='Nombre')