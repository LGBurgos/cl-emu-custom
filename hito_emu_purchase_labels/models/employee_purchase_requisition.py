from odoo import models, fields

class EmployeePurchaseRequisition(models.Model):
    _inherit = "employee.purchase.requisition"

    requisition_purchase_label_id = fields.Many2one('requisition.purchase.label', string='Etiqueta de Requisición')
