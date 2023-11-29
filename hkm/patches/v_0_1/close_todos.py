import frappe
def execute():
    for todo in frappe.db.sql("""
                select reference_type, reference_name
                from `tabToDo`
                where status = 'Open'
                group by reference_type, reference_name
                    """,as_dict = 1):
        docstatus = frappe.get_value(todo['reference_type'],todo['reference_name'],'docstatus')
        if docstatus != 0:
            frappe.db.sql(f"""
                            update `tabToDo`
                            set status = 'Closed'
                            where reference_type = '{todo['reference_type']}' and  reference_name = '{todo['reference_name']}'
                            """)