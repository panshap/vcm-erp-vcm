// Copyright (c) 2022, HKM and contributors
// For license information, please see license.txt

{% include 'erpnext/public/js/controllers/buying.js' %};

frappe.provide("hkm.buying");

frappe.ui.form.on('BOQ', {
	setup: function(frm) {
		frm.custom_make_buttons = {
			'Material Request': 'Material Request',
		};
		frm.set_df_property("items", "allow_bulk_edit", 0);
	},	
	onload: function(frm) {
		frm.set_query("department", function(doc){
			return {
				filters: {'company': doc.company, 'is_group':0}
			};
		});
		frm.set_query("set_warehouse", function(doc){
			return {
				filters: {'company': doc.company, 'is_group':0}
			};
		});		
		frm.set_query("warehouse", "items", function(doc){
			return {
				filters: {'company': doc.company, 'is_group':0}
			};
		});				
		frm.set_query("from_warehouse", "items", function(doc){
			return {
				filters: {'company': doc.company, 'is_group':0}
			};
		});						
		frm.set_query("boq_item_code", function(doc){
			return {
				filters: {'is_stock_item': 0, 'has_variants': 0}
			};
		});		
	},
	refresh: function(frm) {
		if(frm.doc.status === "Open"){
			frm.events.make_custom_buttons(frm);	
		}else if(frm.doc.status === "Completed"){
			frm.set_read_only(true);
			frm.disable_save();
		}
		
	},
	set_from_warehouse: function(frm) {
		if (frm.doc.set_from_warehouse) {
			frm.doc.items.forEach(d => {
				frappe.model.set_value(d.doctype, d.name,
					"from_warehouse", frm.doc.set_from_warehouse);
			})
		}
	},
	make_custom_buttons: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Material Request"),
				() => frm.events.make_material_request(frm), __("Create"));
		}
	},	
	make_material_request: function(frm) {
		frappe.model.open_mapped_doc({
			method: "hkm.erpnext___custom.doctype.boq.boq.make_material_request",
			frm: frm
		});
	},	
});
frappe.ui.form.on("BOQ Item", {
	qty: function (frm, doctype, name) {
		var d = locals[doctype][name];
		d.stock_qty = d.qty;
	},	
	uom: function (frm, doctype, name) {
		var d = locals[doctype][name];
		d.stock_uom = d.uom;
		d.conversion_factor = 1;
	},
});
hkm.BOQController = erpnext.buying.BuyingController.extend({
	item_code: function() {
		return;
	},
	validate_company_and_party: function() {
		return true;
	},

	calculate_taxes_and_totals: function() {
		this.calculate_item_values();
		this.frm.refresh_fields();
	},
	calculate_item_values: function() {
		let me = this;
		if (!this.discount_amount_applied) {
			$.each(this.frm.doc["items"] || [], function(i, item) {
				frappe.model.round_floats_in(item);
				item.net_rate = item.rate;

				if ((!item.qty) && me.frm.doc.is_return) {
					item.amount = flt(item.rate * -1, precision("amount", item));
				} else if ((!item.qty) && me.frm.doc.is_debit_note) {
					item.amount = flt(item.rate, precision("amount", item));
				} else {
					item.amount = flt(item.rate * item.qty, precision("amount", item));
				}

				item.net_amount = item.amount;
				item.item_tax_amount = 0.0;
				item.total_weight = flt(item.weight_per_unit * item.stock_qty);

				//me.set_in_company_currency(item, ["rate", "amount"]);
			});
		}
	},
});

// for backward compatibility: combine new and previous states
$.extend(cur_frm.cscript, new hkm.BOQController({frm: cur_frm}));	