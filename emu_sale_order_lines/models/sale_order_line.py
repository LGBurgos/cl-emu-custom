from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    release = fields.Integer(string='Release')

    scheduled_date_manual = fields.Datetime(string="Fecha programada manualmente")

    scheduled_date = fields.Datetime(
        string="Fecha programada",
        compute="_compute_scheduled_date",
        inverse="_inverse_scheduled_date",
        store=True,
        readonly=False,
    )

    @api.depends('scheduled_date_manual')
    def _compute_scheduled_date(self):
        for line in self:
            line.scheduled_date = line.scheduled_date_manual or False
            if line.scheduled_date and line.order_id.date_order:
                line.customer_lead = line.scheduled_date.day - line.order_id.date_order.day

    def _inverse_scheduled_date(self):
        for line in self:
            if line.scheduled_date != (line.order_id.commitment_date or line._expected_date()):
                line.scheduled_date_manual = line.scheduled_date


    @api.depends(
        'product_id', 'customer_lead', 'product_uom_qty', 'product_uom', 'order_id.commitment_date',
        'move_ids', 'move_ids.forecast_expected_date', 'move_ids.forecast_availability', 'warehouse_id'
    )
    def _compute_qty_at_date(self):
        super(SaleOrderLine, self)._compute_qty_at_date()


        for line in self:
            if not line.scheduled_date_manual:
                line.scheduled_date = False
            else:
                line.scheduled_date = line.scheduled_date_manual