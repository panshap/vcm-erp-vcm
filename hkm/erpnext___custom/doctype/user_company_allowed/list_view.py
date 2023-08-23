import frappe

def get_applicable_documents():
	
	doctypes = frappe.db.get_all('Custom DocPerm', pluck='parent',group_by = 'parent')
	
	sel_doctypes = []
	for dt in doctypes:
		if frappe.db.exists('DocType', dt) and frappe.get_meta(dt).has_field('company'):
			sel_doctypes.append(dt)
	return sel_doctypes


def query(user):
	if not user:
		user = frappe.session.user
		
	user_company_allowed = frappe.db.get_all('User Company Allowed',pluck='company',filters={'user':user})

	if len(user_company_allowed)>0:
		filter_strings =[]
		for company in user_company_allowed:
			filter_strings.append("company = '{}'".format(company))
		return "("+ (" or ".join(filter_strings)) + ")"
	else:
		return "( 1 )"

def company_specific(user):
	if not user:
		user = frappe.session.user
		
	user_company_allowed = frappe.db.get_all('User Company Allowed',pluck='company',filters={'user':user})
	if len(user_company_allowed)>0:
		filter_strings =[]
		for company in user_company_allowed:
			filter_strings.append("name = '{}'".format(company))
		return "("+ (" or ".join(filter_strings)) + ")"
	else:
		return "( 1 )"