# Copyright (c) 2021, Tara Technologies
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute():
	frappe.reload_doc("Setup", "doctype", "Company")
	frappe.db.sql("""
			update tabCompany comp
			inner join (
			select jv.company, jva.account
			from `tabJournal Entry` jv 
			inner join `tabJournal Entry Account` jva on(jva.parent = jv.name)
			where jv.docstatus = 1
			and jv.voucher_type = 'Bank Entry'
			and jva.credit_in_account_currency > 0
			and jva.account like 'Suspense%'
			group by jv.company, jva.account
			) jv on (jv.company = comp.name)
			set comp.donation_suspense_account = jv.account
			""")
