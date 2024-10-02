# Copyright (c) 2024, Ameer Muavia Shah and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate


def execute(filters=None):
    validate_filters(filters)
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def validate_filters(filters):
    if not filters.get("party_link"):
        frappe.throw(_("Please select Party Link to proceed"))


def get_columns():
    return [
        {
            "fieldname": "posting_date",
            "label": _("Posting Date"),
            "fieldtype": "Date",
            "width": 130,
        },
        {
            "fieldname": "account",
            "label": _("Account"),
            "fieldtype": "Link",
            "options": "Account",
            "width": 120,
        },
        {
            "fieldname": "party_type",
            "label": _("Party Type"),
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "fieldname": "party",
            "label": _("Party"),
            "fieldtype": "Dynamic Link",
            "options": "Party Type",
            "width": 200,
        },
        {
            "fieldname": "voucher_type",
            "label": _("Voucher Type"),
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "fieldname": "voucher_no",
            "label": _("Voucher No"),
            "fieldtype": "Dynamic Link",
            "options": "Voucher Type",
            "width": 200,
        },
        {
            "fieldname": "debit",
            "label": _("Debit"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "credit",
            "label": _("Credit"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "balance",
            "label": _("Balance"),
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "fieldname": "remarks",
            "label": _("Remarks"),
            "fieldtype": "Data",
            "width": 150,
        },
    ]


def get_data(filters):
    party_link_name = filters.get("party_link")
    primary_party, secondary_party, primary_role, secondary_role = frappe.db.get_value(
        "Party Link",
        party_link_name,
        ["primary_party", "secondary_party", "primary_role", "secondary_role"],
    )

    data = []
    balance = 0
    balance += get_opening_balance(primary_party, primary_role, filters)
    balance += get_opening_balance(secondary_party, secondary_role, filters)

    # Add opening balance row
    data.append(
        {
            "posting_date": "",
            "account": "",
            "party_type": "",
            "party": "Opening Balance",
            "voucher_type": "",
            "voucher_no": "",
            "debit": 0,
            "credit": 0,
            "balance": balance,
        }
    )

    transactions = get_party_transactions(primary_party, primary_role, filters)
    data.extend(transactions)

    transactions = get_party_transactions(secondary_party, secondary_role, filters)
    data.extend(transactions)

    # Sort by date
    data.sort(
        key=lambda x: x["posting_date"] or getdate("1900-01-01")
    )  # None dates to min date

    # Calculate running balance
    for row in data:
        if row.get("posting_date"):  # skip opening balance row
            balance += row.get("debit", 0) - row.get("credit", 0)
            row["balance"] = balance

    # Add ending balance row
    data.append(
        {
            "posting_date": "",
            "account": "",
            "party_type": "",
            "party": "Ending Balance",
            "voucher_type": "",
            "voucher_no": "",
            "debit": 0,
            "credit": 0,
            "balance": balance,
        }
    )

    return data


def get_opening_balance(party, role, filters):
    if party:
        balance = frappe.db.sql(
            """
            SELECT IFNULL(SUM(debit) - SUM(credit), 0)
            FROM `tabGL Entry`
            WHERE party_type = %s AND party=%s AND posting_date < %s
            """,
            (role, party, filters.get("from_date")),
        )[0][0]
        return balance


def get_party_transactions(party, party_type, filters):
    transactions = frappe.db.sql(
        """
        SELECT
            posting_date, account, %s as party_type, party, voucher_type,
            voucher_no, debit, credit, remarks
        FROM
            `tabGL Entry`
        WHERE
            party_type = %s AND party=%s AND is_cancelled = 0 AND posting_date BETWEEN %s AND %s
        ORDER BY
            posting_date, account
        """,
        (
            party_type,
            party_type,
            party,
            filters.get("from_date"),
            filters.get("to_date"),
        ),
        as_dict=1,
    )

    return [dict(t) for t in transactions]
