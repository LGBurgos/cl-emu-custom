from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = "crm.lead"

    recepcion_rfq = fields.Datetime(string='Recepción RFQ')
    envio_rfq = fields.Datetime(string='Envío RFQ')
    lead_time = fields.Integer(string='Lead Time', compute='compute_lead_time')
    cotizacion = fields.Integer(string='Cotización', readonly=True, copy=False)
    rubro = fields.Many2one('x_rubro', string='Rubro')
    tipo_de_pieza = fields.Many2one('x_tipo_de_pieza', string='Tipo de pieza')

    @api.model
    def create(self, vals):
        if not vals.get('cotizacion'):
            vals['cotizacion'] = self.env['ir.sequence'].next_by_code('crm.lead.cotizacion') or 1
        return super().create(vals)

    @api.depends('envio_rfq', 'recepcion_rfq')
    def compute_lead_time(self):
        for rec in self:
            if rec.envio_rfq and rec.recepcion_rfq:
                delta = rec.envio_rfq - rec.recepcion_rfq
                rec.lead_time = delta.days
            else:
                rec.lead_time = 0

    @api.model
    def copy_data(self):
        leads = self.env['crm.lead'].sudo().search([])
        for rec in leads:
            if rec.x_studio_recepcin_rfq:
                rec.recepcion_rfq = rec.x_studio_recepcin_rfq
            if rec.x_studio_envo_rfq:
                rec.envio_rfq = rec.x_studio_envo_rfq
            if rec.x_studio_lead_time:
                rec.lead_time = rec.x_studio_lead_time
            if rec.x_studio_cotizacin:
                rec.cotizacion = rec.x_studio_cotizacin
            if rec.x_studio_rubro_1:
                rec.rubro = rec.x_studio_rubro_1.id
            if rec.x_studio_tipo_de_pieza:
                rec.tipo_de_pieza = rec.x_studio_tipo_de_pieza.id