# Copyright (c) 2022, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class HKMERPNextSettings(Document):
	pass

@frappe.whitelist()
def disable_old_users():
	if not 'System Manager' in frappe.get_roles(frappe.session.user):
		return
	users = frappe.get_list('User', pluck='name', filters={'enabled':1})
	for user in users:
		recent_logs = frappe.db.sql("""
				select timestamp
				from `tabAccess Log`
				where timestamp < DATE_SUB(CURDATE(), INTERVAL 2 month)
				and user = '{}'
				order by timestamp desc;
					""".format(user),as_dict=1)
		if len(recent_logs) == 0:
			frappe.db.set_value("User", user, 'enabled', 0)
	return

