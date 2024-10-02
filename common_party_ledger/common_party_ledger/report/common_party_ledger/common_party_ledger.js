// Copyright (c) 2024, Ameer Muavia Shah and contributors
// For license information, please see license.txt
/* eslint-disable */


frappe.query_reports["Common Party Ledger"] = {
	"filters": [
		{
			"fieldname": "party_link",
			"label": __("Party Link"),
			"fieldtype": "Link",
			"options": "Party Link",
			"reqd": 1,
			"on_change": function () {
				const party_link = frappe.query_report.get_filter_value('party_link');
				if (party_link) {
					// Fetch the primary_party based on the selected party_link
					frappe.db.get_value('Party Link', party_link, 'primary_party', function (value) {
						// Set the fetched primary_party as the default value for the party filter
						frappe.query_report.set_filter_value('party', value.primary_party);
					});
				} else {
					// If no party_link is selected, clear the party filter
					frappe.query_report.set_filter_value('party', '');
				}
			}
		},
		{
			"fieldname": "party",
			"label": __("Party"),
			"fieldtype": "Data",
			"depends_on": "party_link",
			"read_only": 1,
			"reqd": 1
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		}
	]
};
