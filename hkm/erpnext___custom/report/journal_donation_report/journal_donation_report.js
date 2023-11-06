// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Journal Donation Report"] = {
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
	]
};
