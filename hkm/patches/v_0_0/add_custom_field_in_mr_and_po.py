# Copyright (c) 2022, HKM
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	add_custom_field_in_material_request()
	add_custom_field_in_purchase_order()

def add_custom_field_in_material_request():
	custom_fields = {
		'Material Request' : [
			dict(fieldname='boq', label='BOQ', fieldtype='Link', options="BOQ",
				insert_after='job_card', translatable=0, read_only=1
			),			
		],
		'Material Request Item' : [
			dict(fieldname='boq', label='BOQ', fieldtype='Link', options="BOQ",
				insert_after='expense_account', translatable=0, read_only=1
			),	
			dict(fieldname='boq_item', label='BOQ Item', fieldtype='Data', 
				insert_after='boq', translatable=0, read_only=1
			),								
		],		
	}
	create_custom_fields(custom_fields)

def add_custom_field_in_purchase_order():
	custom_fields = {
		'Purchase Order' : [
			dict(fieldname='for_a_work_order', label='For A Work Order', fieldtype='Check', 
				insert_after='type', translatable=0, read_only=1
			),			
		],
	}
	if not frappe.db.exists('Custom Field', {"dt": 'Purchase Order', "fieldname":'for_a_work_order'}):
		create_custom_fields(custom_fields)
