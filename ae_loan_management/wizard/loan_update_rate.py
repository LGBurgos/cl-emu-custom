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

from odoo import models,fields,api,_

class UpdateRate(models.TransientModel):

	_name = "update.rate.wizard"
	_description = "Update Rate Wizard"

	name = fields.Char(string="Name")
	update_rate = fields.Float(required=True, default=12.0,digits=(5, 1), help='Currently applied rate')
	loan_id = fields.Many2one('account.loan',string="Loan",default=lambda self: self.env.context.get('active_id', None))


	def confirm_rate(self):
		if self.loan_id:
			self.loan_id.rate = self.update_rate
			self.loan_id.compute_update_rate_lines()
			mail_template = self.loan_id.env.ref('ae_loan_management.email_template_update_rate_loan_details')
			mail_template.send_mail(self.loan_id.id, force_send=True)
