import json
import frappe


@frappe.whitelist()
def upload_preachers():
    preachers = json.loads(frappe.request.data)
    for p in preachers:
        if not frappe.db.exists("LLP Preacher", p):
            doc = frappe.get_doc(
                {"doctype": "LLP Preacher", "full_name": p, "initial": p}
            )
            doc.insert()
    return


@frappe.whitelist()
def upload_salutations():
    salutations = json.loads(frappe.request.data)
    for s in salutations:
        if not frappe.db.exists("Salutation", s):
            doc = frappe.get_doc({"doctype": "Salutation", "salutation": s})
            doc.insert()
    return


