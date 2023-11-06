// Copyright (c) 2023, Narahari Dasa and contributors
// For license information, please see license.txt

frappe.ui.form.on('Item Code Printer', {
    refresh(frm) {
        frm.add_custom_button(__("Print Item Codes"), async function () {
            if (frm.doc.item_code && frm.doc.company && frm.doc.price_list && frm.doc.quantity) {
                console.log(frm.doc.item_code)
                frappe.ui.form.qz_connect()
                    .then(function () {
                        var config = qz.configs.create("Godex G500");            // Exact printer name from OS
                        var print_data = [];
                        var shift = 310;
                        frappe.call({
                            method: 'hkm.erpnext___custom.godex_print.filter_sellable_items',
                            args: {
                                items: [frm.doc.item_code],
                                price_list: frm.doc.price_list,
                                company: frm.doc.company
                            },

                            freeze: true,
                            callback: (r) => {
                                console.log(r.message);
                                var items_detailed = r.message;
                                var total_items = [];
                                var qty = frm.doc.quantity;
                                console.log(qty);
                                for (var i = 0; i < qty; i++) {
                                    total_items.push(items_detailed[0])
                                }

                                console.log(total_items);
                                for (var j = 0; j < total_items.length; j = j + 2) {
                                    var group_string = "";
                                    for (var g = 0; g < 2; g++) {
                                        if ((j + g) < total_items.length) {
                                            group_string += `\nBA3,` + (4 + g * shift) + `,8,1,2,63,0,0,` + total_items[j + g]['code'] +
                                                `\nAB,` + (4 + g * shift) + `,70,1,1,0,0E,` + total_items[j + g]['code'] +
                                                `\nAA,` + (4 + g * shift) + `,104,1,1,0,0E,` + total_items[j + g]['name'] +
                                                `\nAC,` + (4 + g * shift) + `,131,1,1,0,0E,Rs.` + total_items[j + g]['rate']
                                        }
                                    }
                                    print_data.push(frm.events.get_EZPL_string(frm, group_string));
                                }
                                return qz.print(config, print_data)
                            },
                            error: (r) => {
                                // on error
                            }
                        });


                    })
                    .then(frappe.ui.form.qz_success)
                    .catch(err => {
                        frappe.ui.form.qz_fail(err);
                    });
                // frm.events.on_success(frm);
            } else {
                frappe.throw("Fields for printing Item Labels are not available.");
            }

            //perform desired action such as routing to new form or fetching etc.
        }, __("Utilities"));
        frm.add_custom_button(__("Print Dates"), function () {
            if (frm.doc.date && frm.doc.quantity_date) {
                frappe.ui.form.qz_connect()
                    .then(function () {
                        var config = qz.configs.create("Godex G500");            // Exact printer name from OS
                        var print_data = [];
                        var shift = 310;
                        for (var j = 0; j < frm.doc.quantity_date; j = j + 2) {
                            var group_string = "";
                            for (var g = 0; g < 2; g++) {
                                if ((j + g) < frm.doc.quantity_date) {
                                    group_string +=
                                        `\nAB,` + (4 + g * shift) + `,50,2,2,0,0E,` + frappe.format(frm.doc.date, { fieldtype: 'Date' });
                                }
                            }
                            print_data.push(frm.events.get_EZPL_string(frm, group_string));
                        }
                        return qz.print(config, print_data)
                    })
                    .then(frappe.ui.form.qz_success)
                    .catch(err => {
                        frappe.ui.form.qz_fail(err);
                    });
                // frm.events.on_success(frm)
            }
            else {
                frappe.throw("Fields for printing Date Labels are not available.");
            }
        }, __("Utilities"));
    },
    on_success: function (frm) {
        frm.set_value("item_code", null);
        frm.set_value("quantity", null);
        frm.save();
    },
    get_EZPL_string: function (frm, data) {
        // Please refer to documentation for seetings : https://www.godexprinters.co.uk/downloads/manuals/desktop/EZPL_EN_J_20180226.pdf
        var settings = `
                        ^Q23,3
                        ^W76
                        ^H10
                        ^P1
                        ^S2
                        ^AD
                        ^C1
                        ^R8
                        ~Q+8
                        ^O0
                        ^D0
                        ^E18
                        ~R255
                        ^L
                        `
        var end = `\nE`
        var str = settings + data + end
        var arr_data = str.split("\n");
        var final_data = "";
        for (var index in arr_data) {
            final_data += arr_data[index].trim() + "\x0D";
        }
        return final_data;
    }
})