CUSTOM_FIELDS = {
  "Journal Entry": [
    {
      "DocType": "Journal Entry",
      "Field Type": "Data",
      "Label": "Bank Statement Name",
      "Fieldname": "bank_statement_name",
      "Insert After": "donation_receipt",
      "Read Only": 1,
      "Hidden": 1,
      "Translatable": 1
    },
    {
      "DocType": "Journal Entry",
      "Field Type": "Link",
      "Label": "Donation Receipt",
      "Fieldname": "donation_receipt",
      "Insert After": "tax_withholding_category",
      "Options": "Donation Receipt"
    }
  ],
  "Purchase Invoice": [
    {
      "DocType": "Purchase Invoice",
      "Field Type": "Link",
      "Label": "Default Difference Account",
      "Fieldname": "default_difference_account",
      "Insert After": "sec_warehouse",
      "Options": "Account"
    },
    {
      "DocType": "Purchase Invoice",
      "Field Type": "Link",
      "Label": "Department",
      "Fieldname": "department",
      "Insert After": "amended_from",
      "Options": "Department",
      "Read Only": 1,
      "In Standard Filter": 1
    }
  ],
  "Material Request Item": [
    {
      "DocType": "Material Request Item",
      "Field Type": "Data",
      "Label": "Item Type",
      "Fieldname": "item_type",
      "Insert After": "item_name",
      "Read Only": 1,
      "In List View": 1,
      "Translatable": 1
    },
    {
      "DocType": "Material Request Item",
      "Field Type": "Data",
      "Label": "Item Description",
      "Fieldname": "item_description",
      "Insert After": "section_break_4",
      "Length": 256,
      "Translatable": 1
    }
  ],
  "Purchase Order Item": {
    "DocType": "Purchase Order Item",
    "Field Type": "Data",
    "Label": "Item Type",
    "Fieldname": "item_type",
    "Insert After": "item_name",
    "Read Only": 1,
    "In List View": 1,
    "Translatable": 1
  },
  "Item Tax Template": {
    "DocType": "Item Tax Template",
    "Field Type": "Int",
    "Label": "Cumulative Tax",
    "Fieldname": "cumulative_tax",
    "Insert After": "disabled",
    "Non Negative": 1
  },
  "Item": [
    {
      "DocType": "Item",
      "Field Type": "Link",
      "Label": "Item Creation Request",
      "Fieldname": "item_creation_request",
      "Insert After": "total_projected_qty",
      "Options": "Item Creation Request",
      "Read Only": 1
    },
    {
      "DocType": "Item",
      "Field Type": "Data",
      "Label": "Selling Rate with GST",
      "Fieldname": "selling_rate_with_gst",
      "Insert After": "standard_rate",
      "Read Only": 1,
      "Translatable": 1
    }
  ],
  "Item Creation Request": {
    "DocType": "Item Creation Request",
    "Field Type": "Link",
    "Label": "Workflow State",
    "Fieldname": "workflow_state",
    "Options": "Workflow State",
    "Hidden": 1,
    "No Copy": 1,
    "Allow on Submit": 1
  },
  "Supplier Creation Request": {
    "DocType": "Supplier Creation Request",
    "Field Type": "Link",
    "Label": "Workflow State",
    "Fieldname": "workflow_state",
    "Options": "Workflow State",
    "Hidden": 1,
    "No Copy": 1,
    "Allow on Submit": 1
  },
  "Donation Receipt": {
    "DocType": "Donation Receipt",
    "Field Type": "Link",
    "Label": "Workflow State",
    "Fieldname": "workflow_state",
    "Options": "Workflow State",
    "Hidden": 1,
    "No Copy": 1,
    "Allow on Submit": 1
  },
  "Task": [
    {
      "DocType": "Task",
      "Field Type": "Data",
      "Label": "Location",
      "Fieldname": "location",
      "Insert After": "completed_by",
      "In List View": 1,
      "In Standard Filter": 1,
      "Translatable": 1
    },
    {
      "DocType": "Task",
      "Field Type": "Select",
      "Label": "workflow_state",
      "Fieldname": "workflow_state",
      "Insert After": "project",
      "Options": "Draft\nAcknowledged\nCompleted\nUser Confirmed",
      "Hidden": 1,
      "In Standard Filter": 1,
      "Translatable": 1
    },
    {
      "DocType": "Task",
      "Field Type": "Data",
      "Label": "Contact Mobile No",
      "Fieldname": "contact_mobile_no",
      "Insert After": "contact_person",
      "Translatable": 1
    },
    {
      "DocType": "Task",
      "Field Type": "Data",
      "Label": "Contact Person",
      "Fieldname": "contact_person",
      "Insert After": "subject",
      "Translatable": 1
    },
    {
      "DocType": "Task",
      "Field Type": "Select",
      "Label": "To Department",
      "Fieldname": "to_department",
      "Options": "Maintenance\nIT",
      "In Standard Filter": 1,
      "Translatable": 1
    }
  ],
  "Stock Entry": {
    "DocType": "Stock Entry",
    "Field Type": "Link",
    "Label": "Default Difference Account",
    "Fieldname": "default_difference_account",
    "Insert After": "source_address_display",
    "Options": "Account",
    "Mandatory Depends On": "eval:doc.purpose=='Material Issue' || doc.purpose=='Material Receipt'"
  },
  "Purchase Receipt": {
    "DocType": "Purchase Receipt",
    "Field Type": "Link",
    "Label": "Department",
    "Fieldname": "department",
    "Insert After": "is_return",
    "Options": "Department",
    "Read Only": 1
  },
  "Purchase Order": [
    {
      "DocType": "Purchase Order",
      "Field Type": "Long Text",
      "Label": "Extra Description",
      "Fieldname": "extra_description",
      "Insert After": "items"
    },
    {
      "DocType": "Purchase Order",
      "Field Type": "Attach",
      "Label": "Comparison Sheet",
      "Fieldname": "comparison_sheet",
      "Insert After": "department",
      "Allow in Quick Entry": 1
    },
    {
      "DocType": "Purchase Order",
      "Field Type": "Link",
      "Label": "Department",
      "Fieldname": "department",
      "Insert After": "company",
      "Options": "Department",
      "Fetch From": "material_request.department",
      "Is Mandatory Field": 1
    },
    {
      "DocType": "Purchase Order",
      "Field Type": "Data",
      "Label": "Final Approving Authority",
      "Fieldname": "final_approving_authority",
      "Insert After": "first_approving_authority",
      "Options": "Email",
      "Read Only": 1,
      "Translatable": 1
    },
    {
      "DocType": "Purchase Order",
      "Field Type": "Data",
      "Label": "First Approving Authority",
      "Fieldname": "first_approving_authority",
      "Insert After": "recommended_by",
      "Options": "Email",
      "Read Only": 1,
      "Translatable": 1
    },
    {
      "DocType": "Purchase Order",
      "Field Type": "Data",
      "Label": "Recommended By",
      "Fieldname": "recommended_by",
      "Insert After": "alm_column_break",
      "Options": "Email",
      "Read Only": 1,
      "Translatable": 1
    },
    {
      "DocType": "Purchase Order",
      "Field Type": "Column Break",
      "Fieldname": "alm_column_break",
      "Insert After": "checked_by"
    },
    {
      "DocType": "Purchase Order",
      "Field Type": "Data",
      "Label": "Checked By",
      "Fieldname": "checked_by",
      "Insert After": "prepared_by",
      "Options": "Email",
      "Read Only": 1,
      "Translatable": 1
    },
    {
      "DocType": "Purchase Order",
      "Field Type": "Data",
      "Label": "Prepared By",
      "Fieldname": "prepared_by",
      "Insert After": "alm",
      "Options": "Email",
      "Read Only": 1,
      "Translatable": 1
    },
    {
      "DocType": "Purchase Order",
      "Field Type": "Section Break",
      "Label": "ALM",
      "Fieldname": "alm",
      "Insert After": "schedule_date"
    },
    {
      "DocType": "Purchase Order",
      "Field Type": "Data",
      "Label": "One Time Vendor Address",
      "Fieldname": "one_time_vendor_address",
      "Insert After": "one_time_vendor_section",
      "Translatable": 1
    },
    {
      "DocType": "Purchase Order",
      "Field Type": "Section Break",
      "Label": "One Time Vendor Details",
      "Fieldname": "one_time_vendor_section",
      "Insert After": "type",
      "Depends On": "eval: doc.supplier == 'One time Vendor'"
    },
    {
      "DocType": "Purchase Order",
      "Field Type": "Select",
      "Label": "Type",
      "Fieldname": "type",
      "Insert After": "supplier",
      "Options": "REVEX\nCAPEX",
      "Is Mandatory Field": 1,
      "In Standard Filter": 1,
      "Translatable": 1,
      "Field Description": "Type of Expenditure.\nCAPEX is an amount spent to acquire or improve a long-term asset such as any electronics equipment.\nREVEX refers to expenses incurred in the course of ordinary business, such as sales, general and administrative expenses."
    },
    {
      "DocType": "Purchase Order",
      "Field Type": "Link",
      "Label": "Workflow State",
      "Fieldname": "workflow_state",
      "Options": "Workflow State",
      "Hidden": 1,
      "No Copy": 1,
      "Allow on Submit": 1,
      "In List View": 1,
      "In Standard Filter": 1
    }
  ],
  "POS Invoice": {
    "DocType": "POS Invoice",
    "Field Type": "Data",
    "Label": "Company Abbreviation",
    "Fieldname": "company_abbreviation",
    "Insert After": "against_income_account",
    "Fetch From": "company.abbr",
    "Hidden": 1,
    "Translatable": 1
  },
  "Material Request": [
    {
      "DocType": "Material Request",
      "Field Type": "Link",
      "Label": "Material Purchase Link",
      "Fieldname": "material_purchase_link",
      "Insert After": "department",
      "Options": "Material Request",
      "Depends On": "eval:doc.material_request_type=='Material Issue'",
      "Allow on Submit": 1,
      "Permission Level": 2
    },
    {
      "DocType": "Material Request",
      "Field Type": "Link",
      "Label": "Department",
      "Fieldname": "department",
      "Insert After": "company",
      "Options": "Department",
      "Is Mandatory Field": 1
    },
    {
      "DocType": "Material Request",
      "Field Type": "Long Text",
      "Label": "Purpose Description",
      "Fieldname": "description",
      "Insert After": "purpose",
      "Field Description": "Write down the description of PURPOSE, if detailing is required."
    },
    {
      "DocType": "Material Request",
      "Field Type": "Data",
      "Label": "Purpose Subject",
      "Fieldname": "purpose",
      "Insert After": "for_a_work_order",
      "Is Mandatory Field": 1,
      "In Standard Filter": 1,
      "Translatable": 1
    },
    {
      "DocType": "Material Request",
      "Field Type": "Check",
      "Label": "For a Work Order",
      "Fieldname": "for_a_work_order",
      "Insert After": "material_request_type",
      "Depends On": "eval:doc.material_request_type == 'Purchase'",
      "In Standard Filter": 1,
      "Bold": 1
    },
    {
      "DocType": "Material Request",
      "Field Type": "Check",
      "Label": "Completed",
      "Fieldname": "completed",
      "Insert After": "naming_series",
      "Read Only Depends On": "eval:doc.completed != user",
      "Allow on Submit": 1
    }
  ],
  "Journal Entry Account": [
    {
      "DocType": "Journal Entry Account",
      "Field Type": "Data",
      "Label": "Online Payment Reference",
      "Fieldname": "online_payment_reference",
      "Insert After": "suspense_jv",
      "Allow on Submit": 1,
      "Translatable": 1
    },
    {
      "DocType": "Journal Entry Account",
      "Field Type": "Link",
      "Label": "Suspense JV",
      "Fieldname": "suspense_jv",
      "Insert After": "receipt_date",
      "Options": "Journal Entry",
      "Allow on Submit": 1
    },
    {
      "DocType": "Journal Entry Account",
      "Field Type": "Date",
      "Label": "Receipt Date",
      "Fieldname": "receipt_date",
      "Insert After": "column_break_34",
      "Depends On": "eval:doc.is_a_donation==true"
    },
    {
      "DocType": "Journal Entry Account",
      "Field Type": "Column Break",
      "Fieldname": "column_break_34",
      "Insert After": "donor_name"
    },
    {
      "DocType": "Journal Entry Account",
      "Field Type": "Data",
      "Label": "Donor Name",
      "Fieldname": "donor_name",
      "Insert After": "dr_no",
      "Depends On": "eval:doc.is_a_donation==true",
      "Translatable": 1
    },
    {
      "DocType": "Journal Entry Account",
      "Field Type": "Data",
      "Label": "DR No",
      "Fieldname": "dr_no",
      "Insert After": "is_folk",
      "Depends On": "eval:doc.is_a_donation==true",
      "In List View": 1,
      "Translatable": 1
    },
    {
      "DocType": "Journal Entry Account",
      "Field Type": "Check",
      "Label": "Is a Donation",
      "Fieldname": "is_a_donation",
      "Insert After": "donation_reference",
      "Allow on Submit": 1,
      "In List View": 1,
      "In Standard Filter": 1
    },
    {
      "DocType": "Journal Entry Account",
      "Field Type": "Section Break",
      "Label": "Donation Reference",
      "Fieldname": "donation_reference",
      "Insert After": "against_account",
      "Bold": 1
    }
  ],
  "Item Group": [
    {
      "DocType": "Item Group",
      "Field Type": "Int",
      "Label": "Live Counter No",
      "Fieldname": "live_counter_no",
      "Insert After": "is_group",
      "Non Negative": 1,
      "In List View": 1,
      "Field Description": "To be used for Restaurant POS Billing"
    },
    {
      "DocType": "Item Group",
      "Field Type": "Data",
      "Label": "Item Code Series",
      "Fieldname": "item_code_series",
      "Insert After": "image",
      "Mandatory Depends On": "eval:!doc.is_group",
      "In List View": 1,
      "Allow in Quick Entry": 1,
      "Translatable": 1
    }
  ],
  "Employee": {
    "DocType": "Employee",
    "Field Type": "Data",
    "Label": "Father Or Spouse Name",
    "Fieldname": "father_or_spouse_name",
    "Insert After": "employee_name",
    "Translatable": 1
  }
}
