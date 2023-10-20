import frappe


def execute():
    print("executing")
    for d in frappe.get_all(
        "Journal Entry", filters=[["bank_statement_name", "!=", ""], ["docstatus", "=", 1]], pluck="name"
    ):
        print(d)
        frappe.db.set_value("Journal Entry", d, "bank_statement_name", None)
    frappe.db.commit()
