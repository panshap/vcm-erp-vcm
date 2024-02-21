# Copyright (c) 2024, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe,json,requests
from frappe.model.document import Document

class WhatsAppSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		token: DF.Password | None
		url: DF.Data | None
	# end: auto-generated types
	pass

def send_whatsapp_using_template(mobile, template_name,parameters):
	mobile = mobile.strip()[-10:]
	settings = frappe.get_single("WhatsApp Settings")
	payload = json.dumps({
	"messaging_product": "whatsapp",
	"recipient_type": "individual",
	"to": f"+91{mobile}",
	"type": "template",
	"template":{
		"name":template_name,
		"language":{
			"code":"en"
		},
		"components":[
			{
				"type":"body",
				"parameters":parameters
			}
		]
	}
	})
	headers = {
	'Content-Type': 'application/json',
	'Authorization': f'Bearer {settings.get_password("token")}'
	}

	response = requests.request("POST", settings.url, headers=headers, data=payload)

	return response.text
