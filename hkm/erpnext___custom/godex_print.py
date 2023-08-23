import frappe,requests,json

@frappe.whitelist()
def filter_sellable_items(items,price_list,company):
	items = json.loads(items)
	item_codes = tuple(items)
	join_item = ','.join(["'"+str(item)+"'" for item in items])
	join_item = "({})".format(join_item)

	data = frappe.db.sql("""
			SELECT
				item.`item_code` as code,
				item.`item_name` as name,
				IF(STRCMP(template.name,"")=1,
					ROUND(item_price.`price_list_rate`+(item_price.`price_list_rate`* template.cumulative_tax/100),0), 
					ROUND(item_price.`price_list_rate`,0)
				) as rate
			FROM
				`tabItem` item
			LEFT JOIN `tabItem Price` item_price
				ON item_price.item_code = item.item_code
			LEFT JOIN `tabItem Tax` tax
				ON tax.parent = item.name
			LEFT JOIN `tabItem Tax Template` template
				ON tax.item_tax_template = template.name
			WHERE item.has_variants=0 and item.name IN {} and item_price.price_list = '{}' and (template.name is null or template.company = '{}')
			GROUP BY item.name
			""".format(join_item,price_list,company), as_dict=1)
	return data