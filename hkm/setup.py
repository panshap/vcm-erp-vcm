import frappe, click
from frappe.desk.page.setup_wizard.setup_wizard import make_records
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_install():
	click.secho("Installing Custom Records", fg="yellow")
	make_custom_records()
	click.secho("Installing Custom Fields", fg="yellow")
	make_custom_fields()
	frappe.clear_cache()

def make_custom_records():
	records = [
		{'doctype': "Party Type", "party_type": "Donor", "account_type": "Receivable"},
	]
	make_records(records)

def make_custom_fields(update=True):
	custom_fields = get_custom_fields()
	create_custom_fields(custom_fields, update=update)

def get_custom_fields():
	custom_fields = {
		'Company': [
			dict(fieldname='dhananjaya_section', label='Dhananjaya Settings',
				 fieldtype='Section Break', insert_after='asset_received_but_not_billed', collapsible=1),
			dict(fieldname='80g_number', label='80G Number',
				 fieldtype='Data', insert_after='dhananjaya_section'),
			dict(fieldname='pan_number', label='PAN Number',
				 fieldtype='Data', insert_after='80g_number')
		]
	}
	return custom_fields