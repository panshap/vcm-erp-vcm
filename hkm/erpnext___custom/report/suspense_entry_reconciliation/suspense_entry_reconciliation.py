# Copyright (c) 2022, HKM and contributors
# For license information, please see license.txt


import frappe
from frappe import _

import erpnext
from frappe.utils import flt
from erpnext.accounts.utils import get_currency_precision

def execute(filters=None):
	if not filters.get("company"):
		frappe.throw(_("Please select company"))
	
	if filters:
		filters['from_date'] = '2022-04-01'

	filters = frappe._dict(filters)

	data = get_data(filters)
	columns = get_columns(filters)
	summary = get_report_summary(data)

	return columns, data, None, None, summary

def get_data(report_filters):

	if not report_filters.account:
		report_filters.account = get_suspense_accounts(report_filters.company)

	if not report_filters.account:
		frappe.throw(_("Please setup <b>Donation Suspense Account</b> under company {0}".format(report_filters.company)))				

	gl_data = get_gl_data(report_filters)
	clearance_entries = get_suspense_clearance_entries(report_filters)

	return get_processed_data(gl_data, clearance_entries, report_filters)

def get_processed_data(gl_data, clearance_entries, report_filters):
	currency_precision = get_currency_precision() or 2
	data = []
	jv_map = frappe._dict()

	def add_jv_map(d):
		jv_map.setdefault(d.voucher_no, d)
		jv_map[d.voucher_no].update({"clearance_jv": []})
		return jv_map[d.voucher_no]

	for d in [d for d in gl_data if d.credit]:
		add_jv_map(d)

	for d in [d for d in gl_data if d.debit]:
		clearing_entry = clearance_entries.get(d.voucher_no, {})
		suspense_amount = d.debit
		remarks = ""
		if clearing_entry:
			for clearance_jv, clearing_amount in clearing_entry.items():
				if jv_map.get(clearance_jv):
					jv_map.get(clearance_jv)["debit"] += clearing_amount
					jv_map.get(clearance_jv)["clearance_jv"].append(d.voucher_no)
					suspense_amount -= clearing_amount
					remarks += "{0} : {1}, ".format(clearance_jv, clearing_amount)
		else:
			add_jv_map(d)

		if clearing_entry and suspense_amount:
			if remarks:
				remarks = "Cleared against {0}".format(remarks)				
			d.update({"debit": suspense_amount, "jv_amount": d.debit})
			jvd = add_jv_map(d)
			jvd["clearance_jv"].append(remarks)

	for voucher_no, d in jv_map.items():
		d["credit"] = flt(d.credit, currency_precision)
		d["debit"] = flt(d.debit, currency_precision)
		d["difference"] = flt(d.debit-d.credit, currency_precision)
		d["clearance_jv"] = ", ".join(d.clearance_jv)

		if report_filters.get("show_only_breaks"):
			if abs(d.difference) > 0:
				data.append(d)
		else:
			data.append(d)

	data = sorted(data, key=lambda k: k['posting_date'])

	return data	

def get_report_summary(data):
	summary = frappe._dict(
		debit = 0,
		credit = 0,
		difference = 0,
	)
	for d in data:
		summary['debit'] += d.debit
		summary['credit'] += d.credit
		summary['difference'] += d.difference

	return [
		dict(
			label="Total Credit", 
			value= summary.credit, 
			indicator="Green",
			datatype= "Currency",
		),
		{ "type": "separator", "value": "-"},
		dict(
			label="Total Debit", 
			value= summary.debit, 
			indicator="Blue",
			datatype= "Currency",
		),
		{ "type": "separator", "value": "="},
		dict(
			label="Difference", 
			value= abs(summary.difference), 
			indicator="Red",
			datatype= "Currency",
			),				
	]


def get_gl_data(report_filters):
	filters = {
		"is_cancelled": 0,
		"company": report_filters.company,
		"posting_date": ("between", [report_filters.from_date, report_filters.as_on_date]),
		"account": ("=", report_filters.account),
	}	
	return frappe.get_all("GL Entry", filters=filters,
		fields = ["posting_date", "voucher_type", "voucher_no",
			"sum(debit_in_account_currency) as debit", "sum(credit_in_account_currency) as credit"],
		group_by = "posting_date, voucher_type, voucher_no",
		order_by = "posting_date",
	)

def get_suspense_clearance_entries(report_filters):
	data = frappe.db.sql("""
			select jv.name, jva.suspense_jv,
			sum(jva.debit) as debit
			from `tabJournal Entry` jv, `tabJournal Entry Account` jva
			where jv.docstatus  = 1
			and jva.parent = jv.name
			and jv.company = %s
			and jv.posting_date between %s and %s
			and jva.account = %s
			and ifnull(jva.suspense_jv, '') != ''
			and jva.debit > 0
			group by jv.name, jva.suspense_jv
			""",(report_filters.company, report_filters.from_date, report_filters.as_on_date, report_filters.account), as_dict=1)
	sc_entries = frappe._dict()

	for d in  data:
		if d.suspense_jv:
			sc_entries.setdefault(d.name, {}).setdefault(d.suspense_jv, d.debit)

	return sc_entries

def get_suspense_accounts(company):
	return frappe.get_cached_value('Company', company, 'donation_suspense_account')

def get_columns(report_filters):
	columns = [
		{
			"label": _("Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": "120"
		},
		{
			"label": _("Voucher Type"),
			"fieldname": "voucher_type",
			"width": "120"
		},
		{
			"label": _("Voucher No"),
			"fieldname": "voucher_no",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": "200"
		},
		{
			"label": _("Credit"),
			"fieldname": "credit",
			"fieldtype": "Currency",
			"width": "150"
		},		
		{
			"label": _("Debit"),
			"fieldname": "debit",
			"fieldtype": "Currency",
			"width": "200"
		},		
		{
			"label": _("Difference"),
			"fieldname": "difference",
			"fieldtype": "Currency",
			"width": "150"
		},
		{
			"label": _("Reference"),
			"fieldname": "clearance_jv",
			"fieldtype": "Data",
			"width": "300"

		},
	]

	return columns
