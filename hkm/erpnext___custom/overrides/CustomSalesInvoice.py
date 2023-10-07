import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from frappe.utils.data import getdate
from frappe.model.naming import getseries

## Below extension is just to include autoname , Validations are in different file in same folder


class CustomSalesInvoice(SalesInvoice):
    def autoname(self):
        # select a project name based on customer
        dateF = getdate(self.posting_date)
        company = self.company_abbreviation
        year = dateF.strftime("%y")
        month = dateF.strftime("%m")
        prefix = f"{company}-{year}-{month}-"
        frappe.errprint(prefix)
        self.name = prefix + getseries(prefix, 4)
