frappe.ui.form.on('Material Request', {
	refresh: function(frm){
		if (frm.doc.docstatus==0) {
			frm.add_custom_button(__("Bill of Quantity"),
				() => frm.events.get_items_from_boq(frm), __("Get Items From"));
		}

	},
    onload:function(frm){
        frm.set_query("material_purchase_link", function() {
			return {
				filters: {
					material_request_type: "Purchase",
					for_a_work_order: false,
				}
			}
		});
    },
	company:function(frm) {
	    frm.set_query('department', () => {
        return {
            filters: {
                company: frm.doc.company
                }
            };
        });
	},
	for_a_work_order:function(frm){
	    frm.events.filter_service_items(frm);
	},
    filter_service_items:function(frm){
            frm.set_query("item_code", "items", function(doc, cdt, cdn) {
    		return {
    			filters: {
    				is_stock_item: !doc.for_a_work_order,
					disabled:0
    			    }
    		    };
	        });
    },
	on_submit:function(frm){
	    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            'doctype': 'ToDo',
            'filters': {'reference_name': frm.doc.name,'status':'Open'},
            'fields':['owner']
            },
        callback: function(r) {
            for(var ind in r.message){
                frm.assign_to.remove(r.message[ind].owner);
                }
            }
    	});

	},
	get_items_from_boq: function(frm) {
		if (!frm.doc.boq){
			frappe.throw(__("This Material Request is not linked to BOQ."));
			return;
		}
		frappe.call({
			method: "hkm.erpnext___custom.doctype.boq.boq.get_boq_items",
			args: {
					"boq": frm.doc.boq,
				},
			callback: function(r) {
				if (!r.message) {
					frappe.throw(__("No pending BOQ item is available"));
				} else {
					let items = r.message;
					if (items.length === 0){
						frappe.msgprint(__("No pending BOQ item is available"));
						return;
					}
					$.each(items, function(i, item) {
						var d = frappe.model.add_child(cur_frm.doc, "Material Request Item", "items");
						d.item_code = item.item_code;
						d.item_name = item.item_name;
						d.description = item.item_name;
						d.item_description = item.item_name;
						d.warehouse = item.warehouse;
						d.uom = item.stock_uom;
						d.stock_uom = item.stock_uom;
						d.conversion_factor = item.conversion_factor;
						d.qty = item.qty;
						d.stock_qty = item.stock_qty;
						d.boq = item.boq;
						d.boq_item = item.boq_item;
						d.schedule_date = frm.doc.schedule_date;

					});
					refresh_field("items");
					frappe.msgprint(__("Added " + items.length + " BOQ item(s)<br><b>Please save your work.</b>"));
				}
				
			}
		});
	},  
});
// frappe.listview_settings['Material Request'] = {
// 	add_fields: ["material_request_type", "status", "per_ordered", "per_received", "transfer_status"],
// 	get_indicator: function(doc) {
// 		if(doc.status=="Stopped") {
// 			return [__("Stopped"), "red", "status,=,Stopped"];
// 		} else if(doc.transfer_status && doc.docstatus != 2) {
// 			if (doc.transfer_status == "Not Started") {
// 				return [__("Not Started"), "orange"];
// 			} else if (doc.transfer_status == "In Transit") {
// 				return [__("In Transit"), "yellow"];
// 			} else if (doc.transfer_status == "Completed") {
// 				return [__("Completed"), "green"];
// 			}
// 		} else if(doc.docstatus==1 && flt(doc.per_ordered, 2) === 0) {
// 			return [__("Pending"), "orange", "per_ordered,=,0"];
// 		} else if(doc.docstatus==1 && flt(doc.per_ordered, 2) < 100 && flt(doc.per_received,2) === 0) {
// 			return [__("Partially ordered"), "yellow", "per_ordered,<,100"];
// 		}  
// 		else if(doc.docstatus==1 && flt(doc.per_ordered, 2) <= 100 && flt(doc.per_received, 2) < 100) {
// 			if (doc.material_request_type == "Purchase" && flt(doc.per_received, 2) < 100 && flt(doc.per_received, 2) > 0) {
// 				return [__("Partially Received"), "yellow", "per_received,<,100"];
// 			} else if (doc.material_request_type == "Purchase" && flt(doc.per_received, 2) == 100) {
// 				return [__("Received"), "green", "per_received,=,100"];
// 			} else if (doc.material_request_type == "Purchase") {
// 				return [__("Ordered"), "green", "per_ordered,=,100"];
// 			} else if (doc.material_request_type == "Material Transfer") {
// 				return [__("Transfered"), "green", "per_ordered,=,100"];
// 			} else if (doc.material_request_type == "Material Issue") {
// 				return [__("Issued"), "green", "per_ordered,=,100"];
// 			} else if (doc.material_request_type == "Customer Provided") {
// 				return [__("Received"), "green", "per_ordered,=,100"];
// 			} else if (doc.material_request_type == "Manufacture") {
// 				return [__("Manufactured"), "green", "per_ordered,=,100"];
// 			}
// 		}
		
//  }
// };
// frappe.ui.form.on('Material Request Item', {
//     item_code(frm,cdt,cdn){
//         var mr_item = frappe.get_doc(cdt,cdn);
//         if(mr_item.item_code!=null)
//         frappe.db.get_doc('Item', mr_item.item_code)
//             .then(doc => {
//                 console.log(doc.specific_company,frm.doc.company)
//                 if(doc.specific_company!=null && doc.specific_company != frm.doc.company){
//                     msgprint("This item is not of this company");
//                     //frm.refresh_field('unbooked')
                    
//                 }
//             })
//     }
// })


frappe.ui.form.on('Material Request Item', { // The child table is defined in a DoctType called "Dynamic Link"
    item_code(frm, cdt, cdn) { // "links" is the name of the table field in ToDo, "_add" is the event
        
        let row = frappe.get_doc(cdt, cdn);
        if(row.item_code){
        	frappe.db.get_doc('Item', row.item_code).then(doc =>{
	        	console.log(doc);
	        	// var child = locals[cdt][cdn];
				
				if(doc.is_fixed_asset == 1){
					row.item_type = "Asset";
				}
				else if(doc.is_stock_item == 1){
					row.item_type = "Stock";
				}
				else{
					row.item_type = "Non-Stock";
				}
				frm.refresh_field("items");
	        });
        }
    },
    
});