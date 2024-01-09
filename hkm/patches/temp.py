import frappe


def execute():
    txs = frappe.get_all(
        "Bank Transaction",
        filters=[["unallocated_amount", "=", 0], ["status", "=", "Unreconciled"]],
        pluck="name",
    )
    for tx in txs:
        frappe.db.set_value("Bank Transaction", tx, "status", "Reconciled")
    frappe.db.commit()
