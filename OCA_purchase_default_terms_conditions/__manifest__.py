# Copyright 2020 - TODAY, Escodoo
# Copyright (C) 2022 OSI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Default Terms Conditions",
    "summary": "Purchase default terms & conditions",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo, OCA",
    "website": "https://github.com/OCA/purchase-workflow",
    "images": ["static/description/banner.png"],
    "depends": ["purchase"],
    "data": [
        "views/res_config_settings.xml",
        "views/res_partner_views.xml",
        "views/purchase_order_terms_view.xml",
        "reports/purchase_terms_report_action.xml",
    ],
    "qweb": [
        "reports/purchase_terms_report_template.xml",
    ],
    "installable": True,
    "application": False,
}
