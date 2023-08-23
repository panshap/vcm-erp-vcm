// Copyright (c) 2021, Narahari Das and contributors
// For license information, please see license.txt

frappe.ui.form.on('User Company Allowed', {
	validate: function(frm) {
		frappe.call({
			method:"frappe.client.get_value",
			args:{
				doctype: "User Company Allowed",
                fieldname: "name",
                filters:{
                	user: frm.doc.user,
                	company:frm.doc.company,
                }
			},
			callback:function(response){
				var user = response.message;
				console.log(user);
				if (!jQuery.isEmptyObject(user)) {
	                  	frappe.msgprint("Same User with the Same Company is Already Exist in Record.");
						frappe.validated=false;
	    				return false;
	             }
			}
		});
	}
});
