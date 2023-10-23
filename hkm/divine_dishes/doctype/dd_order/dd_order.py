# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DDOrder(Document):
    def validate(self):
        self.validate_address()

    def validate_address(self):
        addresses = frappe.get_all(
            "DD User Address",
            filters=[["user", "=", self.user], ["status", "=", "Approved"]],
            pluck="name",
        )
        if len(addresses) == 0:
            frappe.throw("At least one Address is required to be approved.")
        return

    def before_save(self):
        total_amount = 0
        for item in self.items:
            frappe.errprint(item.item)
            price = frappe.get_value("DD Item",item.item,"price")
            item.amount = price * item.qty
            total_amount += item.amount
        self.total_amount = total_amount
    
    def on_submit(self):
        if self.status == "Delivered":
            settings_doc = frappe.get_cached_doc("Divine Dishes Settings")
            doc = frappe.get_doc(
                {
                    "doctype": "App Notification",
                    "app": settings_doc.firebase_app,
                    "notify": 1,
                    "user": self.user,
                    "subject": "Order Delivered!",
                    "message": f"Please check the Order for more details.",
                    "is_route": 1,
                    "route": f"/order/{self.name}",
                }
            )
            doc.insert(ignore_permissions=True)

@frappe.whitelist()
def mark_delivered(docname):
    doc = frappe.get_doc("DD Order",docname)
    doc.status = "Delivered"
    doc.save(ignore_permissions=True)
