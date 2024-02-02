import frappe
from frappe.contacts.doctype.address.address import get_address_display
from frappe.utils import time_diff_in_hours, time_diff_in_seconds, date_diff, flt
from frappe.model.workflow import apply_workflow
from frappe.utils.background_jobs import enqueue

system_admin = "nrhd@hkm-group.org"


def fetch_address_from_creation_request(self, method):
    if self.flags.is_new_doc and self.get("supplier_creation_request"):
        address = frappe.get_doc(
            "Supplier Creation Request", self.get("supplier_creation_request")
        )
        self.address_line1 = address.address_line_1
        self.address_line2 = address.address_line_2
        self.pincode = address.pincode
        self.city = address.city
        self.state = address.state
        self.country = address.country
        self.gstin = address.gstin
        self.phone = address.mobile_number
        if not (self.gstin is None or self.gstin == ""):
            self.gst_category = "Registered Regular"
        elif self.country != "India":
            self.gst_category = "Overseas"
        else:
            self.gst_category = "Unregistered"

        address = make_address(self)
        address_display = get_address_display(address.name)

        self.db_set("supplier_primary_address", address.name)
        self.db_set("primary_address", address_display)

        # Notify Requestor
        sc_request = frappe.get_doc(
            "Supplier Creation Request", self.get("supplier_creation_request")
        )

        message = success_mail(self, sc_request)
        email_args = {
            "recipients": [sc_request.owner],
            "message": message,
            "subject": "Item {} Created".format(sc_request.supplier_name),
            # "attachments": [frappe.attach_print(doc.doctype, doc.name, file_name=doc.name)],
            "reference_doctype": self.doctype,
            "reference_name": self.name,
            "reply_to": self.owner if self.owner != "Administrator" else system_admin,
            "delayed": False,
            "sender": self.owner,
        }
        enqueue(
            method=frappe.sendmail,
            queue="short",
            timeout=300,
            is_async=True,
            **email_args
        )

        apply_workflow(sc_request, "Confirm as Done")
        frappe.db.commit()

    return


def make_address(args, is_primary_address=1):
    reqd_fields = []
    for field in ["city", "country"]:
        if not args.get(field):
            reqd_fields.append("<li>" + field.title() + "</li>")

    if reqd_fields:
        msg = _("Following fields are mandatory to create address:")
        frappe.throw(
            "{0} <br><br> <ul>{1}</ul>".format(msg, "\n".join(reqd_fields)),
            title=_("Missing Values Required"),
        )

    address = frappe.get_doc(
        {
            "doctype": "Address",
            "address_title": args.get("name"),
            "address_line1": args.get("address_line1"),
            "address_line2": args.get("address_line2"),
            "city": args.get("city"),
            "state": args.get("state"),
            "pincode": args.get("pincode"),
            "country": args.get("country"),
            "gst_category": args.get("gst_category"),
            "gstin": args.get("gstin"),
            "phone": args.get("phone"),
            "links": [
                {"link_doctype": args.get("doctype"), "link_name": args.get("name")}
            ],
        }
    ).insert()

    return address


def success_mail(supplier, sc_request):
    time_taken, postfix = (
        time_diff_in_hours(supplier.creation, sc_request.creation),
        "hours",
    )
    if time_taken < 1:
        time_taken, postfix = (
            time_diff_in_seconds(supplier.creation, sc_request.creation) / 60,
            "minutes",
        )
    elif time_taken > 23:
        time_taken, postfix = date_diff(supplier.creation, sc_request.creation), "days"
    time_taken = flt(time_taken, 2)
    message = """
				<p>Hare Krishna,</p>
				<p>We have created an Supplier as requested by you. Please check the details.</p>
				<p>&nbsp;</p>
				<p><strong>Supplier Name : {}</strong></p>
				<p><strong>Link to Supplier for more details : {}</strong></p>
				<p>&nbsp;</p>
				<p><em>We have created this within <strong>{} {}</strong>, you raised the request.</em></p>
				Please contact <strong>{}</strong> for any issues.
				<p>&nbsp;</p>
				<p>Thanks,</p>
				<p>ERP Team</p>
				""".format(
        supplier.supplier_name,
        frappe.utils.get_url_to_form("Supplier", supplier.name),
        time_taken,
        postfix,
        supplier.owner,
    )
    return message


item_supplier_admin = "Item Manager"


def creation_from_gstin(self, method):
    if (
        self.is_new()
        and not self.get("gstin")
        and not item_supplier_admin in frappe.get_roles(frappe.session.user)
    ):
        frappe.throw(
            "You are not allowed to create a Supplier without GSTIN. Raise through Supplier Creation Request."
        )
    return
