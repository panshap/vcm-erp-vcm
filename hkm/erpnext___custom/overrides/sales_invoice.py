import frappe,requests,json
from ast import literal_eval
from datetime import datetime
import xml.etree.ElementTree as ET
from frappe.utils import getdate

# @frappe.whitelist()
# def confirm_payment_received(invoice):
# 	doc = frappe.get_doc('Sales Invoice', invoice)
# 	if "Cashier" in frappe.get_roles(frappe.session.user):
# 		doc.cashier_received_the_money = 1
# 		doc.save()
# 	else:
# 		frappe.throw("You are not allowed to confirm this.")
# 	return 'Done'

def validate_extra(self,method):
	validate_if_zero_rate_item(self,method)
	validate_back_dated_entry(self)


def validate_if_zero_rate_item(self,method):
	for item in self.get("items"):
		if item.item_code:
			valuation_rate = frappe.get_value("Item",item.item_code,'valuation_rate')
			if item.rate == 0:
				frappe.throw("Sale Rate of <b>Item: {}</b> can't be ZERO".format(item.item_name))
			if item.rate < valuation_rate:
				frappe.throw("Sale Rate({0}) of <b>Item: {1}</b> can't be less than it's Valuation Rate ({2})".format(item.rate,item.item_name,valuation_rate))
	return

def validate_back_dated_entry(self):
	if not self.amended_from:
		latest_sales_invoice = frappe.get_all(
			"Sales Invoice",
			fields=['name','posting_date'], 
			filters = [['docstatus','=','1'],['company','=',self.company]],
			order_by='posting_date desc, posting_time desc'
			)[0]
		if getdate(self.posting_date) < latest_sales_invoice['posting_date']:
			frappe.throw(f"Posting Date can't be earlier to the latest Sales Invoice i.e. on {latest_sales_invoice['posting_date']}")
	return