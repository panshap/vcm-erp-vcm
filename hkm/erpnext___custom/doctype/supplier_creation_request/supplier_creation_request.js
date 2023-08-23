// Copyright (c) 2022, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.ui.form.on('Supplier Creation Request', {
	refresh: function(frm) {
		frm.add_custom_button(__("Create Supplier"), function() {
	        frappe.model.open_mapped_doc({
	    			method: "hkm.erpnext___custom.doctype.supplier_creation_request.supplier_creation_request.create_supplier",
	    			frm: frm
	    		});
	    });
	}
});