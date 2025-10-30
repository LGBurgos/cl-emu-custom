{
    'name': 'Notas para Extractos Bancarios',
    'version': '1.0.0',
    'category': 'Accounting',
    'author': 'FranG',
    'summary': 'Gestiona notas predefinidas en operaciones manuales de extractos bancarios',
    'description': '''
        Módulo que permite:
        - Crear y gestionar tipos de notas predefinidas para extractos bancarios
        - Seleccionar notas desde un catálogo en lugar de ingresarlas como texto libre
        - Configurar nota predeterminada por banco
        - Cambio de campo de texto a many2one para notas
        - Integración completa con flujo de contabilidad de Odoo
    ''',
    'depends': ['account'],
    'data': [
        'views/bank_statement_note_views.xml',
        'views/account_bank_statement_views_inherited.xml',
        'views/res_bank_views_inherited.xml',
    ],
    'installable': True,
    'application': False,
    'sequence': 1,
    'license': 'LGPL-3',
}
