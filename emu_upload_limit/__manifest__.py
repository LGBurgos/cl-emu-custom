{
    'name': 'EMU Upload Size Limit',
    'version': '18.0.1.1.0',
    'category': 'Custom',
    'summary': 'Restrict chatter file uploads to max 1.5 MB with custom message',
    'depends': ['mail'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'emu_upload_limit/static/src/js/upload_limit.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}