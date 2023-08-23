// Copyright (c) 2020, Tara Technologies
// For license information, please see license.txt

frappe.ui.form.on("Journal Entry", {
	onload: function(frm) {
		//frm.trigger("setup_queries");
		frm.set_query("suspense_jv", "accounts", function(doc, cdt, cdn) {
			return {
				query: "hkm.erpnext___custom.extend.queries.uncleared_suspense_voucher_query",
				filters: {
					'company': frm.doc.company
				}
			}
		});		
	},
	setup_queries: function() {
		frm.set_query("suspense_jv", "accounts", function(doc, cdt, cdn) {
			return {
				query: "hkm.erpnext___custom.extend.queries.uncleared_suspense_voucher_query",
				filters: {
					'company': frm.doc.company
				}
			}
		});
	},	

});
$.extend(erpnext.journal_entry, {
	account_query: function(frm) {
		var filters = {
			company: frm.doc.company,
			is_group: 0
		};
		return { filters: filters };
	},
});
