

import frappe,click

def execute():
	delete_custom_docperms()

def delete_custom_docperms():
	doctypes = get_doctypes()

	alm_perms = frappe.get_all("Custom DocPerm", [	["parent", "in", doctypes ]	], pluck="name")
	click.secho("Deleting Custom Doctype Perms")
	for perm in alm_perms:
		frappe.delete_doc("Custom DocPerm", perm , ignore_missing=True)

def get_doctypes():
	return [
			"ALM", "ALM Level","Ashram Store Inward","Ashram Store Item","Ashram Store Item Issue","Ashram Store User",
			"Bed",
			"Block GST Entry Settings",
			"Devotee",
			"DocType",
			"ECS",
			"FOLK Guide",
			"FOLK Institute Degree",
			"FOLK Redirect",
			"FOLK Residency",
			"FOLK Residency Rent",
			"FOLK Residency Rent Return",
			"FOLK Student",
			"FOLK Student Interaction",
			"Freeze Transaction Settings",
			"IT Brand",
			"IT Category",
			"IT Device",
			"IT Specification",
			"IT UOM",
			"IT User",
			"MRN Usability Settings",
			"Prasadam CPN Request",
			"Supplier Creation Request"
			]
			