import frappe


def user_wallet_balance(user):
    if user is None:
        user = frappe.session.user

    txs = frappe.get_all("DD Wallet Tx", fields=["final_balance"], order_by="creation desc", filters={"user": user})
    if len(txs) == 0:
        return 0
    return txs[0].final_balance
