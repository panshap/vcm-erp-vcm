frappe.ui.form.on('Sales Invoice', {
    onload:function(frm){
        frm.set_query("default_sales_income_account", function() {
			return {
				filters: { root_type:'Income', is_group : 0, company: frm.doc.company }
			}
		});
    },
	before_save:function(frm){
		if(frm.doc.default_sales_income_account){
			frm.events.update_default_sales_income_account(frm);
		}
	},
	default_sales_income_account:function(frm){
	    frm.events.update_default_sales_income_account(frm);
	},
	update_default_sales_income_account(frm){
		var entries = frm.doc.items
	    for(var i=0;i<entries.length;i++)
            {  
                frappe.model.set_value('Sales Invoice Item',entries[i].name, 'income_account', frm.doc.default_sales_income_account);
            }
		frm.refresh_field('items');
	}
	
})

// frappe.ui.form.on('Sales Invoice Item', {
// 	refresh(frm) {
// 		// your code here
// 	},
// 	item_code:function(frm,cdt,cdn){

// 	},
// 	items_add:function(frm,cdt,cdn){
// 		console.log(cdn);
// 		frm.events.update_default_sales_income_account(frm);
// 	},
// })

// frappe.ui.form.on('Sales Invoice Item', {
// 	item_code: function(frm, cdt, cdn) {
// 	    frappe.model.set_value(cdt, cdn, 'income_account', frm.doc.default_difference_account);
// 	}
// })