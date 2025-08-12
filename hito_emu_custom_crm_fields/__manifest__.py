{
    "name": "Hito EMU Custom CRM Fields",
    "version": "18.0",
    "depends": ['crm','sale'],
    "category": "",
    "summary": "Add custom fields to CRM",
    "data": [
        'data/sequence.xml',
        'data/copiar_datos.xml',
        'views/crm_lead.xml',
        'views/sale_order.xml',
    ],
    'post_init_hook': 'post_init_hook',
    "installable": True,
    "application": False,
}