import frappe
from datetime import datetime, timedelta

from hkm.divine_dishes.utils import user_wallet_balance


def every_day_evening():
    create_subscription_orders()


def create_subscription_orders():
    tomorrow_weekday = (datetime.now() + timedelta(days=1)).strftime("%A")

    subscriptions = frappe.get_all("DD Subscription", filters={"running": 1}, pluck="name")

    users = {}

    for s in subscriptions:
        subscription_doc = frappe.get_doc("DD Subscription", s)
        for schd in subscription_doc.schedule:
            if schd.week_day == tomorrow_weekday:
                if subscription_doc.user not in users:
                    users.setdefault(subscription_doc.user, [])
                schd_order_item = frappe._dict(website_item=subscription_doc.website_item, qty=schd.qty)
                users[subscription_doc.user].append(schd_order_item)

    for u in users:
        check_order(u, users[u])


def check_order(user, orders):
    settings = frappe.get_cached_doc("E Commerce Settings")
    total_amount = 0
    for order in orders:
        web_item_doc = frappe.get_cached_doc("Website Item", order["website_item"])
        prices = frappe.get_all(
            "Item Price",
            fields=["price_list_rate"],
            filters={"price_list": settings.price_list, "item_code": web_item_doc.item_code},
        )
        if len(prices) > 0:
            rate = prices[0].price_list_rate
            amount = rate * order["qty"]
            total_amount += amount
        else:
            frappe.throw(f"Rate of Item {order['website_item']} is not set.")
    if user_wallet_balance(user) >= total_amount:
        if process_order(user, orders):
            make_wallet_tx(user, total_amount)
            frappe.db.commit()
    else:
        pass  # Notify user that it couldn't processed due to insufficeient balance in wallet


def process_order(user, orders) -> bool:
    try:
        doc = frappe.get_doc(
            {
                "doctype": "DD Order",
                "user": user,
                "status": "Paid",
                "items": orders,
                "auto_generated": 1,
            }
        )
        doc.insert()
        return True
    except:
        return False


def make_wallet_tx(user, amount):
    doc = frappe.get_doc(
        {"doctype": "DD Wallet Tx", "withdrawl": amount, "user": user, "remarks": "Deducted to pay for Subscription."}
    )
    doc.insert()
