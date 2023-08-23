# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
# Modified By: Tara Technologies


import frappe
from frappe import _
from frappe.utils import cstr, flt, formatdate, getdate, cint

import erpnext
from erpnext.accounts.report.financial_statements import (
	filter_accounts,
	filter_out_zero_value_rows,
	set_gl_entries_by_account,
)
from erpnext.accounts.report.trial_balance.trial_balance import (
	validate_filters,
	get_columns,
	get_opening_balances,
	calculate_values,
	accumulate_values_into_parents,
	value_fields,
	prepare_opening_closing,
	calculate_total_row

)

def execute(filters=None):
	validate_filters(filters)
	data = get_data(filters)
	columns = get_columns()
	return columns, data

def get_data(filters):

	accounts = frappe.db.sql("""select name, account_number, parent_account, account_name, root_type, report_type, lft, rgt, is_group

		from `tabAccount` where company=%s order by lft""", filters.company, as_dict=True)
	company_currency = filters.presentation_currency or erpnext.get_company_currency(filters.company)

	if not accounts:
		return None

	accounts, accounts_by_name, parent_children_map = filter_accounts(accounts)

	min_lft, max_rgt = frappe.db.sql("""select min(lft), max(rgt) from `tabAccount`
		where company=%s""", (filters.company,))[0]

	gl_entries_by_account = {}

	opening_balances = get_opening_balances(filters)

	#add filter inside list so that the query in financial_statements.py doesn't break
	if filters.project:
		filters.project = [filters.project]

	set_gl_entries_by_account(filters.company, filters.from_date,
		filters.to_date, min_lft, max_rgt, filters, gl_entries_by_account, ignore_closing_entries=not flt(filters.with_period_closing_entry))

	calculate_values(accounts, gl_entries_by_account, opening_balances)
	accumulate_values_into_parents(accounts, accounts_by_name)

	data = prepare_data(accounts, filters, parent_children_map, company_currency)
	data = filter_out_zero_value_rows(data, parent_children_map, show_zero_values=filters.get("show_zero_values"))
	if not cint(filters.get("with_group_account")):
		data = [d for d in data if not cint(d.get("is_group"))]
		for d in data:
			d['indent'] = 0
			d['parent_account'] = None		

	return data

def prepare_data(accounts, filters, parent_children_map, company_currency):
	data = []

	for d in accounts:
		# Prepare opening closing for group account
		if parent_children_map.get(d.account):
			prepare_opening_closing(d)

		has_value = False
		row = {
			"account": d.name,
			"parent_account": d.parent_account,
			"indent": d.indent,
			"from_date": filters.from_date,
			"to_date": filters.to_date,
			"currency": company_currency,
			"account_name": ('{} - {}'.format(d.account_number, d.account_name)
				if d.account_number else d.account_name),
			"is_group": d.is_group,
		}

		for key in value_fields:
			row[key] = flt(d.get(key, 0.0), 3)

			if abs(row[key]) >= 0.005:
				# ignore zero values
				has_value = True

		row["has_value"] = has_value
		data.append(row)
	total_row = calculate_total_row(accounts, company_currency)
	data.extend([{},total_row])

	return data
