from __future__ import unicode_literals
import frappe, erpnext
from frappe import _
from frappe.utils import cint, flt, get_link_to_form, getdate, nowdate

from erpnext.accounts.doctype.loyalty_program.loyalty_program import validate_loyalty_points
from erpnext.accounts.doctype.payment_request.payment_request import make_payment_request

from erpnext.accounts.doctype.sales_invoice.sales_invoice import (
	SalesInvoice,
	get_bank_cash_account,
	get_mode_of_payment_info,
	update_multi_mode_option,
)

from erpnext.accounts.party import get_due_date, get_party_account

from erpnext.accounts.doctype.pos_invoice.pos_invoice import POSInvoice,get_stock_availability



from six import iteritems

from erpnext.stock.doctype.batch.batch import get_batch_qty, get_pos_reserved_batch_qty
from erpnext.stock.doctype.serial_no.serial_no import (
	get_delivered_serial_nos,
	get_pos_reserved_serial_nos,
	get_serial_nos,
)

class CustomPOS(POSInvoice):
	def __init__(self, *args, **kwargs):
		super(CustomPOS, self).__init__(*args, **kwargs)

	def validate(self):
		if not cint(self.is_pos):
			frappe.throw(
				_("POS Invoice should have {} field checked.").format(frappe.bold("Include Payment"))
			)

		# run on validate method of selling controller
		super(SalesInvoice, self).validate()
		self.validate_auto_set_posting_time()
		self.validate_mode_of_payment()
		self.validate_uom_is_integer("stock_uom", "stock_qty")
		self.validate_uom_is_integer("uom", "qty")
		self.validate_debit_to_acc()
		self.validate_write_off_account()
		self.validate_change_amount()
		self.validate_change_account()
		self.validate_item_cost_centers()
		self.validate_warehouse()
		self.validate_serialised_or_batched_item()
		self.validate_stock_availablility()
		self.validate_return_items_qty()
		self.set_status()
		self.set_account_for_mode_of_payment()
		self.validate_pos()
		self.validate_full_amount()
		self.validate_loyalty_transaction()
		#  Added by Narahari Dasa
		self.validate_if_zero_rate_item()
		self.validate_full_amount()
		self.cummulative_stock_availbility()
		#FOR RTGP
		# self.validate_discount()
		#  Added by Narahari Dasa
		# if self.coupon_code:
		# 	from erpnext.accounts.doctype.pricing_rule.utils import validate_coupon_code

		# 	validate_coupon_code(self.coupon_code)

	def validate_full_amount(self):
		if self.paid_amount != self.rounded_total:
			frappe.throw("Please check the Paid Amount. It can't be less or more.")

	def validate_if_zero_rate_item(self):
		for item in self.get("items"):
			valuation_rate = frappe.get_value("Item",item.item_code,'valuation_rate')
			if item.rate == 0:
				frappe.throw("Sale Rate of <b>Item: {}</b> can't be ZERO".format(item.item_name))
			if item.rate < valuation_rate:
				frappe.throw("Sale Rate({0}) of <b>Item: {1}</b> can't be less than it's Valuation Rate ({2})".format(item.rate,item.item_name,valuation_rate))
		return
	@frappe.whitelist()
	def get_gst_breakup(self):
		rows = []
		total_tax = 0
		for item in self.items:
			qty = item.qty
			rate = item.rate
			# item_record = frappe.get_doc('Item', item.item_code)
			GSTp = 0
			tax_templates = frappe.db.sql("""
											select item.gst_hsn_code, tax_template.name as template, tax_template.cumulative_tax as rate
											from `tabItem` item
											join `tabItem Tax` item_tax
												on item_tax.parent = item.name
											join `tabItem Tax Template` tax_template
												on tax_template.name = item_tax.item_tax_template
											where tax_template.company = '{}' and item.name = '{}'
											""".format(self.company,item.item_code),as_dict=1)
			if len(tax_templates)>0:
				tax_template =  tax_templates[0]
				GSTp = tax_template['rate']
				row_index = self.search_rows(rows,tax_template['gst_hsn_code'],GSTp)
				if row_index is None:
					temp_data =  {
						'HSN':tax_template['gst_hsn_code'],
						'GSTp':GSTp,
						'Taxable': qty*rate,
						'CGSTI': qty*rate*GSTp/200,
						'SGSTI': qty*rate*GSTp/200
						}
					rows.append(temp_data)
				else:
					rows[row_index]['Taxable'] += qty*rate
					rows[row_index]['CGSTI'] = rows[row_index]['CGSTI'] + qty*rate*GSTp/200
					rows[row_index]['SGSTI'] = rows[row_index]['SGSTI'] + qty*rate*GSTp/200
		for row in rows:
			row['Taxable'] = round(row['Taxable'],2)
			row['CGSTI'] = round(row['CGSTI'],2)
			row['SGSTI'] = round(row['SGSTI'],2)
			total_tax+=  row['CGSTI']  +  row['SGSTI']
		total_tax = round(total_tax,2)
		cashier = frappe.db.get_value('User', self.owner, 'full_name')
		return rows, total_tax, cashier
		
	@frappe.whitelist()
	def get_company_address(self):
		adds = frappe.db.sql("""
						select address.*
						from `tabAddress` address
						join `tabDynamic Link` link on link.parent = address.name
						where link.link_name = '{}' and link.link_doctype = 'Company'
						""".format(self.company),as_dict=1)
		address = adds[0]

		formatted_address = "%(address_line1)s, %(address_line2)s, %(city)s, %(state)s - %(pincode)s"%address

		return formatted_address

	@frappe.whitelist()
	def get_items_segregated(self):
		item_group_data = {}
		
		for item in self.items:
			#item_record = frappe.get_doc('Item', item.item_code)
			grp = item.item_group
			qty = item.qty
			if grp not in item_group_data:
				item_group_data.setdefault(grp,
										{item.item_code:frappe._dict({
												"name":item.item_name,
												"qty":qty
											})}
										)
			else:
				grp_data = item_group_data[grp]
				if item.item_code not in grp_data:
					grp_data.setdefault(item.item_code,{
											"name":item.item_name,
											"qty":qty}
										)
				else:
					grp_data[item.item_code]["qty"] = grp_data[item.item_code]["qty"] + qty
				item_group_data.setdefault(grp,grp_data)

		#For Restaurant : Get the count of this bill
		
		token = frappe.db.sql(f"""
						SELECT count(name) as token
						FROM `tabPOS Invoice`
						WHERE pos_profile = '{self.pos_profile}'
						AND posting_date = '{self.posting_date}'
						AND posting_time < '{self.posting_time}'
						""")[0][0] + 1


		return item_group_data,token

	def search_rows(self,rows,HSN, GSTp):
		for idx, r in enumerate(rows):
			if r['HSN'] == HSN and r['GSTp'] == GSTp:
				return idx
		return None
	def cummulative_stock_availbility(self):
		# items = [item.item_code for item in self.get("items")]
		# unique_items = list(set(items))
		warehouse = self.set_warehouse
		unique_items_qty ={}
		for d in self.get("items"):
			if d.item_code in unique_items_qty:
				unique_items_qty[d.item_code] = unique_items_qty[d.item_code] + d.qty
			else:
				unique_items_qty[d.item_code] = d.qty
		
		for item in unique_items_qty:
			available_stock, is_stock_item = get_stock_availability(item, warehouse)
			if is_stock_item and flt(available_stock) < flt(unique_items_qty[item]):
				frappe.throw(
					_(
						"Stock quantity not enough for Item Code: {} under warehouse {}. Available quantity {}."
					).format(item, warehouse, available_stock,unique_items_qty[item]),
					title=_("Item Unavailable"),
				)
	def validate_discount(self):
		amount_threshold = 3000
		pos_profiles = ["POS - Donwcounter", "POS - RKM Book Counter", "POS - Temple Counter"]
		if (not self.is_return) and self.pos_profile in pos_profiles:
			if self.grand_total < amount_threshold and self.additional_discount_percentage != 0:
				frappe.throw("Discount is not allowed for amount < {}".fomrat(amount_threshold))
			if self.grand_total >= amount_threshold and self.additional_discount_percentage != 5:
				frappe.throw("Discount is not applied on amount >= {} or applied more".format(amount_threshold))
		return