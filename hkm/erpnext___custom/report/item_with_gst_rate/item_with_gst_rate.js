// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["ITEM With GST Rate"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd":1,
			"width":80,
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname": "price_list",
			"label": __("Price List"),
			"fieldtype": "Link",
			"options": "Price List",
			"reqd":1,
			"width":80,
			"default": frappe.defaults.get_user_default("Price List")
		},
		{
			"fieldname": "item_group",
			"label": __("Item Group"),
			"fieldtype": "Link",
			"options": "Item Group",
			"width":80
		},
	],
	getEditor: function(colIndex, rowIndex, value, parent, column, row, data) {
		// colIndex, rowIndex of the cell being edited
		// value: value of cell before edit
		// parent: edit container (use this to append your own custom control)
		// column: the column object of editing cell
		// row: the row of editing cell
		// data: array of all rows

		const control = frappe.ui.form.make_control({
			parent: parent,
			df: {
				label: '',
				fieldname: doctype,
				fieldtype: 'Link',
				options: doctype
			},
			render_input: true,
			only_input: true,
		});

		let oldValue = '';

		return {
			// called when cell is being edited
			initValue(value) {
				control.input.focus();
				control.input.value = value;
				oldValue = value;
			},
			// called when cell value is set
			setValue(newValue) {
				// ----------- Do whatever is needed here.
				control.input.value = newValue;
			},
			// value to show in cell
			getValue() {
				return control.input.value;
			}
		}
	}
};
