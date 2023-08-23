# -*- coding: utf-8 -*-
# Copyright (c) 2021, NRHD and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.website.website_generator import WebsiteGenerator

class FOLKStudent(WebsiteGenerator):
	
	def validate(self):
		if not self.folk_resident:
			self.residency = None
			self.since = None
