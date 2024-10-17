{
    'name': "LiveChat: Soporte de reclamaciones",
    'version': '1.0',
    'depends': ['base','claims_support','im_livechat'],
    'installable': True,
    'author': "JANAQ",
    'category': '',
    'summary': 'Módulo para la integración de LiveChat y el Soporte de reclamaciones',
    'description': """""",
    'data': [
        'views/res_config_settings_views.xml',
        'views/claims_support_views.xml',
        'views/im_livechat_channel_templates.xml',
        'views/mail_channel_views.xml',
        'views/nps_survey_views.xml', 
    ],
}