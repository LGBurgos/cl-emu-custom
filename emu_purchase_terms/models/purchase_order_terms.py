from odoo import models, fields

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    tc_unidad_medida = fields.Char("UNIDAD DE MEDIDA")
    tc_cant_x_envase = fields.Char("CANTIDAD X ENVASE")
    tc_formula_reajuste = fields.Char("FORMULA REAJUSTE")
    tc_lugar_descarga = fields.Char("LUGAR DE DESCARGA")
    tc_vigencia_oc = fields.Char("VIGENCIA DE LA O/C")
    tc_reemplazo_oc = fields.Char("REEMPLAZO O/C")
    tc_tipo_moneda = fields.Char("TIPO DE MONEDA")
    tc_material = fields.Char("MATERIAL")
    tc_embalaje = fields.Char("EMBALAJE")
    tc_cantidad_pedida = fields.Char("CANTIDAD PEDIDA")
    tc_cadencia_entrega = fields.Char("CADENCIA DE ENTREGA")
    tc_vigencia_precio = fields.Char("VIGENCIA DEL PRECIO")
    tc_nivel_cambio_plano = fields.Char("NIVEL DE L/CAMBIO PLANO")
    tc_condicion_pago = fields.Char("CONDICIÓN DE PAGO")
    tc_lugar_pago = fields.Char("LUGAR DE PAGO")
    tc_ppm_defec_max = fields.Char("PPM DEFEC MAX ADMISIBLE")
    tc_item_1 = fields.Char("1) campo 1")
    tc_item_2 = fields.Char("2) campo 2")
    tc_item_3 = fields.Char("3) campo 3")
