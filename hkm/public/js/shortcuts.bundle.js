frappe.ui.keys.add_shortcut({
    description: "Show Balance Sheet",
    shortcut:"alt+b",
    action:()=>{
        frappe.set_route("List","Journal Entry");
    }
})