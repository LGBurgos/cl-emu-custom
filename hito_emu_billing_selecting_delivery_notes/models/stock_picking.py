from odoo import models, fields, api
from odoo.tools import float_compare
import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    facturado = fields.Selection([('facturado', 'Facturado'), ('no_facturado', 'No Facturado')], default='no_facturado',
                                 store=True, compute="compute_state")

    invoice_by_remito_ids = fields.Many2many(
        comodel_name='account.move',
        compute='_compute_invoice_by_remito_ids',
        string='Facturas por Remito',
    )
    invoice_by_remito_count = fields.Integer(
        compute='_compute_invoice_by_remito_ids',
        string='Facturas por Remito',
    )

    @api.depends('vouchers')
    def _compute_invoice_by_remito_ids(self):
        for rec in self:
            if rec.vouchers:
                invoices = self.env['account.move'].search([
                    ('invoice_line_ids.remito', '=', rec.vouchers),
                ])
                rec.invoice_by_remito_ids = invoices
                rec.invoice_by_remito_count = len(invoices)
            else:
                rec.invoice_by_remito_ids = False
                rec.invoice_by_remito_count = 0

    @api.depends(
        'move_ids.invoice_line_ids',
        'move_ids.invoice_line_ids.move_id.state',
        'move_ids.invoice_line_ids.move_id.payment_state',
    )
    def compute_state(self):
        for rec in self:
            # Camino 1: relación directa stock.move → account.move.line
            invoices = rec.move_ids.invoice_line_ids.mapped('move_id')
            invoices = invoices.filtered(
                lambda inv: inv.state == 'posted' and inv.payment_state != 'reversed'
            )

            # Camino 2: si no hay relación directa, buscar por campo vouchers/remito
            if not invoices and rec.vouchers:
                invoices = self.env['account.move'].search([
                    ('move_type', '=', 'out_invoice'),
                    ('state', '=', 'posted'),
                    ('payment_state', '!=', 'reversed'),
                    ('invoice_line_ids.remito', '=', rec.vouchers),
                ])

            rec.facturado = 'facturado' if invoices else 'no_facturado'

    def action_view_invoices_by_remito(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facturas vinculadas por Remito (%s)' % self.vouchers,
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.invoice_by_remito_ids.ids)],
            'context': {'default_move_type': 'out_invoice'},
        }

    @api.model
    def cron_marcar_remitos_facturados(self):
        """
        Realiza tres correcciones sobre el campo facturado:

        1a. CORREGIR ENTRADAS MAL MARCADAS: Pickings de entrada (incoming)
            marcados como 'facturado'. El campo no aplica a entradas.
            → Se revierten a 'no_facturado'.

        1b. CORREGIR FALSOS FACTURADOS (salidas): Remitos de salida marcados
            como 'facturado' pero sin factura válida (posted + no reversed),
            verificado tanto por vouchers/remito como por invoice_ids.
            → Se revierten a 'no_facturado'.

        2.  MARCAR FACTURADOS FALTANTES: Remitos 'no_facturado' que tienen
            una factura posteada y no revertida con línea coincidente en
            producto y cantidad.
            → Se marcan como 'facturado'.
        """

        _logger.info("=" * 70)
        _logger.info("CRON cron_marcar_remitos_facturados: iniciando")
        _logger.info("=" * 70)

        AccountMove = self.env['account.move']

        # --- PASO 1a: Corregir pickings de entrada mal marcados ---
        _logger.info("PASO 1a: Buscando pickings de entrada marcados como 'facturado'...")

        pickings_entrada_facturados = self.search([
            ('picking_type_code', 'in', ('incoming', 'internal')),
            ('facturado', '=', 'facturado'),
        ])

        _logger.info("PASO 1a: %s pickings de entrada en estado 'facturado' encontrados",
                     len(pickings_entrada_facturados))

        revertidos_entrada = []
        for picking in pickings_entrada_facturados:
            picking.facturado = 'no_facturado'
            revertidos_entrada.append(picking)
            _logger.warning(
                "PASO 1a: Revertido a 'no_facturado' (entrada) | PICKING: %s (ID: %s) | VOUCHER: %s",
                picking.name, picking.id, picking.vouchers,
            )

        if revertidos_entrada:
            _logger.warning("PASO 1a: Total entradas revertidas: %s", len(revertidos_entrada))
        else:
            _logger.info("PASO 1a: OK - No se encontraron pickings de entrada mal marcados")

        # --- PASO 1b: Corregir falsos facturados en salidas ---
        # Solo se procesan pickings que tienen vouchers O invoice_ids,
        # ya que sin ninguna referencia a factura no hay nada que verificar.
        _logger.info("PASO 1b: Buscando remitos de salida marcados como 'facturado' sin factura válida...")

        pickings_con_voucher = self.search([
            ('picking_type_code', '=', 'outgoing'),
            ('facturado', '=', 'facturado'),
            ('vouchers', '!=', False),
        ])
        pickings_con_invoice = self.search([
            ('picking_type_code', '=', 'outgoing'),
            ('facturado', '=', 'facturado'),
            ('invoice_ids', '!=', False),
        ])
        pickings_facturados = pickings_con_voucher | pickings_con_invoice

        _logger.info("PASO 1b: %s pickings de salida en estado 'facturado' con vouchers o facturas vinculadas",
                     len(pickings_facturados))

        revertidos = []
        for picking in pickings_facturados:
            # Verificación 1: buscar por vouchers/remito en líneas de factura
            factura_por_remito = False
            if picking.vouchers:
                factura_por_remito = bool(AccountMove.search([
                    ('move_type', '=', 'out_invoice'),
                    ('state', '=', 'posted'),
                    ('payment_state', '!=', 'reversed'),
                    ('invoice_line_ids.remito', '=', picking.vouchers),
                ], limit=1))

            # Verificación 2: buscar por invoice_ids directamente vinculadas
            factura_por_invoice_ids = any(
                inv.move_type == 'out_invoice'
                and inv.state == 'posted'
                and inv.payment_state != 'reversed'
                for inv in picking.invoice_ids
            )

            if not factura_por_remito and not factura_por_invoice_ids:
                picking.facturado = 'no_facturado'
                revertidos.append(picking)
                _logger.warning(
                    "PASO 1b: Revertido a 'no_facturado' | PICKING: %s (ID: %s) | VOUCHER: %s",
                    picking.name, picking.id, picking.vouchers,
                )

        if revertidos:
            _logger.warning("PASO 1b: Total salidas revertidas a 'no_facturado': %s", len(revertidos))
        else:
            _logger.info("PASO 1b: OK - No se encontraron falsos facturados en salidas")

        # --- PASO 2: Marcar facturados faltantes ---
        _logger.info("PASO 2: Buscando remitos 'no_facturado' con factura válida asociada...")

        pickings = self.search([
            ('picking_type_code', '=', 'outgoing'),
            ('vouchers', '!=', False),
            ('facturado', '=', 'no_facturado'),
            ('state', '=', 'done'),
        ])

        _logger.info("PASO 2: %s pickings en estado 'no_facturado' encontrados", len(pickings))

        if not pickings:
            _logger.info("PASO 2: OK - No hay pickings 'no_facturado' para procesar")
            _logger.info("=" * 70)
            _logger.info("CRON cron_marcar_remitos_facturados: finalizado")
            _logger.info("=" * 70)
            return

        marcados = []
        sin_factura = []
        sin_match = []

        for picking in pickings:
            # Buscar facturas posteadas y no revertidas que tengan alguna línea con este remito
            invoices = AccountMove.search([
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', '!=', 'reversed'),
                ('invoice_line_ids.remito', '=', picking.vouchers),
            ])

            if not invoices:
                sin_factura.append(picking)
                continue

            remito_facturado = False

            for move in invoices:
                for line in move.invoice_line_ids.filtered(
                        lambda l: l.remito == picking.vouchers and l.product_id
                ):
                    # Buscar movimiento del remito con mismo producto
                    move_line = picking.move_ids_without_package.filtered(
                        lambda m: m.product_id == line.product_id
                    )

                    if not move_line:
                        continue

                    # Comparar cantidades (con precisión UoM)
                    if float_compare(
                            line.quantity,
                            sum(move_line.mapped('quantity')),
                            precision_rounding=line.product_uom_id.rounding,
                    ) == 0:
                        remito_facturado = True
                        break

                if remito_facturado:
                    break

            if remito_facturado:
                picking.facturado = 'facturado'
                marcados.append(picking)
                _logger.info(
                    "PASO 2: Marcado como 'facturado' | PICKING: %s (ID: %s) | VOUCHER: %s",
                    picking.name, picking.id, picking.vouchers,
                )
            else:
                sin_match.append(picking)
                _logger.warning(
                    "PASO 2: Sin match de producto/cantidad | PICKING: %s (ID: %s) | VOUCHER: %s | Facturas encontradas: %s",
                    picking.name, picking.id, picking.vouchers,
                    ', '.join(invoices.mapped('name')),
                )

        # --- Resumen final ---
        _logger.info("=" * 70)
        _logger.info("CRON cron_marcar_remitos_facturados: resumen")
        _logger.info("  PASO 1a - Entradas revertidas a 'no_facturado': %s", len(revertidos_entrada))
        _logger.info("  PASO 1b - Salidas revertidas a 'no_facturado':  %s", len(revertidos))
        _logger.info("  PASO 2  - Marcados como 'facturado':            %s", len(marcados))
        _logger.info("  PASO 2  - Sin factura asociada:                 %s", len(sin_factura))
        _logger.info("  PASO 2  - Con factura pero sin match:           %s", len(sin_match))
        _logger.info("=" * 70)
        _logger.info("CRON cron_marcar_remitos_facturados: finalizado")
        _logger.info("=" * 70)