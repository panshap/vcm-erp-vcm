import frappe


def execute():
    # txs = frappe.get_all(
    #     "Bank Transaction",
    #     filters=[["unallocated_amount", "=", 0], ["status", "=", "Unreconciled"]],
    #     pluck="name",
    # )
    # for tx in txs:
    #     frappe.db.set_value("Bank Transaction", tx, "status", "Reconciled")
    # frappe.db.commit()
    # for batch in frappe.get_all("PG Upload Batch", fields=["name", "final_amount"]):
    #     if batch["final_amount"] == 0:
    #         frappe.db.set_value("PG Upload Batch", batch["name"], "status", "Closed")
    # frappe.db.commit()

    ## Disable Role Item & Supplier Creator
    frappe.db.set_value("Role", "Item & Supplier Creator", "disabled", 1)

    for role_assign in frappe.get_all(
        "Has Role",
        filters={"role": "Item & Supplier Creator"},
        fields=["name", "parent", "parenttype"],
    ):
        if role_assign["parenttype"] == "User":
            user_doc = frappe.get_doc("User", role_assign["parent"])
            new_role_exists = False
            for role_child in user_doc.roles:
                if role_child.role == "Item Manager":
                    new_role_exists = True
            if not new_role_exists:
                user_doc.append("roles", {"role": "Item Manager"})
                user_doc.save()
        if role_assign["parenttype"] == "Role Profile":
            role_profile_doc = frappe.get_doc("Role Profile", role_assign["parent"])
            new_role_exists = False
            for role_child in role_profile_doc.roles:
                if role_child.role == "Item Manager":
                    new_role_exists = True
            if not new_role_exists:
                role_profile_doc.append("roles", {"role": "Item Manager"})
                role_profile_doc.save()
        frappe.delete_doc("Has Role", role_assign["name"])

    frappe.db.commit()
