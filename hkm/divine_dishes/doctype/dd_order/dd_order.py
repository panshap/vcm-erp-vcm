# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

DEFAULT_PRICE_LIST = "Online Selling"

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
            item_code = frappe.get_value("Website Item", item.website_item, "item_code")
            item.price = self.get_item_price(item_code)
            item.amount = item.price * item.qty
            total_amount += item.amount
        self.total_amount = total_amount

    def get_item_price(self, item_code):
        prices = frappe.get_all(
            "Item Price", filters={"item_code": item_code, "price_list": DEFAULT_PRICE_LIST}, fields=["price_list_rate"]
        )
        return prices[0]["price_list_rate"]
