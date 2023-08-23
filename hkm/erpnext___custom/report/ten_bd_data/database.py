import mysql.connector
import frappe


def get_donor_details(filters):
    mydb = mysql.connector.connect(
        host="3.108.82.37", user="erp", password="sagarsss123", database="dhananjaya"
    )
    mycursor = mydb.cursor()
    company = frappe.get_doc("Company", filters.get("company"))

    query = """
			select 
			donor.DONOR_ID,
			donor.TRUST_ID,
            CONCAT(donor.FIRST_NAME, IFNULL(donor.LAST_NAME,"")) as name,
            donor.LAST_NAME,
			donor.FAX_NUMBER,
			receipt.DR_NUMBER,
			receipt.DR_DATE,
			receipt.DR_AMOUNT,
			receipt.SEVA_CODE,
            CONCAT(donor.RES_ADDR_LINE_1,donor.RES_ADDR_LINE_2,donor.RES_ADDR_LINE_3,donor.RES_ADDR_LINE_4,donor.RES_CITY," ",donor.RES_STATE," ",donor.RES_PINCODE) as res_address,
            CONCAT(donor.OFF_ADDR_LINE_1,donor.OFF_ADDR_LINE_2,donor.OFF_ADDR_LINE_3,donor.OFF_ADDR_LINE_4,donor.OFF_CITY," ",donor.OFF_STATE," ",donor.OFF_PINCODE) as off_address,
            donor.RES_PHONE,
            donor.OFF_PHONE,
            donor.MOBILE_1,
            donor.MOBILE_2,
            donor.PHONE_1,
            donor.PHONE_2,
            donor.EMAIL_1,
            donor.EMAIL_2
			from view_receipt_details receipt
			join view_donor_details donor
			on receipt.DONOR_ID = donor.DONOR_ID
			where donor.TRUST_ID = {}
            AND receipt.DR_DATE BETWEEN '{}' AND '{}'
            AND receipt.PAYMENT_STATUS = 'CL'
			""".format(
        company.dhananjaya_trust_code, filters.get("from_date"), filters.get("to_date")
    )
    mycursor.execute(query)
    myresult = mycursor.fetchall()
    data = {}

    for x in myresult:
        x = list(x)
        x[5] = str(x[5])[4:]
        x[5] = int(x[5])
        data.setdefault(
            x[5],
            {
                "donor_id": x[0],
                "trust_id": x[1],
                "name": x[2],
                "second_name": x[3],
                "pan": x[4],
                "dr_no": x[5],
                "dr_date": x[6],
                "dr_amount": x[7],
                "seva_code": x[8],
                "res_add": x[9],
                "off_add": x[10],
                "res_phone": x[11],
                "off_phone": x[12],
                "mobile1": x[13],
                "mobile2": x[14],
                "phone1": x[15],
                "phone2": x[16],
                "email1": x[17],
                "email2": x[18],
            },
        )
    return data


# def get_bounced_donors():
#     mydb = mysql.connector.connect(
#         host="3.108.82.37", user="erp", password="sagarsss123", database="dhananjaya"
#     )
#     mycursor = mydb.cursor(dictionary=True)
#     # company = frappe.get_doc("Company",filters.get("company"))

#     query = """
#             select 
#             donor.DONOR_ID ,
#             donor.TRUST_ID,
#             CONCAT(donor.FIRST_NAME, IFNULL(donor.LAST_NAME,"")) as name,
#             donor.LAST_NAME,
#             donor.FAX_NUMBER,
#             receipt.DR_NUMBER,
#             receipt.DR_DATE,
#             receipt.DR_AMOUNT,
#             receipt.SEVA_CODE,
#             receipt.PAYMENT_STATUS,
#             CONCAT(donor.RES_ADDR_LINE_1,donor.RES_ADDR_LINE_2,donor.RES_ADDR_LINE_3,donor.RES_ADDR_LINE_4,donor.RES_CITY," ",donor.RES_STATE," ",donor.RES_PINCODE) as res_address,
#             CONCAT(donor.OFF_ADDR_LINE_1,donor.OFF_ADDR_LINE_2,donor.OFF_ADDR_LINE_3,donor.OFF_ADDR_LINE_4,donor.OFF_CITY," ",donor.OFF_STATE," ",donor.OFF_PINCODE) as off_address,
#             donor.RES_PHONE,
#             donor.OFF_PHONE,
#             donor.MOBILE_1,
#             donor.MOBILE_2,
#             donor.PHONE_1,
#             donor.PHONE_2,
#             donor.EMAIL_1,
#             donor.EMAIL_2
#             from view_receipt_details receipt
#             join view_donor_details donor
#             on receipt.DONOR_ID = donor.DONOR_ID
#             # where donor.TRUST_ID
#             AND receipt.DR_DATE BETWEEN '2022-04-01' AND '2023-03-31'
#             # AND receipt.PAYMENT_STATUS = 'CL'
#             """
#     mycursor.execute(query)
#     myresult = mycursor.fetchall()
#     for r in myresult:
#         doc_dict = {
#             "doctype": "Temp Data",
#             "donor_id": r["DONOR_ID"],
#             "trust_id": r["TRUST_ID"],
#             "name1": r["name"],
#             "dr_number": r["DR_NUMBER"],
#             "dr_date": r["DR_DATE"],
#             "dr_amount": r["DR_AMOUNT"],
#             "seva_code": r["SEVA_CODE"],
#             "payment_status": r["PAYMENT_STATUS"],
#             "res_address": r["res_address"],
#             "off_address": r["off_address"],
#             "res_phone": r["RES_PHONE"],
#             "mobile_1": r["MOBILE_1"],
#             "phone_1": r["PHONE_1"],
#         }
#         doc = frappe.get_doc(doc_dict)
#         doc.insert()
#     frappe.db.commit()
