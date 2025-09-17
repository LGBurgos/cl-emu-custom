{
    "name": "Hito EMU Purchase Labels",
    "version": "18.0",
    "depends": ['purchase','project_purchase','purchase_request'],
    "category": "",
    "summary": "etiquetas en compras y requisicion de compras",
    "data": [
        'security/ir.model.access.csv',
        'views/purchase_order.xml',
        'views/purchase_request.xml',
        'views/purchase_label.xml',
        'views/requisition_purchase_label.xml',
    ],
    "installable": True,
    "application": False,
}