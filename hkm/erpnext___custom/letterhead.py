import frappe

EXEMPT_DOCTYPES = ["POS Invoice"]


def query(self, method=None):
    if self.doctype in EXEMPT_DOCTYPES:
        return
    if hasattr(self, "letter_head") and self.get("company"):
        self.letter_head = frappe.db.get_value(
            "Company", self.get("company"), "default_letter_head"
        )
