# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator


class DDUserAddress(WebsiteGenerator):
    def before_save(self):
        if self.primary == 1:
            if self.status == "Pending Approval":
                frappe.throw("Not Allowed! The address is still not approved.")
            self.unset_all_primary()

    def unset_all_primary(self):
        other_addresses = frappe.get_list(
            "DD User Address",
            filters=[["name", "!=", self.name], ["user", "=", self.user], ["primary", "=", 1]],
            pluck="name",
        )

        for oa in other_addresses:
            frappe.db.set_value("DD User Address", oa, "primary", 0)
