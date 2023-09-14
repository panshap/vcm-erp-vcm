# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import re
from dhananjaya.dhananjaya.utils import get_best_contact_address
import frappe


DJ_YEAR = "2022"


def execute(filters=None):
    columns, data = get_columns(filters), get_journal_entry_receipts(filters)
    return columns, data


def get_journal_entry_receipts(filters):
    conditions = get_conditions("je", filters)
    je_receipts = frappe.db.sql(
        f"""
					select 
						jea.receipt_date,
                        jea.dr_no,
                        jea.account,
                        jea.credit as amount,
				 		jea.donor_name,
                        jea.name as jea_name,
                        je.posting_date,
                        je.cheque_date,
						je.name as journal_entry,
				 		je.user_remark
					from `tabJournal Entry Account` jea
					join `tabJournal Entry` je
					on je.name = jea.parent
					where jea.is_a_donation = 1
					AND je.docstatus = 1
				 	AND jea.dr_no IS NOT NULL AND jea.dr_no != ""
                    AND jea.credit > 0
					{conditions}
					""",
        as_dict=1,
    )

    only_dr_nos = []
    wrong_je = []
    for j in je_receipts:
        if j["dr_no"]:
            j["dr_no"] = re.sub(r"^2022", "", j["dr_no"])
            j["dr_no"] = re.sub(r"^[0\s]+", "", str(j["dr_no"]))
            only_dr_nos.append(j["dr_no"])
        else:
            wrong_je.append(j)
    only_dr_nos = list(set(only_dr_nos))

    pure_dr, old_dr_relation, receipts_data = get_kyc_erp_receipts(filters)

    final_data = []

    for j in je_receipts:
        donation_row = None

        if j["dr_no"] in old_dr_relation:
            donation_row = receipts_data[old_dr_relation[j["dr_no"]]]
        else:
            near_match = get_match_ending(
                je_receipts, receipts_data, pure_dr, j["dr_no"]
            )
            if near_match:
                donation_row = receipts_data[near_match]

        if donation_row is not None:
            if (not filters.get("cash_include")) and donation_row[
                "payment_method"
            ] == "Cash":
                continue
            row = {
                "dr_no": j["dr_no"],
                "dr_no_dj": donation_row["name"],
                "je": j["journal_entry"],
                "income_account": j["account"],
                "jea_name": j["jea_name"],
                "donor_name": donation_row["full_name"],
                "donor_name_accounts": j["donor_name"],
                "receipt_date": j["receipt_date"],
                "posting_date": j["posting_date"],
                "cheque_date": j["cheque_date"],
                "payment_method": donation_row["payment_method"],
                "seva_type": donation_row["seva_type"],
                "amount_erp": j["amount"],
                "amount_dj": donation_row["amount"],
                "amount_diff": j["amount"] - donation_row["amount"],
                "id_type": donation_row["id_type"],
                "id_number": donation_row["id_number"],
                "contact": donation_row["contact"],
                "address": donation_row["address"],
                "remarks": j["user_remark"],
            }
            final_data.append(row)
        else:
            row = {
                "dr_no": j["dr_no"],
                "dr_no_dj": "NA",
                "je": j["journal_entry"],
                "income_account": j["account"],
                "jea_name": j["jea_name"],
                "donor_name": "NA",
                "donor_name_accounts": j["donor_name"],
                "receipt_date": j["receipt_date"],
                "posting_date": j["posting_date"],
                "cheque_date": j["cheque_date"],
                "payment_method": "NA",
                "seva_type": "NA",
                "amount_erp": j["amount"],
                "amount_dj": 0,
                "amount_diff": j["amount"],
                "id_type": "NA",
                "id_number": "NA",
                "contact": "NA",
                "address": "NA",
                "remarks": j["user_remark"],
            }
            final_data.append(row)

    return final_data


def get_match_ending(je_receipts, erp_receipts, pure_drs, str):
    if len(str) >= 5:
        for p in pure_drs:
            if p.endswith(str):
                p_found = False
                e_amount = erp_receipts[p]["amount"]
                for je in je_receipts:
                    if je["dr_no"] == str and je["amount"] == e_amount:
                        p_found = True
                        break
                if p_found:
                    return p
                else:
                    return None
    return None


def get_kyc_erp_receipts(filters):
    conditions = get_conditions("dr", filters)
    dhananjaya_receipts = frappe.db.sql(
        f"""
					select name,old_dr_no
					from `tabDonation Receipt` dr
					where docstatus = 1
					{conditions}
					""",
        as_dict=1,
    )
    pure_erp_receipt_names = []
    old_dr_erp_receipt_relations = {}
    for d in dhananjaya_receipts:
        pure_erp_receipt_names.append(d["name"])
        if d["old_dr_no"]:
            # clean_dr = str(d['old_dr_no']).lstrip(DJ_YEAR).lstrip('0')
            # if re.match(r'^202[1-3]', str(d['old_dr_no'])):
            clean_dr = str(d["old_dr_no"])[4:].lstrip("0")
            old_dr_erp_receipt_relations.setdefault(clean_dr, d["name"])
    unique_erp_receipt_names = list(
        set(pure_erp_receipt_names + list(old_dr_erp_receipt_relations.values()))
    )
    erp_receipts_data = get_erp_receipts_data(unique_erp_receipt_names)

    return pure_erp_receipt_names, old_dr_erp_receipt_relations, erp_receipts_data


def get_erp_receipts_data(dj_names):
    dj_names_str = ",".join([f"'{d}'" for d in dj_names])
    receipt_kycs = {}
    for r in frappe.db.sql(
        f"""
					select 
						receipt.name,
						receipt.full_name,
						receipt.donor,
						receipt.payment_method,
						receipt.amount,
                        receipt.seva_type,
						IF(donor.pan_no IS NULL or donor.pan_no = "",IF(donor.aadhar_no IS NULL or donor.aadhar_no = "","NA","Aadhar Number"),"PAN Number") as id_type,
						IF(donor.pan_no IS NULL or donor.pan_no = "",donor.aadhar_no,donor.pan_no) as id_number
					from `tabDonation Receipt` receipt
					join `tabDonor` donor on receipt.donor = donor.name
					where receipt.name IN ({dj_names_str})
					""",
        as_dict=1,
    ):
        receipt_kycs.setdefault(r["name"], r)
    unique_donors = list({receipt_kycs[r]["donor"] for r in receipt_kycs})
    donor_addresses_contacts = {}
    for d in unique_donors:
        address, contact, _ = get_best_contact_address(d)
        donor_addresses_contacts.setdefault(d, {"address": address, "contact": contact})

    for r in receipt_kycs:
        receipt_kycs[r]["address"] = donor_addresses_contacts[receipt_kycs[r]["donor"]][
            "address"
        ]
        receipt_kycs[r]["contact"] = donor_addresses_contacts[receipt_kycs[r]["donor"]][
            "contact"
        ]

    return receipt_kycs
    ## receipt_id, donor_id, full_name, address, contact, id_type, id_number


def get_conditions(type, filters):
    conditions = ""
    if type == "je":
        if filters.get("date_range_option") == "Posting Date":
            conditions += f"""
                            AND je.company  =  '{filters.get('company')}'
                            AND je.posting_date BETWEEN '{filters.get('from_date')}' AND '{filters.get('to_date')}'
                            """
        else:
            conditions += f"""
                            AND je.company  =  '{filters.get('company')}'
                            AND jea.receipt_date BETWEEN '{filters.get('from_date')}' AND '{filters.get('to_date')}'
                            """
        if filters.get("show_irrelavant"):
            conditions += " AND jea.irrelavant = 1"
        else:
            conditions += " AND jea.irrelavant = 0"
        if filters.get("show_bounced"):
            conditions += " AND jea.bounced = 1"
        else:
            conditions += " AND jea.bounced = 0"
    elif type == "dr":
        conditions += f"""
						AND dr.company  =  '{filters.get('company')}'
						AND dr.receipt_date BETWEEN '2021-01-01' AND '{filters.get('to_date')}'
						"""
        # AND dr.receipt_date BETWEEN '{filters.get('from_date')}' AND '{filters.get('to_date')}'
    return conditions


def get_columns(filters):
    columns = []
    if filters.status != "Unlinked":
        columns.extend(
            [
                {
                    "label": "DR No. [JE]",
                    "fieldname": "dr_no",
                    "fieldtype": "Data",
                    "width": 160,
                },
                {
                    "label": "DR No. [DJ]",
                    "fieldname": "dr_no_dj",
                    "fieldtype": "Link",
                    "fieldtype": "Donation Receipt",
                    "width": 160,
                },
                {
                    "label": "Journal Entry",
                    "fieldname": "je",
                    "fieldtype": "Link",
                    "options": "Journal Entry",
                    "width": 140,
                },
                {
                    "label": "Income Account",
                    "fieldname": "income_account",
                    "fieldtype": "Data",
                    "width": 160,
                },
                {
                    "label": "JEA Name",
                    "fieldname": "jea_name",
                    "fieldtype": "Data",
                    "width": 140,
                },
                {
                    "label": "Remarks",
                    "fieldname": "remarks",
                    "fieldtype": "Data",
                    "width": 140,
                },
                {
                    "label": "Donor Name[DJ]",
                    "fieldname": "donor_name",
                    "fieldtype": "Data",
                    "width": 160,
                },
                {
                    "label": "Donor Name[JE]",
                    "fieldname": "donor_name_accounts",
                    "fieldtype": "Data",
                    "width": 160,
                },
                {
                    "label": "Receipt Date",
                    "fieldname": "receipt_date",
                    "fieldtype": "Date",
                    "width": 120,
                },
                {
                    "label": "Posting Date",
                    "fieldname": "posting_date",
                    "fieldtype": "Date",
                    "width": 120,
                },
                {
                    "label": "Cheque Date",
                    "fieldname": "cheque_date",
                    "fieldtype": "Date",
                    "width": 120,
                },
                {
                    "label": "Payment Method",
                    "fieldname": "payment_method",
                    "fieldtype": "Data",
                    "width": 120,
                },
                {
                    "label": "Seva Type",
                    "fieldname": "seva_type",
                    "fieldtype": "Data",
                    "width": 120,
                },
                {
                    "label": "Amount [DJ]",
                    "fieldname": "amount_dj",
                    "fieldtype": "Currency",
                    "width": 120,
                },
                {
                    "label": "Amount [JE]",
                    "fieldname": "amount_erp",
                    "fieldtype": "Currency",
                    "width": 120,
                },
                {
                    "label": "Amount Diff",
                    "fieldname": "amount_diff",
                    "fieldtype": "Currency",
                    "width": 120,
                },
                {
                    "label": "ID Type",
                    "fieldname": "id_type",
                    "fieldtype": "Data",
                    "width": 120,
                },
                {
                    "label": "ID Number",
                    "fieldname": "id_number",
                    "fieldtype": "Data",
                    "width": 120,
                },
                {
                    "label": "Contact",
                    "fieldname": "contact",
                    "fieldtype": "Data",
                    "width": 120,
                },
                {
                    "label": "Address",
                    "fieldname": "address",
                    "fieldtype": "Data",
                    "width": 200,
                },
            ]
        )
    return columns
