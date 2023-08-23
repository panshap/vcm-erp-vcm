// Copyright (c) 2022, Narahari Dasa and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Ten BD Data"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd":1,
			"width":80,
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname": "date_range_option",
			"label": __("Date Range Option"),
			"fieldtype": "Select",
			"options":["Receipt Date","Posting Date"],
			"default":"Receipt Date",
			"reqd": 1
		},
		{
			"fieldname": "date_range",
			"label": __("Date Range"),
			"fieldtype": "DateRange",
			"default": [frappe.datetime.add_months(frappe.datetime.get_today(),-1), frappe.datetime.get_today()],
			"reqd": 1
		},
		{
			"fieldname": "devotee",
			"label": __("Devotee"),
			"width":80,
			"fieldtype": "Link",
			"options": "Devotee"
		},
		{
			"fieldname": "dr_cummulative",
			"label": __("DR Cummulative"),
			"width":80,
			"fieldtype": "Check"
		},
		{
			"fieldname": "show_only_dcc",
			"label": __("Only DCC"),
			"width":80,
			"fieldtype": "Check"
		},
	]
};
