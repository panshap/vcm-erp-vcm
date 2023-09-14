# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DDSubscription(Document):
    def validate(self):
        self.validate_duplicate_and_qty()

    def validate_duplicate_and_qty(self):
        documents = []
        for d in self.get("schedule"):
            if d.week_day in documents:
                frappe.throw("Row#{0} Duplicate record not allowed for {1}".format(d.idx, d.week_day))
            if d.qty == 0:
                frappe.throw("Row#{0} contains zero quantity".format(d.idx))

            documents.append(d.week_day)
