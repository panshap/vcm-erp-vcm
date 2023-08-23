frappe.ui.form.on('Stock Entry', {
    onload:function(frm){
        frm.set_query("default_difference_account", function() {
			return {
				filters: { root_type:'Expense', company: frm.doc.company }
			}
		});
    },
	default_difference_account:function(frm){
	    var entries = frm.doc.items
	    for(var i=0;i<entries.length;i++)
            {  
                frappe.model.set_value('Stock Entry Detail',entries[i].name, 'expense_account', frm.doc.default_difference_account);
            }
        //frm.reload_doc();
	}
	
})

frappe.ui.form.on('Stock Entry Detail', {
	item_code: function(frm, cdt, cdn) {
	    frappe.model.set_value(cdt, cdn, 'expense_account', frm.doc.default_difference_account);
	}
})