# Copyright (c) 2023, Narahari Dasa and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from firebase_admin import messaging
from datetime import timedelta


class AppNotification(Document):
    def after_insert(self):
        if self.notify:
            self.send_app_notification()

    def send_app_notification(self):
        tokens = frappe.db.get_list(
            "Firebase App Token",
            pluck="token",
            filters={"user": self.user},
        )
        if len(tokens) > 0:
            # See documentation on defining a message payload.
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=self.subject,
                    body=self.message,
                ),
                data={"is_route": str(self.is_route), "screen": self.route},
                tokens=tokens,
                android=messaging.AndroidConfig(
                    ttl=timedelta(seconds=3600),
                    priority="normal",
                    notification=messaging.AndroidNotification(icon="stock_ticker_update", color="#f45342"),
                ),
            )
            fa_doc = frappe.get_doc("Firebase Admin App", self.app)
            response = messaging.send_multicast(message, app=fa_doc.instance)
            return response
