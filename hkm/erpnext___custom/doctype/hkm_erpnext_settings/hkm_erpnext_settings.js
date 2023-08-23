// Copyright (c) 2022, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.ui.form.on('HKM ERPNext Settings', {
	refresh: function(frm) {

      frm.add_custom_button(__('Disable old users'), function(){
	      	frappe.warn('Are you sure you want to disable all inactive users?',
			    'Not accessed ERP for last 60 days.',
			    () => {
			        frappe.call({
					    method: 'hkm.erpnext___custom.doctype.hkm_erpnext_settings.hkm_erpnext_settings.disable_old_users',
					    freeze: true,
					    callback: (r) => {
					    	console.log(r);
				    		frappe.show_alert({
						    message:__('All the inactive users are disabled.'),
						    indicator:'green'
							}, 5);
					    },
					    error: (r) => {
					  //       frappe.show_alert({
							//     message:__('There is some error'),
							//     indicator:'red'
							// }, 5);
					    }
					})
			    },
			    'Continue',
			    true // Sets dialog as minimizable
			);
	});
}
});
