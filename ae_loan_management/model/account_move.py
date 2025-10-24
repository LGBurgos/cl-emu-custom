# -*- coding: utf-8 -*-
##############################################################################
#
#    AtharvERP Business Solutions
#    Copyright (C) 2020-TODAY AtharvERP Business Solutions(<http://www.atharverp.com>).
#    Author: AtharvERP Business Solutions(<http://www.atharverp.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from odoo import api, fields, models

class AccountMove(models.Model):

    _inherit = 'account.move'

    loan_line_id = fields.Many2one('account.loan.line', readonly=True, ondelete='restrict')
    loan_id = fields.Many2one('account.loan', readonly=True, ondelete='restrict')
    partner = fields.Many2one('res.partner', related='loan_id.partner_id', store=True, string="Partners")
    is_agent = fields.Boolean(string="Is Agent",copy=False)
    is_penlty = fields.Boolean(string="Is Penlty",copy=False,default=False)

    def post(self):
        """
        Create Transaction history when validating loan invoice.
        :return:
        """
        res = super(AccountMove, self).action_post()
        loan_transaction_history = self.env['loan.transaction.history']
        for invoice in self.filtered(lambda x:x.loan_id and x.move_type=="out_invoice"):
            for invoice_line in invoice.invoice_line_ids:
                loan_transaction_history.create({
                    'date': invoice.invoice_date,
                    'loan_id': invoice.loan_id and invoice.loan_id.id or False,
                    'reference': invoice.name and invoice.name or False,
                    'debit': invoice_line.price_subtotal,
                    'move_id': invoice and invoice.id or False
                })
        return res

class AccountInvoiceLine(models.Model):

    _inherit = 'account.move.line'

    loan_invoice_id = fields.Many2one('account.move')

class AccountPayment(models.Model):

    _inherit = "account.payment"

    reconciled_invoice_ids = fields.Many2many('account.move', 'account_payment_move_inv_rel', 'payment_id','move_id',string="Reconciled Invoices",
        compute='_compute_stat_buttons_from_reconciliation',
        help="Invoices whose journal items have been reconciled with these payments.", store=True)
    reconciled_invoices_count = fields.Integer(string="# Reconciled Invoices",
        compute="_compute_stat_buttons_from_reconciliation", store=True)

    # used to determine label 'invoice' or 'credit note' in view
    reconciled_invoices_type = fields.Selection(
        [('credit_note', 'Credit Note'), ('invoice', 'Invoice')],
        compute='_compute_stat_buttons_from_reconciliation', store=True)
    reconciled_bill_ids = fields.Many2many('account.move', 'account_payment_move_bill_rel', 'payment_id','move_id', string="Reconciled Bills",
        compute='_compute_stat_buttons_from_reconciliation',
        help="Invoices whose journal items have been reconciled with these payments.", store=True)
    reconciled_bills_count = fields.Integer(string="# Reconciled Bills",
        compute="_compute_stat_buttons_from_reconciliation", store=True)
    reconciled_statement_line_ids = fields.Many2many(
        comodel_name='account.bank.statement.line',
        string="Reconciled Statement Lines",
        compute='_compute_stat_buttons_from_reconciliation',
        help="Statements lines matched to this payment", store=True
    )
    reconciled_statement_lines_count = fields.Integer(
        string="# Reconciled Statement Lines",
        compute="_compute_stat_buttons_from_reconciliation", store=True
    )


