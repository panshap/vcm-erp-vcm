# Copyright (c) 2022, Tara Technologies
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute():
	from hkm.erpnext___custom.extend.journal_entry import update_suspense_jv_cleared_amount
	frappe.reload_doc("Accounts", "doctype", "Journal Entry")
	update_suspense_jv_cleared_amount()
