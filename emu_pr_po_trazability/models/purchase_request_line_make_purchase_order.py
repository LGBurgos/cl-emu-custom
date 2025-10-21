from datetime import datetime

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import get_lang


class PurchaseRequestLineMakePurchaseOrderInherit(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"



    def make_purchase_order(self):
        res = []
        purchase_obj = self.env["purchase.order"]
        po_line_obj = self.env["purchase.order.line"]
        pr_line_obj = self.env["purchase.request.line"]
        user_tz = pytz.timezone(self.env.user.tz or "UTC")
        purchase = False

        for item in self.item_ids:
            line = item.line_id
            if item.product_qty <= 0.0:
                raise UserError(_("Enter a positive quantity."))
            if self.purchase_order_id:
                purchase = self.purchase_order_id
                if len(self.item_ids.request_id.request_type) > 1:
                    raise UserError('Para poder crear una PO a partir de múltiples PR, estos deben ser del mismo tipo de solicitud.')
                purchase.write({'request_type': self.item_ids.request_id.request_type.id})

                list_pr = [ri.display_name for ri in self.item_ids.request_id]

                if purchase.origin:
                    existing = [o.strip() for o in purchase.origin.split(',') if o.strip()]
                    list_pr.extend(existing)

                list_pr = sorted(set(list_pr))

                purchase.origin = ', '.join(list_pr)

            if not purchase:
                po_data = self._prepare_purchase_order(
                    line.request_id.picking_type_id,
                    line.request_id.group_id,
                    line.company_id,
                    line.origin,
                )
                if len(self.item_ids.request_id.request_type) > 1:
                    raise UserError('Para poder crear una PO a partir de múltiples PR, estos deben ser del mismo tipo de solicitud.')
                po_data.update({'request_type': self.item_ids.request_id.request_type.id})
                purchase = purchase_obj.create(po_data)
                if purchase.origin:
                    list_pr = [ri.display_name for ri in self.item_ids.request_id]

                    if purchase.origin:
                        existing = [o.strip() for o in purchase.origin.split(',') if o.strip()]
                        list_pr.extend(existing)

                    list_pr = sorted(set(list_pr))

                    purchase.origin = ', '.join(list_pr)
                else:
                    list_pr = []
                    if self.item_ids:
                        for ri in self.item_ids.request_id:
                                list_pr.append(ri.display_name)
                    list_pr.sort()
                    purchase.origin = ', '.join(list_pr)


            # Look for any other PO line in the selected PO with same
            # product and UoM to sum quantities instead of creating a new
            # po line
            domain = self._get_order_line_search_domain(purchase, item)
            available_po_lines = po_line_obj.search(domain)
            new_pr_line = True
            # If Unit of Measure is not set, update from wizard.
            if not line.product_uom_id:
                line.product_uom_id = item.product_uom_id
            # Allocation UoM has to be the same as PR line UoM
            alloc_uom = line.product_uom_id
            wizard_uom = item.product_uom_id
            if available_po_lines and not item.keep_description:
                new_pr_line = False
                po_line = available_po_lines[0]
                po_line.purchase_request_lines = [(4, line.id)]
                po_line.move_dest_ids |= line.move_dest_ids
                po_line_product_uom_qty = po_line.product_uom._compute_quantity(
                    po_line.product_uom_qty, alloc_uom
                )
                wizard_product_uom_qty = wizard_uom._compute_quantity(
                    item.product_qty, alloc_uom
                )
                all_qty = min(po_line_product_uom_qty, wizard_product_uom_qty)
                self.create_allocation(po_line, line, all_qty, alloc_uom)
            else:
                po_line_data = self._prepare_purchase_order_line(purchase, item)
                if item.keep_description:
                    po_line_data["name"] = item.name
                po_line = po_line_obj.create(po_line_data)
                po_line_product_uom_qty = po_line.product_uom._compute_quantity(
                    po_line.product_uom_qty, alloc_uom
                )
                wizard_product_uom_qty = wizard_uom._compute_quantity(
                    item.product_qty, alloc_uom
                )
                all_qty = min(po_line_product_uom_qty, wizard_product_uom_qty)
                self.create_allocation(po_line, line, all_qty, alloc_uom)
            # TODO: Check propagate_uom compatibility:
            new_qty = pr_line_obj._calc_new_qty(
                line, po_line=po_line, new_pr_line=new_pr_line
            )
            po_line.product_qty = new_qty
            # The quantity update triggers a compute method that alters the
            # unit price (which is what we want, to honor graduate pricing)
            # but also the scheduled date which is what we don't want.
            date_required = item.line_id.date_required
            # we enforce to save the datetime value in the current tz of the user
            po_line.date_planned = (
                user_tz.localize(
                    datetime(date_required.year, date_required.month, date_required.day)
                )
                .astimezone(pytz.utc)
                .replace(tzinfo=None)
            )
            res.append(purchase.id)

        purchase_requests = self.item_ids.mapped("request_id")
        purchase_requests.button_in_progress()
        return {
            "domain": [("id", "in", res)],
            "name": _("RFQ"),
            "view_mode": "list,form",
            "res_model": "purchase.order",
            "view_id": False,
            "context": False,
            "type": "ir.actions.act_window",
        }