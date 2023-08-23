# Copyright (c) 2022, Tara Technologies
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute():
	docs = frappe.get_all("Ashram Library Book Ledger", filters = {"voucher_type" : "Ashram Library Book Inward"})
	for doc in docs:
		frappe.db.set_value("Ashram Library Book Ledger", doc["name"], 'transaction', 'Inward')