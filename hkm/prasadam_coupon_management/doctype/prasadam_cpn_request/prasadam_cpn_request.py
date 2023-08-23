# Copyright (c) 2022, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now,getdate
from datetime import datetime,date,timedelta
from frappe.model.document import Document
from hkm.prasadam_coupon_management.utils import current_coupon_credits, get_allowed_time
class PrasadamCPNRequest(Document):
	def before_submit(self):
		if not self.authority:
			self.authority = frappe.session.user
		return
	def validate(self):
		self.validate_user_permission()
		self.validate_credits()
		self.validate_booking_date()
		self.validate_time_allowance()
		self.validate_transfer()
		return

	def validate_user_permission(self):
		settings = frappe.get_doc('Prasadam Coupon Settings')
		if not self.authority:
				self.authority = frappe.session.user
		elif self.authority != frappe.session.user and  settings.admin_role not in frappe.get_roles():
				frappe.throw("You can't use some other Authority name.")
	def validate_credits(self):
		if self.type == 'Release' or self.type == 'Transfer':
			credits = current_coupon_credits(self.authority,self.date,self.slot,self.coupon_type)
			
			if credits < self.number:
				frappe.throw(
				    title='No Sufficient Coupon Credits',
				    msg="Credits not there with the user : <b>{}</b> to release or transfer.<br>AVL_CREDIT:<b>{}</b>".format(self.authority,credits),
				)

	def validate_time_allowance(self):


		timings = get_allowed_time(self.slot)

		#For Booking Date
		date_time_str = '{} {}'.format(self.date,timings[self.slot][self.type])
		date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')

		#For Current Time
		current_date_time = datetime.strptime(now(), '%Y-%m-%d %H:%M:%S.%f')

		if current_date_time>date_time_obj:
			frappe.throw(
			    title='Not Allowed',
			    msg="Allowed time for this <b>{}</b> is till <b>{}</b>".format(self.type,timings[self.slot][self.type])
			)
		return


		# timings = get_allowed_time(self.slot)
		# current_date_time = datetime.strptime(now(), '%Y-%m-%d %H:%M:%S.%f')
		# current_day_midnight = datetime(current_date_time.year, current_date_time.month, current_date_time.day)
		# time_passed_today = current_date_time-current_day_midnight
		
		# if time_passed_today >  timings[self.slot][self.type]:
		# 	frappe.throw(
		# 		    title='Not Allowed',
		# 		    msg="Allowed time for this <b>{}</b> is till <b>{}</b>".format(self.type,timings[self.slot][self.type])
		# 		)
		# return

	def validate_booking_date(self):
		doc = frappe.get_cached_doc('Prasadam Coupon Settings')
		booking_date = datetime.strptime(self.date, "%Y-%m-%d").date()
		after_date = date.today() + timedelta(days=doc.advance_days)
		if not (booking_date >= date.today() and booking_date <= after_date):
			frappe.throw(
				    title='Not Allowed',
				    msg="Coupon can be transacted only for today and of next <b>{}</b> days".format(doc.advance_days)
				)
		return

	def validate_transfer(self):
		if self.type == 'Transfer' and not self.transfer_to:
			 frappe.throw("Please select a user in Transfer")
		if self.transfer_to == frappe.session.user:
			 frappe.throw("Please select a different user other than yourself.")
		return