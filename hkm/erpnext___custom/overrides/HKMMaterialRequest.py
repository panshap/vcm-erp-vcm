import frappe
from frappe import _

from erpnext.stock.doctype.material_request.material_request import MaterialRequest
from hkm.erpnext___custom.overrides.buying_validations import (
    check_items_are_not_from_template,
    validate_work_order_item,
)


class HKMMaterialRequest(MaterialRequest):
    def __init__(self, *args, **kwargs):
        super(HKMMaterialRequest, self).__init__(*args, **kwargs)

    def before_save(self):
        super().before_save()
        prefix = ""
        wo = self.for_a_work_order
        if self.material_request_type == "Purchase" and wo == 1:
            prefix = "Work Request"
        elif self.material_request_type == "Purchase":
            prefix = "Purchase"
        elif self.material_request_type == "Material Issue":
            prefix = "Material Issue"
        elif self.material_request_type == "Material Transfer":
            prefix = "Material Transfer"
        else:
            prefix = "MRN"
        item_names = []
        for item in self.items:
            item_names.append(item.item_name)
        item_names = ",".join(item_names)
        item_names = (
            item_names[0:39] + "..." if len(item_names) > 40 else item_names[0:39]
        )

        self.title = prefix + " for " + item_names

    def validate(self):
        super().validate()
        check_items_are_not_from_template(self)
        validate_work_order_item(self)
        self.validate_purchase_item()
        self.validate_asset_item()
        self.validate_work_head()
        return

    def validate_work_head(self):
        if self.work_head:
            work_request_head_doc = frappe.get_doc("Work Request Head", self.work_head)
            if work_request_head_doc.status == "Completed":
                frappe.throw(
                    "Work Request is not allowed in this Work Request Head as it is COMPLETED."
                )
        return

    def validate_asset_item(self):
        if not self.material_request_type == "Material Issue":
            return
        invalid_items = []
        asset_items = frappe.get_list(
            "Item", pluck="name", filters={"disabled": 0, "is_fixed_asset": 1}
        )
        for d in self.get("items"):
            if d.item_code in asset_items:
                invalid_items.append(d)
        for d in invalid_items:
            frappe.throw(
                _(
                    "Row#{0}: Asset Item {1} is not allowed for MRN of Issue.<br> Please select a stock item."
                ).format(
                    d.idx,
                    frappe.bold(d.item_code),
                ),
                title=_("Invalid Item"),
            )
        return

    def validate_purchase_item(self):
        if not self.material_request_type == "Purchase":
            return

        if self.for_a_work_order:
            return

        purchase_for_stock = False

        # allowed_role = frappe.db.get_single_value('HKM ERPNext Settings', 'purchase_request_creator_for_stock')

        allowed_role = "Stock User"

        if allowed_role in frappe.get_roles(frappe.session.user):
            purchase_for_stock = True

        for d in self.get("items"):
            item = frappe.get_doc("Item", d.item_code)
            if item.is_stock_item and not purchase_for_stock:
                frappe.throw(
                    _(
                        "Row#{0}: {1} is a Stock Item. So you can't make a Purchase MRN for that. It should be routed through Store<br>It is allowed only for Role : {2}"
                    ).format(
                        d.idx,
                        frappe.bold(d.item_name),
                        frappe.bold(allowed_role),
                    ),
                    title=_("Not Allowed"),
                )
        return

    def on_cancel(self):
        super().on_cancel()
        self.notify_on_cancellation()

    def notify_on_cancellation(self):
        material_purchase_link = self.material_purchase_link
        if material_purchase_link:
            mrn_purchase = frappe.get_doc(self.doctype, material_purchase_link)
            message = """
					<h3>Hare Krishna,</h3>
					<p>The MRN below has been cancelled by the user.</p>
					<h3><span style="color: #000080;">MRN Details:</span></h3>
					<p>MRN Issue Link : {}</p>
					<p>MRN Purchase Link : {}</p>
					<p>Cancelled By : {}</p>
					""".format(
                frappe.utils.get_url_to_form(self.doctype, self.name),
                frappe.utils.get_url_to_form(self.doctype, material_purchase_link),
                frappe.session.user,
            )
            email_args = {
                "recipients": [mrn_purchase.owner, self.owner],
                "message": message,
                "subject": "Issue MRN :{} Cancelled".format(self.name),
                "reference_doctype": self.doctype,
                "reference_name": self.name,
                "reply_to": self.owner,
                "delayed": False,
                "sender": self.owner,
            }
            frappe.enqueue(
                method=frappe.sendmail,
                queue="short",
                timeout=300,
                is_async=True,
                **email_args
            )


# def is_eligible_mrn(mrn):
# 	if mrn.material_request_type == 'Material Issue':
# 		return True
# 	elif mrn.material_request_type == 'Purchase' and mrn.for_a_work_order == 1:
# 		return True
# 	else:
# 		return False

# # Exclusive for SYSP
# DEPARTMENTS_TO_BE_NOTIFIED = ['Maintenance - HKMJ','Civil Department - HKMJ', 'Annakoot-TSFJ']
# def notify_mrn(self,method):
# return # No More Required as asked by SYSP
# if self.department in DEPARTMENTS_TO_BE_NOTIFIED and is_eligible_mrn(self):
# 	item_string = ""
# 	for idx,item in enumerate(self.items):
# 			item_string = item_string+"""
# 										<tr style="height: 18px;">
# 										<td style="width: 6.50568%; height: 18px; text-align: center;"> {} </td>
# 										<td style="width: 45.7103%; height: 18px; text-align: center;"> {} </td>
# 										<td style="width: 7.21585%; height: 18px; text-align: center;"> {} </td>
# 										<td style="width: 12.1874%; height: 18px; text-align: center;"> {} </td>
# 										</tr>
# 									  """.format(idx+1,item.item_name,item.uom,item.qty)

# 	items_string = """
# 				<table style="border-collapse: collapse; width: 100%; height: 36px;" border="1">
# 				<tbody>
# 				<tr style="height: 18px;">
# 				<td style="width: 6.50568%; height: 18px; text-align: center;"><strong><span style="color: #800000;">S.No.</span></strong></td>
# 				<td style="width: 45.7103%; height: 18px; text-align: center;"><strong><span style="color: #800000;">Item Name</span></strong></td>
# 				<td style="width: 7.21585%; height: 18px; text-align: center;"><strong><span style="color: #800000;">UOM</span></strong></td>
# 				<td style="width: 12.1874%; height: 18px; text-align: center;"><strong><span style="color: #800000;">Quantity</span></strong></td>
# 				</tr>
# 				{}
# 				</tbody>
# 				</table>
# 			   """.format(item_string)
# 	message = """
# 			<h3>Hare Krishna,</h3>
# 			<p>The MRN has been submitted just now.</p>
# 			<h3><span style="color: #000080;">MRN Details:</span></h3>
# 			<p>Department : {}</p>
# 			<p>MRN Link : {}</p>
# 			<p>Submitted By : {}</p>
# 			<hr>
# 			<p>Purpose : {}</p>
# 			<h3><span style="color: #000080;">Item Details:</span></h3>
# 			{}
# 			""".format(
# 				self.department,
# 				frappe.utils.get_url_to_form(self.doctype, self.name),
# 				#frappe.utils.get_url_to_form(self.doctype, material_purchase_link),
# 				frappe.session.user,
# 				self.purpose,
# 				items_string
# 				)
# 	email_args = {
# 		"recipients": ['sysd@hkm-group.org'],
# 		"message": message,
# 		"subject": 'MRN :{} Created'.format(self.name),
# 		"reference_doctype": self.doctype,
# 		"reference_name": self.name,
# 		"reply_to": frappe.session.user,
# 		"delayed":False,
# 		"sender":frappe.session.user
# 		}
# 	frappe.enqueue(method=frappe.sendmail, queue='short', timeout=300, is_async=True, **email_args)
# return
