{
    'name': "Permisos para el chat en vivo",
    'version': '1.0',
    'depends': ['base','im_livechat'],
    'installable': True,
    'author': "JANAQ",
    'category': '',
    'summary': 'Módulo para configurar permisos del chat en vivo',
    'description': """
    Módulo diseñado para proporcionar una diferenciación entre los permisos del chat en vivo
    """,
    'data': [
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/mail_channel_views.xml'
    ],
}