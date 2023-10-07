import frappe
import erpnext
from hkm.erpnext___custom.overrides.material_request import check_items_are_not_from_template, validate_work_order_item


def validate(self, method=None):
    check_items_are_not_from_template(self)
    validate_work_order_item(self)
    update_extra_description_from_mrn(self, method)
    validate_mrn_availble(self)


def validate_mrn_availble(self):
    for item in self.items:
        if item.material_request is None:
            frappe.throw(
                f"Item {item.item_name} doesn't have a linked MRN. Seems this Purchase Order is not linked from any MRN."
            )


def before_insert(self, method=None):
    set_naming_series(self)
    validate_work_request_status(self)


def set_naming_series(self):
    if self.meta.get_field("for_a_work_order") and self.for_a_work_order:
        self.naming_series = "WOR-ORD-.YYYY.-"
    else:
        self.naming_series = "PUR-ORD-.YYYY.-"


def update_extra_description_from_mrn(self, method=None):
    descriptions = []
    mrns = frappe.db.get_all("Purchase Order Item", pluck="material_request", filters={"parent": self.name})
    mrns = set(mrns)
    for mrn in mrns:
        if mrn is not None:
            mrn_doc = frappe.get_doc("Material Request", mrn)
            if mrn_doc.description is not None:
                descriptions.append(mrn_doc.purpose + "\n" + mrn_doc.description)
    description = ", ".join(descriptions)
    if self.extra_description == None or self.extra_description.strip() == "":
        self.extra_description = description
    return


def validate_work_request_status(doc):
    if not (doc.meta.get_field("for_a_work_order") and doc.for_a_work_order == 1):
        return
    mrns = []
    for row in doc.get("items"):
        mrn = row.material_request
        if mrn is not None and mrn not in mrns:
            mrns.append(mrn)
    for mrn in mrns:
        mrn_doc = frappe.get_doc("Material Request", mrn)
        if mrn_doc.completed == 1:
            frappe.throw(
                "<p> Work Order is not allowed in respect to this work request ({}) because it has been marked as <b class='text-danger'>COMPLETED</b> by the User (MRN Approver).</p>".format(
                    mrn_doc.name
                )
            )
    return
