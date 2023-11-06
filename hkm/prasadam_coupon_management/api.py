import frappe
from frappe.utils import getdate
from frappe.utils import today
from hkm.prasadam_coupon_management.utils import current_coupon_credits

@frappe.whitelist()
def get_coupon_stats(date,slot):

	coupon_types = ["Silver", "Gold"]

	silver_coupons = get_coupon_type_wise_stats(date,slot,"Silver")
	gold_coupons = get_coupon_type_wise_stats(date,slot,"Gold")

	unique_users = []
	for silver in silver_coupons:
		if silver not in unique_users:
			unique_users.append(silver)
	for gold in gold_coupons:
		if gold not in unique_users:
			unique_users.append(gold)

	response = []
	for user in unique_users:
		user_details = frappe.get_doc("User",user)
		username = user_details.full_name
		
		gold = silver = frappe._dict(
					request = 0,
					release = 0,
					transfer_sent = 0,
					transfer_rec = 0,
					generated = 0,
					credit = 0,
					used =0
				)
		if user in silver_coupons:
			silver = silver_coupons[user]
		
		if user in gold_coupons:
			gold = gold_coupons[user]

		data = frappe._dict(
					username = username,
					user = user,
					gold = gold,
					silver = silver
				)
		response.append(data)

	return response

def get_coupon_type_wise_stats(date,slot,coupon_type):
	#requests = frappe.get_list("Prasadam CPN Request",filters= {'docstatus': 1, 'date':date, 'slot':slot}, fields =['transfer_to','authority','type','number'])
	requests = frappe.db.sql("""
							select transfer_to, authority, type, number
							from `tabPrasadam CPN Request`
							where docstatus = 1 and date = '{}' and slot ='{}' and coupon_type = '{}'
								""".format(date,slot,coupon_type), as_dict = 1)				
	users = {}
	for request in requests:
		if request['authority'] not in users:
			users.setdefault(request['authority'], frappe._dict(
					request = 0,
					release = 0,
					transfer_sent = 0,
					transfer_rec = 0,
					generated = 0,
					credit = 0,
					used =0
				))
		if request['transfer_to'] is not None and request['transfer_to'] not in users:
			users.setdefault(request['transfer_to'], frappe._dict(
					request = 0,
					release = 0,
					transfer_sent = 0,
					transfer_rec = 0,
					generated = 0,
					credit = 0,
					used =0
				))
		if request['type'] == "Request":
			users[request['authority']]['request']+= request['number']
		if request['type'] == "Release":
			users[request['authority']]['release']+= request['number']
		if request['type'] == "Transfer":
			users[request['authority']]['transfer_sent']+= request['number']
			users[request['transfer_to']]['transfer_rec']+= request['number']

	# return users,transfers,checks
	# generates = frappe.get_list("Prasadam Coupon", 
	# 						filters = {'date':date, 'slot':slot}, 
	# 						fields=['authority','number'])

	generates = frappe.db.sql("""
							select authority, number
							from `tabPrasadam Coupon`
							where date = '{}' and slot ='{}' and docstatus = 1 and coupon_type = '{}'
								""".format(date,slot,coupon_type), as_dict = 1)
	used = frappe.db.sql("""
							select authority, number
							from `tabPrasadam Coupon`
							where date = '{}' and slot ='{}' and used = 1 and docstatus = 1 and coupon_type = '{}'
								""".format(date,slot,coupon_type), as_dict = 1)

	for generate in generates:
		users[generate['authority']]['generated'] += generate['number']
		
	for u in used:
		users[u['authority']]['used'] += u['number']
		
	response = []
	for user in users:
		# user_details = frappe.get_doc("User",user)
		
		users[user]['credit'] = current_coupon_credits(user,date,slot,coupon_type)
		# users[user]['username'] = user_details.full_name
		# response.append(users[user])

	return users


@frappe.whitelist()
def get_dashboard_data():
	silver	= get_dashboard_data_coupon_wise("Silver")
	gold  	= get_dashboard_data_coupon_wise("Gold")

	# return silver
	# return silver
	response = []

	for slot in ["Morning", "Afternoon", "Evening"]:
		response.append(frappe._dict(
							slot = slot,
							gold  = gold[slot],
							silver = silver[slot]
							))

	return response

def get_dashboard_data_coupon_wise(coupon_type):
	user = frappe.session.user
	date = today()
	#date = "2022-05-27"
	requests = frappe.db.sql("""
							select transfer_to, authority, type, number, slot
							from `tabPrasadam CPN Request`
							where docstatus = 1 and date = '{}' and authority ='{}' and coupon_type = '{}'
								""".format(date,user,coupon_type), as_dict = 1)
	slots = {}
	for s in ["Morning","Afternoon","Evening"]:
		slots.setdefault(s, frappe._dict(
					request = 0,
					release = 0,
					transfer_sent = 0,
					transfer_rec = 0,
					generated = 0,
					credit = 0,
					used = 0
				))
	
	for request in requests:
		if request['type'] == "Request":
			slots[request['slot']]['request']+= request['number']
		if request['type'] == "Release":
			slots[request['slot']]['release']+= request['number']
		if request['type'] == "Transfer":
			slots[request['slot']]['transfer_sent']+= request['number']


	transferred_rec = frappe.db.sql("""
							select transfer_to, authority, type, number, slot
							from `tabPrasadam CPN Request`
							where docstatus = 1 and date = '{}' and transfer_to ='{}' and coupon_type = '{}'
								""".format(date,user,coupon_type), as_dict = 1)
	for t in transferred_rec:
		slots[t['slot']]['transfer_rec']+= t['number']
			# users[request['authority']]['transfer_sent']+= request['number']
			# users[request['transfer_to']]['transfer_rec']+= request['number']

	# return users,transfers,checks
	generates = frappe.db.sql("""
							select authority, number, slot, used
							from `tabPrasadam Coupon`
							where date = '{}' and authority ='{}' and docstatus = 1 and coupon_type = '{}'
								""".format(date,user,coupon_type), as_dict = 1)

	for generate in generates:
		slots[generate['slot']]['generated'] += generate['number']
		if generate['used']:
			slots[generate['slot']]['used'] += generate['number']


	# response = []
	for s in slots:
		slots[s]['credit'] = current_coupon_credits(user,date,s,coupon_type)
		# response.append(slots[s])

	return slots

@frappe.whitelist()
def fetch_request_users():
	purchase_request_role = 'Prasadam Request User'
	users = frappe.db.sql("""
							select user.full_name,user.name
							from `tabUser` user
							join `tabHas Role` has_role on has_role.parent = user.name
							join `tabRole` role on has_role.role  = role.name
							where role.name = '{}' and user.name != '{}'
							order by user.full_name
								""".format(purchase_request_role,frappe.session.user), as_dict = 1)	
	return users
	

@frappe.whitelist()
def get_coupons_of_user(date):
	coupons = frappe.get_list("Prasadam Coupon",fields=["name","date","coupon_type","slot","number","qr_code","creation"], filters = {"used":0,"docstatus" : 1,"date":date,"authority":frappe.session.user})
	return coupons

# @frappe.whitelist()
# def get_coupon_details(coupon):
# 	coupons = frappe.
# 	return coupons

@frappe.whitelist()
def confirmCouponUsed(coupon):
	doc = frappe.get_doc("Prasadam Coupon", coupon)
	if doc.used == 1:
		frappe.throw("This coupon is Already used.")
	else:
		doc.used = 1
		doc.save()
	return doc
