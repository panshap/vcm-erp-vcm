// Copyright (c) 2022, HKM and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Suspense Entry Reconciliation"] = {
	"filters": [
		{
			"label": __("Company"),
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"label": __("As On Date"),
			"fieldname": "as_on_date",
			"fieldtype": "Date",
			"reqd": 1,			
			"default": frappe.datetime.get_today(),
		},
		{
			"label": __("Show Only Breaks"),
			"fieldname": "show_only_breaks",
			"fieldtype": "Check",
			"default": 1,
		},		
	]
};
