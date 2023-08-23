# Copyright (c) 2021, Tara Technologies
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, throw
from frappe.utils import flt
from erpnext.accounts.doctype.journal_entry.journal_entry import JournalEntry

class HKMJJournalEntry(JournalEntry):
	@property
	def donation_suspense_account(self):
		if not hasattr(self, "__donation_suspense_account"):
			self.__donation_suspense_account = frappe.get_cached_value('Company', self.company, 'donation_suspense_account')

		return self.__donation_suspense_account

	def validate(self):
		super(HKMJJournalEntry, self).validate()
		self.validate_dr_number()
		# Based on Date, Reference No., 
		# self.validate_duplicate_entry()

	def on_submit(self):
		self.validate_suspense_cleared_amount()
		self.set_suspense_amount()
		self.set_suspense_cleared_amount()
		self.validate_gst_entry()
		super(HKMJJournalEntry, self).on_submit()

	def on_cancel(self):
		self.set_suspense_cleared_amount()
		super(HKMJJournalEntry, self).on_cancel()

	def validate_donation_suspense_account(self):
		pass

	def validate_suspense_cleared_amount(self):
		cleared_amount = flt(sum([flt(d.debit) + flt(d.credit) for d in self.get("accounts") if d.account == self.donation_suspense_account and d.suspense_jv != '']))
		for d in self.get_suspense_clearance_entry():
			suspense_amount = frappe.get_cached_value('Journal Entry Account', {"docstatus": 1, "parent": d.suspense_jv, "account": d.account }, 'credit')
			if d.debit > suspense_amount:
				frappe.throw(_("""Cleared amount <b>{0}</b> can not be greater 
					than to uncleared amount <b>{1}</b> against suspense entry <b>{2}</b>.\n
					Please enter correct amount.""".format(
						d.debit, suspense_amount, d.suspense_jv
					)))

	def set_suspense_amount(self):
		if self.is_suspense_entry():
			suspense_amount = flt(sum([d.credit for d in self.get("accounts") if d.account == self.donation_suspense_account]))			
			self.cleared_amount = 0
			self.uncleared_amount = suspense_amount

	def set_suspense_cleared_amount(self):
		for d in self.get("accounts"):
			if d.suspense_jv and d.account==self.donation_suspense_account:
				cleared_amount =  d.debit + (d.credit*-1)
				cleared_amount = cleared_amount*-1 if self.docstatus == 2 else cleared_amount
				suspense_jv_doc = frappe.get_doc('Journal Entry', d.suspense_jv)
				suspense_jv_doc.cleared_amount += cleared_amount
				suspense_jv_doc.uncleared_amount -= cleared_amount
				suspense_jv_doc.save()			

	def is_suspense_entry(self):
		return list(set([d.account for d in self.get("accounts") if d.account==self.donation_suspense_account and d.credit > 0 ]))

	def get_suspense_clearance_entry(self):
		return [d for d in self.get("accounts") if d.suspense_jv and d.account==self.donation_suspense_account and d.debit > 0]

	def validate_gst_entry(self):
		from hkm.erpnext___custom.extend.accounts_controller import validate_gst_entry
		validate_gst_entry(self)

	def validate_dr_number(self):
		dr_nos = [d.dr_no for d in self.get("accounts") if d.dr_no]
		if not dr_nos:
			return
			
		conditions = " and doc.company='%s' and doc.name !='%s'"%(self.company,self.name)
		conditions += f""" and acc.dr_no in ({', '.join(frappe.db.escape(dr_no) for dr_no in dr_nos)})"""
		dr_no_map = frappe._dict()
		for d in frappe.db.sql(""" select doc.name, acc.dr_no 
			from `tabJournal Entry` doc, `tabJournal Entry Account` acc
			where doc.docstatus < 2
			and acc.parent = doc.name
			and acc.debit > 0
			{conditions}""".format(conditions=conditions), as_dict=1):
			dr_no_map.setdefault(d.dr_no, d.name)

		for d in self.get("accounts"):
			parent = dr_no_map.get(d.dr_no)
			if parent:
				frappe.throw(_("Row #{0} DR Number {1} is already used in Journal Entry {2}.<br>Please enter different number.").format(
					d.idx, 
					frappe.bold(d.dr_no), 
					frappe.bold(parent)
				), title=_("Duplicate DR Entry"))

	# def validate_reference_number(self):
	# 	matchings = frappe.db.get_all("Journal Entry", filters={'cheque_no':self.cheque_no,'docstatus':1})
	# 	if len(matchings)>0:
	# 		frappe.throw(_("There are already entries against this reference number in ERP. So duplicate is not allowed."))
	# 	return

def update_suspense_jv_cleared_amount(suspense_jv=None):
	conditions = ""
	if suspense_jv:
		conditions = " and jv.name='%s'"%suspense_jv

	frappe.db.sql("""
		update `tabJournal Entry` jv 
		inner join `tabJournal Entry Account` jva on(jva.parent = jv.name)
		inner join `tabCompany` comp on (comp.name = jv.company)
		left join (
			select cl.suspense_jv, cl.account, sum((cl.debit+(cl.credit*-1))) as cleared_amount
		    from `tabJournal Entry Account` cl
			where cl.docstatus = 1
		    group by cl.suspense_jv, cl.account
		) cl on (cl.suspense_jv = jv.name and cl.account = jva.account)
		set jv.cleared_amount = ifnull(cl.cleared_amount, 0),
		    jv.uncleared_amount = jva.credit - ifnull(cl.cleared_amount, 0)
		where jv.docstatus = 1
		and jva.account = comp.donation_suspense_account
		and ifnull(jva.suspense_jv, '') = ''
		{0}""".format(conditions))	