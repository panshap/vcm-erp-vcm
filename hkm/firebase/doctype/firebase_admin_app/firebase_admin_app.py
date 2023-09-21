# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
import firebase_admin
from frappe.model.document import Document


class FirebaseAdminApp(Document):
    @property
    def instance(self):
        if self.name not in firebase_admin._apps:
            cred = firebase_admin.credentials.Certificate(frappe.get_site_path() + self.private_key_file)
            firebase_admin.initialize_app(cred, name=self.name)
        return firebase_admin._apps.get(self.name)
