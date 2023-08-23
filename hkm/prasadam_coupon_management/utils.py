import frappe


def current_coupon_credits(user,date,slot,coupon_type):
	credits = 0
	requests = frappe.get_all("Prasadam CPN Request", 
							filters = {'docstatus': 1,'authority':user, 'date':date, 'slot':slot, 'coupon_type':coupon_type}, 
							fields=['type','number'])
	
	for request in requests:
		if request['type'] == "Request":
			credits += request['number']
		if request['type'] in ["Release" , "Transfer"]:
			credits -= request['number']

	# Coupons already generated
	generated = frappe.get_all("Prasadam Coupon", 
							filters = {'authority':user, 'date':date, 'slot':slot,'coupon_type':coupon_type}, 
							fields=['number'])

	for gen in generated:
		credits -= gen['number']

	#Transferred
	transferred = frappe.get_all("Prasadam CPN Request", 
							filters = {'docstatus': 1,'transfer_to':user, 'date':date, 'slot':slot, 'coupon_type':coupon_type}, 
							fields=['number'])
	for transfer in transferred:
		credits += transfer['number']
	
	# #Received
	# received = frappe.get_all("Prasadam CPN Request", 
	# 						filters = {'docstatus': 1,'transfer_to':user, 'date':date, 'slot':slot, 'coupon_type':coupon_type}, 
	# 						fields=['number'])
	# for transfer in transferred:
	# 	credits += transfer['number']

	return credits

def get_allowed_time(slot):
	timings = frappe.cache().hget("prasadam_timings", slot) or frappe._dict()
	if not timings:
		doc = frappe.get_cached_doc('Prasadam Coupon Settings')
		for d in doc.get("slots"):
			if d.slot == slot:
				timings.setdefault(slot,frappe._dict(
					Request = d.request,
					Release = d.release,
					Transfer = d.transfer
				))
				frappe.cache().hset("prasadam_timings", slot, timings)
				break
	return timings