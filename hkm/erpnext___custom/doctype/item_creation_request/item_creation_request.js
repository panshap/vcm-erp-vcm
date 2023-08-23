// Copyright (c) 2022, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item Creation Request', {
	refresh: function(frm) {
		if(frm.doc.workflow_state == "Approved"){
			frm.add_custom_button(__("Create Item"), function() {
	        frappe.model.open_mapped_doc({
	    			method: "hkm.erpnext___custom.doctype.item_creation_request.item_creation_request.create_item",
	    			frm: frm
	    		});
	    	});
		}
		
	},
	tax_category:function(frm){
		console.log("tax");
		frappe.db.get_doc('Item Tax Template', frm.doc.tax_category).then(doc => {
						// frm.doc.default_company = doc.company
						frm.set_value("default_company", doc.company);
					});
	},
	onload:function(frm){
        frm.set_query("default_sales_income_account", function() {
			
			return {
				filters: { root_type:'Income', is_group:0 , company: frm.doc.default_company }
			}
		});
		frm.set_query("tax_category", function() {
			
			return {
				filters: {company: frm.doc.default_company }
			}
		});
    },
});