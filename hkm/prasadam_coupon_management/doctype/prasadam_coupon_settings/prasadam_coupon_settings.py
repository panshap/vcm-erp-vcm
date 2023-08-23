# Copyright (c) 2022, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PrasadamCouponSettings(Document):
	def validate(self):
		self.validate_duplicate()

	def on_update(self):
		self.delete_timings_key()

	def on_trash(self):
		self.delete_timings_key()

	def delete_timings_key(self):
		for d in self.get("slots"):
			frappe.cache().hdel("prasadam_timings",d.slot)

	def validate_duplicate(self):
		documents = []
		for d in self.get("slots"):
			if d.slot in documents:
				frappe.throw("Row#{0} Duplicate record not allowed for {1}".format(d.idx, d.slot))
				
			documents.append(d.slot)
		return
