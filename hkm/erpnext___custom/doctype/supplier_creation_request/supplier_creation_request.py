# Copyright (c) 2022, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class SupplierCreationRequest(Document):
    pass


@frappe.whitelist()
def create_supplier(source_name, target_doc=None):
    # def update_item(source, target, source_parent):
    # 	#target.warehouse = source_parent.warehouse

    doclist = get_mapped_doc(
        "Supplier Creation Request",
        source_name,
        {
            "Supplier Creation Request": {
                "doctype": "Supplier",
                "field_map": {
                    "supplier_name": "supplier_name",
                    "supplier_type": "supplier_type",
                    "supplier_creation_request": "name",
                },
            },
        },
        target_doc,
    )

    if hasattr(doclist, "custom_aadhar_no"):
        doclist.custom_aadhar_no = frappe.db.get_value(
            "Supplier Creation Request", source_name, "aadhar_no"
        )

    return doclist
