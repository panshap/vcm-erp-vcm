# Copyright (c) 2022, HKM and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, scrub

from erpnext.selling.report.sales_analytics.sales_analytics import Analytics

def execute(filters=None):
	return HKMAnalytics(filters).run()

class HKMAnalytics(Analytics):	
	def get_sales_transactions_based_on_items(self):
		if self.filters["value_quantity"] == 'Value':
			value_field = 'base_amount'
		else:
			value_field = 'stock_qty'

		department_filter = ""
		if self.filters.get("department"):
			department_filter = " and s.department = '{0}'".format(self.filters.get("department"))

		self.entries = frappe.db.sql("""
			select i.item_code as entity, i.item_name as entity_name, i.stock_uom, i.{value_field} as value_field, 
			s.{date_field}
			from `tab{doctype} Item` i , `tab{doctype}` s
			where s.name = i.parent and i.docstatus = 1 and s.company = %s
			and s.{date_field} between %s and %s
			{department_filter}
		"""
		.format(date_field=self.date_field, 
			value_field=value_field, 
			doctype=self.filters.doc_type, 
			department_filter=department_filter
		),(self.filters.company, self.filters.from_date, self.filters.to_date), as_dict=1)

		self.entity_names = {}
		for d in self.entries:
			self.entity_names.setdefault(d.entity, d.entity_name)	

	def get_sales_transactions_based_on_item_group(self):
		if self.filters["value_quantity"] == 'Value':
			value_field = "base_amount"
		else:
			value_field = "qty"

		department_filter = ""
		if self.filters.get("department"):
			department_filter = " and s.department = '{0}'".format(self.filters.get("department"))			

		self.entries = frappe.db.sql("""
			select i.item_group as entity, i.{value_field} as value_field, s.{date_field}
			from `tab{doctype} Item` i , `tab{doctype}` s
			where s.name = i.parent and i.docstatus = 1 and s.company = %s
			and s.{date_field} between %s and %s
			{department_filter}
		""".format(date_field=self.date_field, 
			value_field=value_field, 
			doctype=self.filters.doc_type,
			department_filter=department_filter			
		),(self.filters.company, self.filters.from_date, self.filters.to_date), as_dict=1)

		self.get_groups()

	def get_sales_transactions_based_on_customers_or_suppliers(self):
		filters={
			"docstatus": 1,
			"company": self.filters.company,
			self.date_field: ('between', [self.filters.from_date, self.filters.to_date])
		}

		if self.filters["value_quantity"] == 'Value':
			value_field = "base_net_total as value_field"
		else:
			value_field = "total_qty as value_field"

		if self.filters.tree_type == 'Customer':
			entity = "customer as entity"
			entity_name = "customer_name as entity_name"
		else:
			entity = "supplier as entity"
			entity_name = "supplier_name as entity_name"
			if self.filters.get("department"):
				filters.update({"department": self.filters.get("department")})

		self.entries = frappe.get_all(self.filters.doc_type,
			fields=[entity, entity_name, value_field, self.date_field],
			filters=filters
		)

		self.entity_names = {}
		for d in self.entries:
			self.entity_names.setdefault(d.entity, d.entity_name)		