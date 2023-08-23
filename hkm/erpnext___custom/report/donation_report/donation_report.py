# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from frappe.utils import flt


def execute(filters=None):
    # columns, data = [], []
    # return columns, data
    if not filters:
        filters = {}
    filters.update({"from_date": filters.get("date_range") and filters.get("date_range")[
                   0], "to_date": filters.get("date_range") and filters.get("date_range")[1]})
    columns = get_columns(filters)
    conditions = get_condition(filters)

    if filters.get("dr_cummulative") == 1:
        JEA_map = {}

        donor_receipt_data = frappe.db.sql("""
			SELECT 
			JEA.devotee,JEA.name,JEA.donor_name,JEA.receipt_date,CAST(JEA.dr_no AS INT) as dr_no,JEA.credit,JEA.debit,JEA.cost_center,
			JE.posting_date,JE.name as journal_entry, JE.cheque_date as reference_date, JE.cheque_no as reference_no,
			JE.user_remark as narration
			FROM `tabJournal Entry Account` as JEA
			JOIN `tabJournal Entry` as JE ON JEA.parent = JE.name 
		 	WHERE JE.docstatus = 1 AND JEA.is_a_donation=1 %s""" % (conditions), filters, as_dict=1)

        data = []

        unique_dr_no = list(set([row['dr_no'] for row in donor_receipt_data]))

        for dr_no in unique_dr_no:
            for row in donor_receipt_data:
                if row['dr_no'] == dr_no:
                    amount = - \
                        row['debit'] if row['credit'] == 0 else row['credit']
                    added = False
                    for idx, saved_data in enumerate(data):
                        if saved_data[0] == dr_no:
                            added = True
                            data[idx][3] = data[idx][3] + amount
                            data[idx][4] = data[idx][4] + \
                                ", " + row['journal_entry']
                            break
                    if added == False:
                        data.append([
                            dr_no if dr_no is not None else 0,
                            row['donor_name'],
                            row['receipt_date'],
                            amount,
                            row['journal_entry'],
                            row['devotee'],
                            row['narration'],
                        ])
        # chart_data = get_chart_data(data)
        data = sorted(data, key=lambda x: x[0])
        return columns, data, None, None
    else:

        JEA_map = {}

        for i in frappe.db.sql("""
			SELECT 
			JEA.devotee,JEA.name,JEA.donor_name,JEA.receipt_date,CAST(JEA.dr_no AS INT) as dr_no,JEA.credit,JEA.debit,JEA.cost_center,
			JE.posting_date,JE.name as journal_entry, JE.cheque_date as reference_date, JE.cheque_no as reference_no
			FROM `tabJournal Entry Account` as JEA
			JOIN `tabJournal Entry` as JE ON JEA.parent = JE.name 
		 	WHERE JE.docstatus = 1 AND JEA.is_a_donation=1 %s""" % (conditions), filters, as_dict=1):
            JEA_map.setdefault(i.name, i)

        data = []
        for JEA in sorted(JEA_map):
            data.append([
                JEA_map[JEA]['devotee'],
                JEA_map[JEA]['donor_name'],
                JEA_map[JEA]['posting_date'],
                JEA_map[JEA]['receipt_date'],
                JEA_map[JEA]['dr_no'],
                JEA_map[JEA]['credit'],
                JEA_map[JEA]['debit'],
                JEA_map[JEA]['reference_no'],
                JEA_map[JEA]['reference_date'],
                JEA_map[JEA]['journal_entry'],
                JEA_map[JEA]['cost_center']
            ])
        chart_data = get_chart_data(data)
        return columns, data, None, chart_data


def get_condition(filters):
    """Get Filter Items"""
    conditions = ""

    if filters.get("date_range_option") == 'Receipt Date':
        for opts in (("company", " and `JE`.company=%(company)s"),
                     ("devotee", " and `JEA`.devotee = %(devotee)s"),
                     ("from_date", " and `JEA`.receipt_date>=%(from_date)s"),
                     ("to_date", " and `JEA`.receipt_date<=%(to_date)s")):
            if filters.get(opts[0]):
                conditions += opts[1]
    elif filters.get("date_range_option") == 'Posting Date':
        for opts in (("company", " and `JE`.company=%(company)s"),
                     ("devotee", " and `JEA`.devotee = %(devotee)s"),
                     ("from_date", " and `JE`.posting_date>=%(from_date)s"),
                     ("to_date", " and `JE`.posting_date<=%(to_date)s")):
            if filters.get(opts[0]):
                conditions += opts[1]

    return conditions


def get_columns(filters):
    """return columns based on filters"""
    if filters.get("dr_cummulative") == 1:
        columns = [
            {
                "fieldname": "dr_no",
                "label": "DR No.",
                "fieldtype": "Int",
                "width": 100
            },
            {
                "fieldname": "donor_name",
                "label": "Donor Name",
                "fieldtype": "Data",
                "width": 140
            },
            {
                "fieldname": "receipt_date",
                "label": "Receipt Date",
                "fieldtype": "Date",
                "width": 110
            },
            {
                "fieldname": "amount",
                "label": "Amount",
                "fieldtype": "Currency",
                "width": 120
            },
            {
                "fieldname": "journal_entries",
                "label": "Journal Entries",
                "fieldtype": "Data",
                "width": 200
            },
            {
                "fieldname": "devotee",
                "label": "Devotee",
                "fieldtype": "Data",
                "width": 110
            },
            {
                "fieldname": "narration",
                "label": "Narration",
                "fieldtype": "Data",
                "width": 500
            },
        ]

    else:
        columns = [
            {
                "fieldname": "devotee",
                "label": "Devotee",
                "fieldtype": "Data",
                "width": 120
            },
            {
                "fieldname": "donor_name",
                "label": "Donor Name",
                "fieldtype": "Data",
                "width": 140
            },
            {
                "fieldname": "posting_date",
                "label": "Posting Date",
                "fieldtype": "Date",
                "width": 110
            },
            {
                "fieldname": "receipt_date",
                "label": "Receipt Date",
                "fieldtype": "Date",
                "width": 110
            },
            {
                "fieldname": "dr_no",
                "label": "DR No.",
                "fieldtype": "Int",
                "width": 100
            },
            {
                "fieldname": "credit",
                "label": "Credit",
                "fieldtype": "Currency",
                "width": 120
            },
            {
                "fieldname": "debit",
                "label": "Debit",
                "fieldtype": "Currency",
                "width": 120
            },
            {
                "fieldname": "reference_no",
                "label": "Reference No.",
                "fieldtype": "Data",
                "width": 140
            },
            {
                "fieldname": "reference_date",
                "label": "Reference Date",
                "fieldtype": "Date",
                "width": 110
            },
            {
                "fieldname": "journal_entry",
                "label": "Journal Entry",
                "fieldtype": "Link",
                "options": "Journal Entry",
                "width": 200
            },
            {
                "fieldname": "cost_center",
                "label": "Cost Center",
                "fieldtype": "Data",
                "width": 200
            },

        ]

    return columns


def get_chart_data(data):
    if not (data):
        return []
    devotees = [item[0] for item in data]

    labels = list(set(devotees))

    datapoints = [0] * len(labels)

    for row in data:
        for idx, label in enumerate(labels):
            if row[0] == label:
                datapoints[idx] = datapoints[idx] + (row[5]-row[6])

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Donation Report",
                            "values": datapoints
                }
            ]
        },
        "type": "bar",
        "lineOptions": {
                "regionFill": 1
        }
    }
