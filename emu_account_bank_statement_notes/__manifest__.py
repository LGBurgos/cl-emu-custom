{
    'name': 'Notas para Extractos Bancarios',
    'version': '1.0.0',
    'category': 'Accounting',
    'author': 'FranG',
    'summary': 'Gestiona notas predefinidas en extractos bancarios',
    'description': '''
        Módulo que permite:
        - Crear y gestionar tipos de notas predefinidas para extractos bancarios
        - Seleccionar notas desde un catálogo many2one en lugar de ingresarlas como texto libre
        - Gestionar las notas desde Configuración
    ''',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/bank_statement_note_views.xml',
        'views/account_bank_statement_views_inherited.xml',
    ],
    'assets': {
            'web.assets_backend': [
                'emu_account_bank_statement_notes/static/src/xml/bank_rec_record_notebook.xml',
            ],
        },
    'installable': True,
    'application': False,
    'sequence': 1,
    'license': 'LGPL-3',
}
