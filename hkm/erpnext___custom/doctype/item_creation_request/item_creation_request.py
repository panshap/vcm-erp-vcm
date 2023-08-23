# Copyright (c) 2022, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
import re

class ItemCreationRequest(Document):
	def validate(self):
		pass
		# if self.selling_rate is not None and self.valuation_rate is not None and self.selling_rate < self.valuation_rate:
		# 	frappe.throw("Selling Rate can't be less than Valuation Rate.")
		# return
	# def before_save(self):
	# 	if self.is_sales_item:
	# 		self.calculate_selling_rate_without_tax_and_set_default_company()
	# def on_update(self):
	# 	self.calculate_selling_rate_without_tax()

	# def calculate_selling_rate_without_tax_and_set_default_company(self):
	# 	if self.tax_category is not None and self.tax_category != "": 
	# 		# result = re.findall('[0-9]+', str(self.tax_category))
	# 		if self.tax_category:
	# 			tax_category_doc = frappe.get_doc("Item Tax Template",self.tax_category)
	# 			cumulative_tax = tax_category_doc.cumulative_tax
	# 			if cumulative_tax != 0:
	# 				self.selling_rate_without_tax = self.selling_rate/(1+(cumulative_tax/100))
	# 		else:
	# 			self.selling_rate_without_tax = self.selling_rate
	# 		self.default_company = tax_category_doc.company


@frappe.whitelist()
def create_item(source_name, target_doc=None):
	data = {
			"item_name": "item_name",
			"item_group": "item_group",
			"stock_item":"is_stock_item",
			"unit_of_measure":"stock_uom",
			"name":"item_creation_request"
			}
	item_creation_request_doc = frappe.get_doc("Item Creation Request", source_name)
	if item_creation_request_doc.asset_item:
		data.setdefault("asset_item","is_fixed_asset")
		data.setdefault("asset_category","asset_category")
	
	if item_creation_request_doc.is_sales_item:
		data.setdefault("valuation_rate","valuation_rate")

	doclist = get_mapped_doc("Item Creation Request", source_name, {
		"Item Creation Request": {
			"doctype": "Item",
			"field_map": data
		},
	}, target_doc)
	return doclist