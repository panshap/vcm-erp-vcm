import frappe
from frappe import _

def validate(self, method=None):
	validate_word_order(self)

def validate_word_order(self):
	linked_purchase_orders = [d.purchase_order for d in self.get("items")]
	linked_purchase_orders = list(set(linked_purchase_orders))
	for po in linked_purchase_orders:
		work_order = frappe.db.get_value('Purchase Order', po, 'for_a_work_order')
		if work_order == 1:
			frappe.throw(
				_('Work Order {0} isn\'t allowed to have a Purchase Receipt.' )
				.format(
					frappe.bold(po),
				), 
				title=_("Not Allowed")
			)
	return