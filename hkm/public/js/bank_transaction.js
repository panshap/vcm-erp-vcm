frappe.ui.form.on("Bank Transaction", {
    onload(frm) {
        frm.add_custom_button(__("Create Journal Entry"), function () {
            frappe.call({
                method:
                    "hkm.erpnext___custom.overrides.journal_entry.get_journal_entry_from_statement",
                args: {
                    statement: frm.doc.name,
                },
                callback: (r) => {
                    var doc = frappe.model.sync(r.message);
                    frappe.set_route("Form", doc[0].doctype, doc[0].name);
                },
            });
        }, "Actions");

    },
});
