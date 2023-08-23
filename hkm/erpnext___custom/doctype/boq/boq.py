# Copyright (c) 2022, HKM and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import get_link_to_form

class BOQ(Document):
	def on_update(self):
		self.validate_with_material_request()

	def validate(self):
		self.set_item_missing_value()

	def set_item_missing_value(self):
		for d in self.get("items"):
			d.stock_qty = d.qty
			d.stock_uom = d.uom
			d.conversion_factor = 1

	def validate_with_material_request(self):
		if frappe.db.exists("Material Request", {"boq" : self.name, "docstatus": ["=", 1]}):
			material_request = frappe.get_cached_value("Material Request", {"boq" : source_name, "docstatus": ["<", 2]} , "name")
			mr_link = get_link_to_form("Material Request", material_request)
			frappe.throw(_("Material Request {0} has already created against this BOQ.".format(mr_link)))

	def set_status(self, update=False, status=None, update_modified=True):
		if self.is_new():
			self.status = 'Open'
			return
			
		if self.has_submitted_material_request():
			self.status = 'Completed'

		if update:
			self.db_set('status', self.status, update_modified = update_modified)


	def has_submitted_material_request(self):
		return frappe.db.exists("Material Request", {"boq" : self.name, "docstatus": ["=", 1]})

@frappe.whitelist()
def get_boq_items(boq):
	mr_items = []
	boq_items = []
	if frappe.db.exists("Material Request", {"boq" : boq, "docstatus": ["<", 2]}):
		mr_doc = frappe.get_doc("Material Request", {"boq" : boq, "docstatus": ["<", 2]})
		for d in mr_doc.get("items"):
			mr_items.append(d.boq_item)

	if frappe.db.exists("BOQ", boq):
		boq_doc = frappe.get_doc("BOQ", boq)
		for d in boq_doc.get("items"):
			if not d.name in mr_items:
				item = d.as_dict()
				item.update({
					"item_code" : boq_doc.boq_item_code,
					"boq": d.parent,
					"boq_item": d.name
				})
				boq_items.append(item)

	return boq_items

@frappe.whitelist()
def make_material_request(source_name, target_doc=None):
	mr_items = []
	if frappe.db.exists("Material Request", {"boq" : source_name, "docstatus": ["<", 2]}):
		material_request = frappe.get_cached_value("Material Request", {"boq" : source_name, "docstatus": ["<", 2]} , "name")
		mr_link = get_link_to_form("Material Request", material_request)
		frappe.throw(_("Material Request {0} has already created against this BOQ.".format(mr_link)))
		#mr_doc = frappe.get_doc("Material Request", {"boq" : source_name, "docstatus": ["<", 2]})
		#for d in mr_doc.get("items"):
		#	mr_items.append(d.boq_item)

	def update_item(obj, target, source_parent):
		target.item_code = source_parent.boq_item_code
		if not target.description:
			target.description = target.item_name
		target.item_description = target.description

	def set_missing_values(source, target):
		target.for_a_work_order = 1
		target.material_request_type = "Purchase"

	doclist = get_mapped_doc("BOQ", source_name, {
		"BOQ": {
			"doctype": "Material Request",
			"validation": {
				"status": ["=", "Open"],
																																																																																																																																															}
		},
		"BOQ Item": {
			"doctype": "Material Request Item",
			"field_map": {
				"name": "boq_item",
				"parent": "boq",
			},
			"postprocess": update_item,
			"condition": lambda doc: doc.name not in mr_items
		}
	}, target_doc, set_missing_values)

	return doclist
