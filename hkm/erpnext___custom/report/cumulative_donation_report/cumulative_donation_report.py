# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):

	if not filters: filters = {}
	filters.update({"from_date": filters.get("date_range") and filters.get("date_range")[0], "to_date": filters.get("date_range") and filters.get("date_range")[1]})
	companies = frappe.db.get_list('Company', pluck='name')
	columns = get_columns(companies,filters)
	conditions = get_condition(filters)

	cummulative_data_map ={}
	devotees = set()
	# trips_string = "%%trips%%" JEA.account not LIKE '{trips_string}' and 
	for i in frappe.db.sql(f"""
            SELECT 
            JEA.devotee, JE.company,
			SUM(
				CASE
				WHEN JEA.credit=0
				THEN -JEA.debit
				ELSE JEA.credit
				END) as amount
			
			# SUM(JEA.debit)
            FROM `tabJournal Entry Account` as JEA
            JOIN `tabJournal Entry` as JE ON JEA.parent = JE.name 
            WHERE JE.docstatus = 1 AND JEA.is_a_donation=1 {conditions}
			GROUP BY JEA.devotee, JE.company
			 
			 """,filters,as_dict=1):
		devotee = "NA" if not i.devotee else i.devotee
		cummulative_data_map.setdefault(devotee+"-"+i.company,i.amount)
		devotees.add(devotee)
	
	# devotees = frappe.db.get_list("Devotee",pluck = "name")

	# devotees = set(d['devotee'] for d in donor_receipt_data)
	
	data = []
	for d in devotees:
		row = [d]
		row.extend([0] * len(companies))
		for idx, company in enumerate(companies):
			if d+"-"+company in cummulative_data_map:
				row[idx+1] = cummulative_data_map[d+"-"+company]
		data.append(row)
	# write below to get unique in devotees
	# columns, data = [], []
	return columns, data

def get_columns(companies,filters):
	
	columns = [{
            "fieldname": "collector",
            "label":"Collector",
            "fieldtype": "Data",
            "width": 100
            }]
	columns.extend([
		{
            "fieldname": company,
            "label":company,
            "fieldtype": "Currency",
            "width": 140
        } 
		for company in companies])
	return columns
	
def get_condition(filters):
	conditions=""
	if filters.get("date_range_option") == 'Receipt Date':
		for opts in (
			("from_date", " and `JEA`.receipt_date>=%(from_date)s"),
			("to_date", " and `JEA`.receipt_date<=%(to_date)s")):
				if filters.get(opts[0]):
					conditions += opts[1]
	elif filters.get("date_range_option") == 'Posting Date':
		for opts in (
			("from_date", " and `JE`.posting_date>=%(from_date)s"),
			("to_date", " and `JE`.posting_date<=%(to_date)s")):
				if filters.get(opts[0]):
					conditions += opts[1]

	conditions += " AND `JEA`.cost_center != 'Chardham Trip - RKM'"

	return conditions