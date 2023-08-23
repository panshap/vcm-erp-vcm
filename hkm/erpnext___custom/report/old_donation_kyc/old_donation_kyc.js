// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Old Donation KYC"] = {
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
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			//"reqd": 1,
			"default": "2022-04-01",
			// "read_only": 1
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.get_today(),
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
			"fieldname": "cash_include",
			"label": __("Include Cash Also"),
			"fieldtype": "Check",
			"default":"0"
		},
		{
			"fieldname": "show_irrelavant",
			"label": __("Show Only Irrelavant"),
			"fieldtype": "Check",
			"default":"0"
		},
		{
			"fieldname": "show_bounced",
			"label": __("Show Only Bounced"),
			"fieldtype": "Check",
			"default":"0"
		}
	]
};
