// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Cumulative Donation Report"] = {
	"filters": [
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
	]
};
