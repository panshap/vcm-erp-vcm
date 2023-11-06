# Copyright (c) 2022, Narahari Dasa and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import msgprint, _
from frappe.utils import flt
from hkm.erpnext___custom.report.ten_bd_data.database import get_donor_details


def execute(filters=None):
    # columns, data = [], []
    # return columns, data
    # bounced_data = get_bounced_donors()
    # frappe.errprint(bounced_data)
    # return [], []
    if not filters:
        filters = {}
    filters.update(
        {
            "from_date": filters.get("date_range") and filters.get("date_range")[0],
            "to_date": filters.get("date_range") and filters.get("date_range")[1],
        }
    )
    columns = get_columns(filters)
    conditions = get_condition(filters)

    if filters.get("show_only_dcc") == 1:
        donor_details = get_donor_details(filters)
        dr_nos = list(donor_details.keys())
        string_dr_nos = ",".join([str(dr) for dr in dr_nos])

        donor_je_data = {}
        for i in frappe.db.sql(
            f"""
            SELECT 
            JEA.devotee,JEA.name,JEA.donor_name as donor_name_ERP,JEA.receipt_date,CAST(JEA.dr_no AS INT) as dr_no,JEA.credit,JEA.debit,JEA.cost_center,
            JE.posting_date,JE.name as journal_entry, JE.cheque_date as reference_date, JE.cheque_no as reference_no,
            JE.user_remark as narration
            FROM `tabJournal Entry Account` as JEA
            JOIN `tabJournal Entry` as JE ON JEA.parent = JE.name 
             WHERE JE.docstatus = 1 AND JEA.is_a_donation=1 
             AND dr_no IN ({string_dr_nos})
             {conditions}""",
            filters,
            as_dict=1,
        ):
            # i['dr_no'] = str(i['dr_no'])
            if i["dr_no"] in donor_je_data:
                donor_je_data[i["dr_no"]]["extra_jes"] += "," + i["journal_entry"]
            else:
                donor_je_data.setdefault(i["dr_no"], i)
                donor_je_data[i["dr_no"]]["extra_jes"] = ""
        dr_list = []
        data = []
        for dr in dr_nos:
            if dr in donor_je_data:
                row_map = donor_je_data[dr]
                row = {
                    "dr_no": dr,
                    "donor_name_ERP": row_map["donor_name_ERP"],
                    "donor_name_dhan": donor_details[dr]["name"],
                    "receipt_date": row_map["receipt_date"],
                    "amount_dhan": donor_details[dr]["dr_amount"],
                    "amount_erp": row_map["credit"],
                    "journal_entry": row_map["journal_entry"],
                    "extra_jes": row_map["extra_jes"],
                }
            else:
                row = {
                    "dr_no": dr,
                    "donor_name_ERP": "",
                    "donor_name_dhan": donor_details[dr]["name"],
                    "receipt_date": donor_details[dr]["dr_date"],
                    "amount_dhan": donor_details[dr]["dr_amount"],
                    "amount_erp": 0,
                    "journal_entry": "",
                    "extra_jes": "",
                }
            data.append(row)

        return columns, data, None, None

    elif filters.get("dr_cummulative") == 1:
        JEA_map = {}

        donor_receipt_data = frappe.db.sql(
            """
            SELECT 
            JEA.devotee,JEA.name,JEA.donor_name as donor_name_ERP,JEA.receipt_date,CAST(JEA.dr_no AS INT) as dr_no,JEA.credit,JEA.debit,JEA.cost_center,
            JE.posting_date,JE.name as journal_entry, JE.cheque_date as reference_date, JE.cheque_no as reference_no,
            JE.user_remark as narration
            FROM `tabJournal Entry Account` as JEA
            JOIN `tabJournal Entry` as JE ON JEA.parent = JE.name 
             WHERE JE.docstatus = 1 AND JEA.is_a_donation=1 %s"""
            % (conditions),
            filters,
            as_dict=1,
        )
        data = []
        unique_dr_no = list(set([row["dr_no"] for row in donor_receipt_data]))
        # Get Additional Data from Dhanajaya
        donor_details = get_donor_details(filters)
        for dr_no in unique_dr_no:
            for row in donor_receipt_data:
                if row["dr_no"] == dr_no:
                    amount = -row["debit"] if row["credit"] == 0 else row["credit"]
                    added = False
                    for idx, saved_data in enumerate(data):
                        if saved_data[0] == dr_no:
                            added = True
                            data[idx][4] = data[idx][4] + amount
                            data[idx][6] = data[idx][6] + ", " + row["journal_entry"]
                            break
                    if added == False:
                        details = {
                            "name": "",
                            "dr_amount": "",
                            "pan": "",
                            "seva_code": "",
                            "res_add": "",
                            "off_add": "",
                            "res_phone": "",
                            "off_phone": "",
                            "mobile1": "",
                            "mobile2": "",
                            "phone1": "",
                            "phone2": "",
                            "email1": "",
                            "email2": "",
                        }
                        if dr_no in donor_details:
                            details = donor_details[dr_no]
                        data.append(
                            [
                                dr_no if dr_no is not None else 0,
                                row["donor_name_ERP"],
                                details["name"],
                                row["receipt_date"],
                                amount,
                                details["dr_amount"],
                                row["journal_entry"],
                                row["devotee"],
                                row["cost_center"],
                                row["narration"],
                                details["pan"],
                                details["seva_code"],
                                details["res_add"],
                                details["off_add"],
                                details["res_phone"],
                                details["off_phone"],
                                details["mobile1"],
                                details["mobile2"],
                                details["phone1"],
                                details["phone2"],
                                details["email1"],
                                details["email2"],
                            ]
                        )
        for idx, d in enumerate(data):
            if d[0] in donor_details:
                details = donor_details[d[0]]
                data[idx][2] = details["name"]
                # if details['second_name'] != "":
                #     data[idx][2] +=  details['second_name']
                data[idx][5] = details["dr_amount"]
                data[idx][10] = details["pan"]
                data[idx][11] = details["seva_code"]
        data = sorted(data, key=lambda x: x[0])
        return columns, data, None, None
    else:
        JEA_map = {}

        for i in frappe.db.sql(
            """
            SELECT 
            JEA.devotee,JEA.name,JEA.donor_name,JEA.receipt_date,CAST(JEA.dr_no AS INT) as dr_no,JEA.credit,JEA.debit,JEA.cost_center,
            JE.posting_date,JE.name as journal_entry, JE.cheque_date as reference_date, JE.cheque_no as reference_no
            FROM `tabJournal Entry Account` as JEA
            JOIN `tabJournal Entry` as JE ON JEA.parent = JE.name 
             WHERE JE.docstatus = 1 AND JEA.is_a_donation=1 %s"""
            % (conditions),
            filters,
            as_dict=1,
        ):
            JEA_map.setdefault(i.name, i)
        data = []
        for JEA in sorted(JEA_map):
            je_doc = frappe.get_doc("Journal Entry", JEA_map[JEA]["journal_entry"])
            # children = frappe.get_all("Journal Entry Account",filters={'parent':je},fields = ['account','suspense_jv'])
            suspense = "Not Calculate"
            # for c in je_doc.accounts:
            #     if 'Suspense' in c.account and (not c.suspense_jv):
            #         suspense = 1
            data.append(
                [
                    JEA_map[JEA]["devotee"],
                    JEA_map[JEA]["donor_name"],
                    JEA_map[JEA]["posting_date"],
                    JEA_map[JEA]["receipt_date"],
                    JEA_map[JEA]["dr_no"],
                    JEA_map[JEA]["credit"],
                    JEA_map[JEA]["debit"],
                    JEA_map[JEA]["reference_no"],
                    JEA_map[JEA]["reference_date"],
                    JEA_map[JEA]["journal_entry"],
                    JEA_map[JEA]["cost_center"],
                    suspense,
                ]
            )
        return columns, data, None, chart_data


def get_condition(filters):
    """Get Filter Items"""
    conditions = ""

    if filters.get("date_range_option") == "Receipt Date":
        for opts in (
            ("company", " and `JE`.company=%(company)s"),
            ("devotee", " and `JEA`.devotee = %(devotee)s"),
            ("from_date", " and `JEA`.receipt_date>=%(from_date)s"),
            ("to_date", " and `JEA`.receipt_date<=%(to_date)s"),
        ):
            if filters.get(opts[0]):
                conditions += opts[1]
    elif filters.get("date_range_option") == "Posting Date":
        for opts in (
            ("company", " and `JE`.company=%(company)s"),
            ("devotee", " and `JEA`.devotee = %(devotee)s"),
            ("from_date", " and `JE`.posting_date>=%(from_date)s"),
            ("to_date", " and `JE`.posting_date<=%(to_date)s"),
        ):
            if filters.get(opts[0]):
                conditions += opts[1]
    return conditions


def get_columns(filters):
    """return columns based on filters"""
    if filters.get("show_only_dcc") == 1:
        columns = [
            {"fieldname": "dr_no", "label": "DR No.", "fieldtype": "Int", "width": 100},
            {
                "fieldname": "donor_name_ERP",
                "label": "Donor Name[ERP]",
                "fieldtype": "Data",
                "width": 140,
            },
            {
                "fieldname": "donor_name_dhan",
                "label": "Donor Name[Dhan]",
                "fieldtype": "Data",
                "width": 140,
            },
            {
                "fieldname": "receipt_date",
                "label": "Receipt Date",
                "fieldtype": "Date",
                "width": 110,
            },
            {
                "fieldname": "amount_dhan",
                "label": "Amount[Dhan]",
                "fieldtype": "Currency",
                "width": 120,
            },
            {
                "fieldname": "amount_erp",
                "label": "Amount[ERP]",
                "fieldtype": "Currency",
                "width": 120,
            },
            {
                "fieldname": "journal_entry",
                "label": "Journal Entry",
                "fieldtype": "Data",
                "width": 200,
            },
            {
                "fieldname": "extra_jes",
                "label": "Extra JEs",
                "fieldtype": "Data",
                "width": 200,
            },
        ]
    elif filters.get("dr_cummulative") == 1:
        columns = [
            {"fieldname": "dr_no", "label": "DR No.", "fieldtype": "Int", "width": 100},
            {
                "fieldname": "donor_name_ERP",
                "label": "Donor Name[ERP]",
                "fieldtype": "Data",
                "width": 140,
            },
            {
                "fieldname": "donor_name_dhan",
                "label": "Donor Name[Dhan]",
                "fieldtype": "Data",
                "width": 140,
            },
            {
                "fieldname": "receipt_date",
                "label": "Receipt Date",
                "fieldtype": "Date",
                "width": 110,
            },
            {
                "fieldname": "amount_erp",
                "label": "Amount[ERP]",
                "fieldtype": "Currency",
                "width": 120,
            },
            {
                "fieldname": "amount_dhan",
                "label": "Amount[Dhan]",
                "fieldtype": "Currency",
                "width": 120,
            },
            {
                "fieldname": "journal_entries",
                "label": "Journal Entries",
                "fieldtype": "Data",
                "width": 200,
            },
            {
                "fieldname": "devotee",
                "label": "Devotee",
                "fieldtype": "Data",
                "width": 110,
            },
            {
                "fieldname": "cost_center",
                "label": "Cost Center",
                "fieldtype": "Data",
                "width": 200,
            },
            {
                "fieldname": "narration",
                "label": "Narration",
                "fieldtype": "Data",
                "width": 500,
            },
            {"fieldname": "pan", "label": "PAN No.", "fieldtype": "Data", "width": 100},
            {
                "fieldname": "seva_code",
                "label": "Seva Code",
                "fieldtype": "Data",
                "width": 100,
            },
            {
                "fieldname": "res_add",
                "label": "Residential Address",
                "fieldtype": "Data",
                "width": 140,
            },
            {
                "fieldname": "off_add",
                "label": "Office Address",
                "fieldtype": "Data",
                "width": 140,
            },
            {
                "fieldname": "res_phone",
                "label": "Residential Phone",
                "fieldtype": "Data",
                "width": 100,
            },
            {
                "fieldname": "off_phone",
                "label": "Office Phone",
                "fieldtype": "Data",
                "width": 100,
            },
            {
                "fieldname": "mobile1",
                "label": "Mobile 1",
                "fieldtype": "Data",
                "width": 100,
            },
            {
                "fieldname": "mobile2",
                "label": "Mobile 2",
                "fieldtype": "Data",
                "width": 100,
            },
            {
                "fieldname": "phone1",
                "label": "Phone 1",
                "fieldtype": "Data",
                "width": 100,
            },
            {
                "fieldname": "phone2",
                "label": "Phone 2",
                "fieldtype": "Data",
                "width": 100,
            },
            {
                "fieldname": "email1",
                "label": "Email 1",
                "fieldtype": "Data",
                "width": 100,
            },
            {
                "fieldname": "email2",
                "label": "Email 2",
                "fieldtype": "Data",
                "width": 100,
            },
        ]
    else:
        columns = [
            {
                "fieldname": "devotee",
                "label": "Devotee",
                "fieldtype": "Data",
                "width": 120,
            },
            {
                "fieldname": "donor_name_ERP",
                "label": "Donor Name",
                "fieldtype": "Data",
                "width": 140,
            },
            {
                "fieldname": "posting_date",
                "label": "Posting Date",
                "fieldtype": "Date",
                "width": 110,
            },
            {
                "fieldname": "receipt_date",
                "label": "Receipt Date",
                "fieldtype": "Date",
                "width": 110,
            },
            {"fieldname": "dr_no", "label": "DR No.", "fieldtype": "Int", "width": 100},
            {
                "fieldname": "credit",
                "label": "Credit",
                "fieldtype": "Currency",
                "width": 120,
            },
            {
                "fieldname": "debit",
                "label": "Debit",
                "fieldtype": "Currency",
                "width": 120,
            },
            {
                "fieldname": "reference_no",
                "label": "Reference No.",
                "fieldtype": "Data",
                "width": 140,
            },
            {
                "fieldname": "reference_date",
                "label": "Reference Date",
                "fieldtype": "Date",
                "width": 110,
            },
            {
                "fieldname": "journal_entry",
                "label": "Journal Entry",
                "fieldtype": "Link",
                "options": "Journal Entry",
                "width": 200,
            },
            {
                "fieldname": "cost_center",
                "label": "Cost Center",
                "fieldtype": "Data",
                "width": 200,
            },
            {
                "fieldname": "suspense",
                "label": "Suspense",
                "fieldtype": "Data",
                "width": 100,
            },
        ]
    return columns