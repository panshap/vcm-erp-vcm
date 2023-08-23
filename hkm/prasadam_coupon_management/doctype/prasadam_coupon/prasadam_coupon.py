# Copyright (c) 2022, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
# from hkm.prasadam_coupon_management.doctype.prasadam_coupon.qr_code import get_qrcode
from frappe.utils import random_string, get_url
from hkm.prasadam_coupon_management.utils import current_coupon_credits, get_allowed_time

class PrasadamCoupon(Document):
	def validate(self):
		self.validate_credits()
		# self.validate_booking_date()
		# self.validate_time_allowance()
		# self.validate_transfer()
		return

	def validate_credits(self):
		credits = current_coupon_credits(self.authority,self.date,self.slot,self.coupon_type)
		if credits < self.number:
			frappe.throw(
			    title='No Sufficient Coupon Credits',
			    msg="Credits exhausted with the user:<b>{}</b>".format(self.authority),
			)
		return

	def before_submit(self):
		# data = frappe.utils.get_url_to_form(self.doctype, self.name)
		doc = frappe.get_cached_doc('Prasadam Coupon Settings')
		logo = doc.logo
		# self.qr_code = get_qrcode(self.name, logo)
		self.published = True
		if not self.authority:
			self.authority = frappe.session.user