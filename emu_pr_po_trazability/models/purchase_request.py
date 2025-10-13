from odoo import models, fields, api

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    @api.onchange('requested_by')
    def copy_requested(self):
        for rec in self:
            if rec.requested_by:
                rec.assigned_to = rec.requested_by