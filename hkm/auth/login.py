from traceback import FrameSummary
import frappe
from frappe import auth
import requests

@frappe.whitelist( allow_guest=True )
def login(usr, pwd):
    # try:
    #     login_manager = frappe.auth.LoginManager()
    #     login_manager.authenticate(user=usr, pwd=pwd)
    #     login_manager.post_login()
    # except frappe.exceptions.AuthenticationError:
    #     # frappe.clear_messages()
    #     # frappe.local.response["message"] = {
    #     #     "success_key":0,
    #     #     "message":"Authentication Error!"
    #     # }
    #     return
    login_manager = frappe.auth.LoginManager()
    login_manager.authenticate(user=usr, pwd=pwd)
    login_manager.post_login()
    token_string =""
    user = frappe.get_doc('User', frappe.session.user)
    token = frappe.db.sql(""" 
                        SELECT user,token FROM `tabUser Token` WHERE user = '{}'
                        """.format(frappe.session.user),as_dict=1)
    if len(token) == 0:
        token_string = get_and_save_token(user)
    else:
        token_string = token[0]['token']
        if not valid_token(token_string):
            token_string = update_token(user)

    
    roles = frappe.get_roles(frappe.session.user)
    return {
        "success_key":1,
        "message":"Authentication success",
        # "sid":frappe.session.sid,
        "token":token_string,
        "full_name":user.full_name,
        "email":user.email,
        "roles":roles
    }

def get_and_save_token(user):
    api_secret = generate_keys(user)
    api_key = user.api_key
    token = "token {}:{}".format(api_key,api_secret)
    user_token = frappe.get_doc({"doctype":"User Token","user":user.name, "token": token})
    user_token.insert(ignore_permissions = True)
    return token

def update_token(user):
    api_secret = generate_keys(user)
    api_key = user.api_key
    token = "token {}:{}".format(api_key,api_secret)
    user_token_doc = frappe.get_doc('User Token', user.name)
    user_token_doc.token = token
    user_token_doc.save(ignore_permissions=True)
    return token

def generate_keys(user):
    user_details = user
    api_secret = frappe.generate_hash(length=15)

    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key

    user_details.api_secret = api_secret
    user_details.save(ignore_permissions=True)
    return api_secret


@frappe.whitelist()
def isLoggedIn():
    return True


def valid_token(token):
    url = "http://hkmjerp.in/api/method/frappe.auth.get_logged_user"
    headers = {
    'Authorization': token,
    }
    response = requests.request("GET", url, headers=headers)

    if response.status_code == 200:
        return True
    return False