import frappe
from mimetypes import guess_type
from frappe import _, is_whitelisted
from frappe.utils import cint

@frappe.whitelist(allow_guest=True)
def upload_file():
	user = None
	if frappe.session.user == 'Guest':
		if frappe.get_system_settings('allow_guests_to_upload_files'):
			ignore_permissions = True
		else:
			return
	else:
		user = frappe.get_doc("User", frappe.session.user)
		ignore_permissions = False

	files = frappe.request.files
	is_private = frappe.form_dict.is_private
	doctype = frappe.form_dict.doctype
	docname = frappe.form_dict.docname
	fieldname = frappe.form_dict.fieldname
	file_url = frappe.form_dict.file_url
	folder = frappe.form_dict.folder or 'Home'
	method = frappe.form_dict.method
	content = None
	filename = None

	if 'file' in files:
		file = files['file']
		content = file.stream.read()
		filename = file.filename

	frappe.local.uploaded_file = content
	frappe.local.uploaded_filename = filename

	if frappe.session.user == 'Guest' or (user and not user.has_desk_access()):
		import mimetypes
		filetype = mimetypes.guess_type(filename)[0]
		if filetype not in ALLOWED_MIMETYPES:
			frappe.throw(_("You can only upload JPG, PNG, PDF, or Microsoft documents."))

	if method:
		method = frappe.get_attr(method)
		is_whitelisted(method)
		return method()
	else:
		ret = frappe.get_doc({
			"doctype": "File",
			"attached_to_doctype": doctype,
			"attached_to_name": docname,
			"attached_to_field": fieldname,
			"folder": folder,
			"file_name": filename,
			"file_url": '/files/{}'.format(filename),
			"is_private": cint(is_private),
			"content": content
		})
		ret.save(ignore_permissions=ignore_permissions)
		std = frappe.get_doc('FOLK Student',docname)
		std.image = ret.file_url
		std.save(ignore_permissions=ignore_permissions)
		frappe.db.commit()
		return file_url
		# frappe.db.set_value('FOLK Student', docname, 'image', file_url)
		# # frappe.db.commit()
		# return ret
